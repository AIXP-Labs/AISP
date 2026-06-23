#!/usr/bin/env python3
"""Static + control-flow simulation regression for AISP skill packages.

Usage:
    python simulate_aisp_flow.py [<path-to-skill-folder>]   (default '.')

Reads <skill>/aisp.aisop.json and runs static checks for any AISP skill. When
the graph is aisp_creator_evolution_aisp's known create/evolve graph, it also
runs the creator-specific 6 normal + 6 anomaly scenarios. Other AISP skills use
a generic graph walk over aisop.main instead of crashing on creator-only nodes.

  (A) STATIC CHECKS
      1. every aisop.* graph node next/branches/error edge resolves to an
         existing node key in the SAME graph.
      2. every graph node has a functions{} entry EXCEPT the allowed
         terminals end_node / research_end (which may be function-less).
      3. every non_negotiable.enforced_by resolves to a real mechanism:
         'aisop.main'            -> the named graph exists
         '<node>.<step>:sys.*'   -> functions[node][step] contains the sys.* token
         'tools'                 -> system.content.tools is present and non-empty
      4. (ProtocolAlign advisory) every functions.<node>.on_error value
         resolves to an existing node in the graph that owns that node
         (main on_error -> main node; research on_error -> research node).
      5. README.md is still the deterministic projection of aisp.aisop.json
         according to the bundled aisp_readme.py --check.
      6. SKILL.md is still the deterministic sidecar projection of
         aisp.aisop.json according to the bundled aisp_skill_md.py --check.
      7. no hidden Python/evolution cache residue is present in the shipped
         package tree.

  (B) PATH SIMULATION
      Generic mode: every non-error aisop.main branch path must terminate.

      Creator mode: 6 normal paths MUST be reachable / valid.
      The graph (decision gates) is derived from the parsed jsonflow; the
      gate labels and the 6 expected paths are encoded as test scenarios and
      replayed against the parsed graph so a future edit that breaks a branch
      label or an edge is caught here.

  (C) CREATOR ANOMALY PATHS (6 MUST be detected as rejected)
      In creator mode only, bad intent / bad research status / validation fail
      / bad review label / bad revision_gate label / retry bound overflow must
      be classified as REJECTED.

Read-only: never writes any file. Stdlib only. No network.
Exit code 0 = all pass, 1 = any failure. Emits a JSON report on stdout.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ---- allowed terminals (graph nodes that may be function-less) --------------
ALLOWED_TERMINALS = ("end_node", "research_end")
CACHE_DIR_NAMES = ("__pycache__", ".evolution_snapshot", ".version_history")
CACHE_FILE_SUFFIXES = (".pyc", ".pyo")

# ---- decision-gate label vocabularies (the control-flow contract) -----------
INTENT_LABELS = ("create", "evolve")
RESEARCH_STATUS = ("complete", "incomplete")
REVIEW_LABELS = ("approved", "needs_revision", "rejected")
REVISION_LABELS = ("retry", "stop")
RETRY_LIMIT = 2  # revision_gate bound: research_attempts < 2


# ============================================================================
# Loading
# ============================================================================
def load_skill(skill_root: Path):
    """Return (system_content, user_content) from <root>/aisp.aisop.json."""
    skill_file = skill_root / "aisp.aisop.json"
    doc = json.loads(skill_file.read_text(encoding="utf-8-sig"))
    if not isinstance(doc, list) or len(doc) != 2:
        raise ValueError(f"{skill_file} must be a two-message AISP JSON array")
    system = doc[0].get("content", {}) if isinstance(doc[0], dict) else {}
    user = doc[1].get("content", {}) if isinstance(doc[1], dict) else {}
    if not isinstance(system, dict) or not isinstance(user, dict):
        raise ValueError("system/user content must be objects")
    return system, user


def _edges(spec):
    """Outgoing control-flow targets of a jsonflow node spec: next+branches+error."""
    out = []
    if not isinstance(spec, dict):
        return out
    nxt = spec.get("next")
    if isinstance(nxt, list):
        out += [(t, "next") for t in nxt if isinstance(t, str)]
    elif isinstance(nxt, str):
        out.append((nxt, "next"))
    branches = spec.get("branches")
    if isinstance(branches, dict):
        out += [(t, f"branches[{k}]") for k, t in branches.items() if isinstance(t, str)]
    err = spec.get("error")
    if isinstance(err, str):
        out.append((err, "error"))
    return out


def _graph_dicts(user):
    """Return every object-valued graph under user.content.aisop."""
    aisop = user.get("aisop", {}) if isinstance(user, dict) else {}
    if not isinstance(aisop, dict):
        return {}
    return {name: graph for name, graph in aisop.items() if isinstance(name, str) and isinstance(graph, dict)}


# ============================================================================
# (A) Static checks
# ============================================================================
def check_static(system, user, report):
    failures = report["failures"]
    graphs = _graph_dicts(user)
    functions = user.get("functions", {}) if isinstance(user.get("functions"), dict) else {}

    if "main" not in graphs:
        failures.append("STATIC: aisop.main graph missing or not an object")
        return
    if not graphs:
        failures.append("STATIC: no object-valued aisop graphs found")
        return

    # A.1 edge resolution within the same graph
    edge_count = 0
    for gname, graph in graphs.items():
        node_keys = set(graph.keys())
        for node, spec in graph.items():
            for target, kind in _edges(spec):
                edge_count += 1
                if target not in node_keys:
                    failures.append(
                        f"STATIC.edge: {gname}.{node}.{kind} -> '{target}' "
                        f"does not resolve to a node in aisop.{gname}"
                    )
    report["static"]["edges_checked"] = edge_count

    # A.2 every graph node has a function, except allowed terminals
    missing_fn = []
    for gname, graph in graphs.items():
        for node in graph:
            if node in ALLOWED_TERMINALS:
                continue
            if node not in functions:
                missing_fn.append(f"{gname}.{node}")
    if missing_fn:
        failures.append(f"STATIC.functions: graph nodes without a functions entry: {missing_fn}")
    # phantom: every function should map to a graph node (advisory, also enforced)
    all_nodes = {node for graph in graphs.values() for node in graph}
    phantom = [fn for fn in functions if fn not in all_nodes]
    if phantom:
        failures.append(f"STATIC.functions: functions without a graph node (phantom): {phantom}")

    # A.3 non_negotiable.enforced_by resolution
    contract = user.get("aisp_contract", {}) if isinstance(user.get("aisp_contract"), dict) else {}
    nn = contract.get("non_negotiable", [])
    tools = system.get("tools", [])
    nn_checked = 0
    for item in nn if isinstance(nn, list) else []:
        if not isinstance(item, dict):
            continue
        enf = item.get("enforced_by")
        if not isinstance(enf, str) or not enf:
            failures.append(f"STATIC.enforced_by: non_negotiable item has no enforced_by: {item!r}")
            continue
        nn_checked += 1
        if not _resolve_enforced_by(enf, graphs, functions, tools):
            failures.append(
                f"STATIC.enforced_by: '{enf}' does not resolve to a real mechanism "
                f"(graph / <node>.<step>:sys.* / tools)"
            )
    report["static"]["non_negotiable_checked"] = nn_checked

    # A.4 on_error target resolution (ProtocolAlign advisory)
    on_error_checked = 0
    for node, fn in functions.items():
        if not isinstance(fn, dict):
            continue
        oe = fn.get("on_error")
        if oe is None:
            continue
        if not isinstance(oe, dict):
            failures.append(f"STATIC.on_error: functions.{node}.on_error must be an object")
            continue
        owners = [(gname, graph) for gname, graph in graphs.items() if node in graph]
        if not owners:
            failures.append(f"STATIC.on_error: functions.{node}.on_error on a non-graph node")
            continue
        owner_name, owner = owners[0]
        for etype, target in oe.items():
            on_error_checked += 1
            if not isinstance(target, str) or target not in owner:
                failures.append(
                    f"STATIC.on_error: functions.{node}.on_error['{etype}'] -> '{target}' "
                    f"does not resolve to a node in aisop.{owner_name}"
                )
    report["static"]["on_error_targets_checked"] = on_error_checked


def check_readme_projection(skill_root, report):
    """Run the bundled README projection check in read-only mode."""
    failures = report["failures"]
    script_candidates = [
        skill_root / "aisp_reference_tools" / "aisp_readme.py",
        Path(__file__).resolve().parents[1] / "aisp_reference_tools" / "aisp_readme.py",
    ]
    script = next((candidate for candidate in script_candidates if candidate.is_file()), script_candidates[0])
    readme = skill_root / "README.md"
    report["static"]["readme_projection_checked"] = False
    if not readme.is_file():
        failures.append("STATIC.readme: README.md is missing")
        return
    if not script.is_file():
        failures.append("STATIC.readme: aisp_readme.py is missing from skill root and simulator root")
        return
    report["static"]["readme_projection_tool"] = str(script).replace("\\", "/")
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(script), str(skill_root), "--check"],
            cwd=str(script.parent.parent),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        failures.append(f"STATIC.readme: README projection check could not run: {exc}")
        return
    report["static"]["readme_projection_checked"] = True
    report["static"]["readme_projection_exit_code"] = proc.returncode
    if proc.returncode != 0:
        detail = (proc.stdout + proc.stderr).strip().replace("\n", " | ")
        failures.append(f"STATIC.readme: README.md drift detected ({detail})")


def check_skill_md_projection(skill_root, report):
    """Run the bundled SKILL.md projection check in read-only mode."""
    failures = report["failures"]
    script_candidates = [
        skill_root / "aisp_reference_tools" / "aisp_skill_md.py",
        Path(__file__).resolve().parents[1] / "aisp_reference_tools" / "aisp_skill_md.py",
    ]
    script = next((candidate for candidate in script_candidates if candidate.is_file()), script_candidates[0])
    sidecar = skill_root / "SKILL.md"
    report["static"]["skill_md_projection_checked"] = False
    if not sidecar.is_file():
        failures.append("STATIC.skill_md: SKILL.md is missing")
        return
    if not script.is_file():
        failures.append("STATIC.skill_md: aisp_skill_md.py is missing from skill root and simulator root")
        return
    report["static"]["skill_md_projection_tool"] = str(script).replace("\\", "/")
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(script), str(skill_root), "--check"],
            cwd=str(script.parent.parent),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        failures.append(f"STATIC.skill_md: SKILL.md projection check could not run: {exc}")
        return
    report["static"]["skill_md_projection_checked"] = True
    report["static"]["skill_md_projection_exit_code"] = proc.returncode
    if proc.returncode != 0:
        detail = (proc.stdout + proc.stderr).strip().replace("\n", " | ")
        failures.append(f"STATIC.skill_md: SKILL.md drift detected ({detail})")


def check_no_cache_residue(skill_root, report):
    """Reject Python bytecode and local evolution/cache residue in the package."""
    bad_dirs = []
    bad_files = []
    for path in skill_root.rglob("*"):
        try:
            rel = path.relative_to(skill_root).as_posix()
        except ValueError:
            continue
        if path.is_dir() and path.name in CACHE_DIR_NAMES:
            bad_dirs.append(rel)
        elif path.is_file() and path.suffix in CACHE_FILE_SUFFIXES:
            bad_files.append(rel)
    report["static"]["cache_residue_dirs"] = len(bad_dirs)
    report["static"]["cache_residue_files"] = len(bad_files)
    if bad_dirs or bad_files:
        report["failures"].append(
            "STATIC.cache: hidden cache/build residue present: "
            f"dirs={bad_dirs}, files={bad_files}"
        )


def _resolve_enforced_by(enf, graphs, functions, tools):
    """True if an enforced_by token resolves to a real mechanism."""
    # form 1: a graph name (e.g. 'aisop.main')
    if enf.startswith("aisop."):
        return enf.split(".", 1)[1] in graphs
    if enf in graphs:
        return True
    # form 2: 'tools'
    if enf == "tools":
        return isinstance(tools, list) and len(tools) > 0
    # form 3: '<node>.<step>:sys.*'
    if ":" in enf and "." in enf.split(":", 1)[0]:
        locator, mechanism = enf.split(":", 1)
        node, step = locator.split(".", 1)
        fn = functions.get(node)
        if not isinstance(fn, dict):
            return False
        step_text = fn.get(step)
        if not isinstance(step_text, str):
            return False
        # mechanism must be a sys.* token and must literally appear in the step text
        if not mechanism.startswith("sys."):
            return False
        return mechanism in step_text
    return False


# ============================================================================
# (B)/(C) Control-flow simulation
# ============================================================================
class FlowRejected(Exception):
    """Raised when the simulated flow rejects a scenario (anomaly correctly caught)."""


def simulate(scenario, graphs):
    """Replay one scenario against the parsed graph.

    The scenario supplies the runtime decisions the gates would make:
      intent, research_status (sequence), review, revision (sequence).
    Returns the terminal node label (e.g. 'deliver' / 'preserve').
    Raises FlowRejected if a gate label is invalid (anomaly path).
    """
    main = graphs["main"]
    intent = scenario.get("intent")
    if intent not in INTENT_LABELS:
        raise FlowRejected(f"bad intent label: {intent!r}")

    # walk classify_intent branch
    node = main["classify_intent"]["branches"][intent]  # capture_request | capture_target
    path = ["classify_intent", node]

    research_status_seq = list(scenario.get("research_status", []))
    revision_seq = list(scenario.get("revision", []))
    research_attempts = 0

    # linear approach to run_research (create: capture_request->define_goal; evolve: capture_target->gather_evidence)
    if intent == "create":
        path += ["define_goal", "run_research"]
    else:
        path += ["gather_evidence", "run_research"]

    # run_research / revision_gate loop
    guard = 0
    while True:
        guard += 1
        if guard > 20:
            raise FlowRejected("flow did not terminate (possible unbounded loop)")
        if not research_status_seq:
            raise FlowRejected("scenario exhausted research_status before resolving run_research")
        status = research_status_seq.pop(0)
        if status not in RESEARCH_STATUS:
            raise FlowRejected(f"bad research status: {status!r}")
        if status == "complete":
            # run_research --complete--> assert_research_complete
            path.append("assert_research_complete")
            break
        # incomplete --> revision_gate (bounded retry)
        path.append("revision_gate")
        if not revision_seq:
            raise FlowRejected("scenario exhausted revision decisions at revision_gate")
        rev = revision_seq.pop(0)
        if rev not in REVISION_LABELS:
            raise FlowRejected(f"bad revision_gate label: {rev!r}")
        if rev == "retry":
            research_attempts += 1
            if research_attempts >= RETRY_LIMIT:
                raise FlowRejected(
                    f"retry bound exceeded: research_attempts={research_attempts}, "
                    f"limit requires research_attempts < {RETRY_LIMIT}"
                )
            path.append("run_research")
            continue
        # stop --> preserve
        path += ["preserve", "end_node"]
        return "preserve", path

    # assert_research_complete --create--> design_skill ; --evolve--> design_evolution
    if intent == "create":
        path += ["design_skill", "generate_candidate"]
    else:
        path += ["design_evolution", "generate_candidate"]
    path += ["validate_candidate"]

    # validate_candidate.step5 sys.assert gate
    if not scenario.get("validation_pass", True):
        raise FlowRejected("validation failed (validate_candidate.step5 sys.assert)")

    path.append("review_candidate")
    review = scenario.get("review")
    if review not in REVIEW_LABELS:
        raise FlowRejected(f"bad review label: {review!r}")

    if review == "approved":
        path += ["deliver", "end_node"]
        return "deliver", path
    if review == "rejected":
        path += ["preserve", "end_node"]
        return "preserve", path
    # needs_revision --> revision_gate --> (retry: run_research again)
    path.append("revision_gate")
    if not revision_seq:
        raise FlowRejected("scenario exhausted revision decisions after needs_revision")
    rev = revision_seq.pop(0)
    if rev not in REVISION_LABELS:
        raise FlowRejected(f"bad revision_gate label: {rev!r}")
    if rev == "stop":
        path += ["preserve", "end_node"]
        return "preserve", path
    # retry -> run_research -> (assume completion) -> review again
    path.append("run_research")
    if not research_status_seq:
        raise FlowRejected("scenario exhausted research_status after needs_revision retry")
    status = research_status_seq.pop(0)
    if status != "complete":
        raise FlowRejected(f"expected complete after needs_revision retry, got {status!r}")
    path.append("assert_research_complete")
    if intent == "create":
        path += ["design_skill", "generate_candidate"]
    else:
        path += ["design_evolution", "generate_candidate"]
    path += ["validate_candidate"]
    if not scenario.get("validation_pass2", True):
        raise FlowRejected("validation failed on retry")
    path.append("review_candidate")
    review2 = scenario.get("review2")
    if review2 not in REVIEW_LABELS:
        raise FlowRejected(f"bad review label (retry): {review2!r}")
    if review2 == "approved":
        path += ["deliver", "end_node"]
        return "deliver", path
    if review2 == "rejected":
        path += ["preserve", "end_node"]
        return "preserve", path
    raise FlowRejected("needs_revision loop exceeded modeled depth")


def _verify_path_edges(path, graphs):
    """Confirm every consecutive pair in a simulated path is a real edge or
    a known terminal landing. Returns a list of broken hops (empty = ok)."""
    main = graphs["main"]
    broken = []
    for a, b in zip(path, path[1:]):
        spec = main.get(a, {})
        targets = {t for t, _ in _edges(spec)}
        if b not in targets:
            broken.append(f"{a} -> {b}")
    return broken


def _is_creator_graph(graphs):
    main = graphs.get("main", {})
    required = {
        "classify_intent",
        "run_research",
        "assert_research_complete",
        "validate_candidate",
        "review_candidate",
        "revision_gate",
    }
    return required.issubset(set(main)) and "research" in graphs


def _normal_targets(spec):
    return [(target, kind) for target, kind in _edges(spec) if kind != "error"]


def run_generic_graph_walk(graphs, report):
    """Explore non-error aisop.main paths for ordinary AISP skills.

    This is intentionally weaker than creator mode: it proves graph shape and
    branch termination, not semantic correctness of model-generated content.
    """
    failures = report["failures"]
    main = graphs.get("main", {})
    if not main:
        failures.append("SIMULATE: aisop.main missing — cannot run generic graph walk")
        return

    start = next(iter(main))
    max_depth = max(len(main) + 5, 10)
    max_paths = 100
    completed = []

    def walk(node, path):
        if len(completed) >= max_paths:
            failures.append(f"GENERIC: path exploration exceeded {max_paths} paths")
            return
        if node not in main:
            failures.append(f"GENERIC: path reached missing node {node!r}")
            return
        if len(path) > max_depth:
            failures.append(f"GENERIC: path exceeded max depth {max_depth}: {' -> '.join(path)}")
            return
        targets = _normal_targets(main[node])
        if not targets:
            completed.append(list(path))
            return
        for target, kind in targets:
            if target in path:
                failures.append(f"GENERIC: cycle detected via {kind}: {' -> '.join(path + [target])}")
                continue
            walk(target, path + [target])

    walk(start, [start])
    for index, path in enumerate(completed, start=1):
        report["normal_paths"].append(
            {
                "name": f"generic path {index}",
                "ok": True,
                "terminal": path[-1],
                "path": path,
            }
        )
    report["static"]["generic_paths_checked"] = len(completed)
    if not completed:
        failures.append("GENERIC: no terminating aisop.main path found")


def run_simulations(graphs, report):
    failures = report["failures"]
    report["simulation_mode"] = "creator_regression"

    # (B) normal paths — MUST reach the expected terminal
    normal = [
        ("create complete approved->deliver",
         {"intent": "create", "research_status": ["complete"], "review": "approved"}, "deliver"),
        ("evolve complete approved->deliver",
         {"intent": "evolve", "research_status": ["complete"], "review": "approved"}, "deliver"),
        ("incomplete->retry->complete->deliver",
         {"intent": "create", "research_status": ["incomplete", "complete"],
          "revision": ["retry"], "review": "approved"}, "deliver"),
        ("incomplete->retry-limit->preserve",
         {"intent": "create", "research_status": ["incomplete", "incomplete"],
          "revision": ["retry", "stop"]}, "preserve"),
        ("rejected->preserve",
         {"intent": "create", "research_status": ["complete"], "review": "rejected"}, "preserve"),
        ("needs_revision->retry->approved->deliver",
         {"intent": "evolve", "research_status": ["complete", "complete"],
          "revision": ["retry"], "review": "needs_revision", "review2": "approved"}, "deliver"),
    ]
    for name, scenario, expected in normal:
        try:
            terminal, path = simulate(scenario, graphs)
        except FlowRejected as exc:
            failures.append(f"NORMAL[{name}]: unexpectedly REJECTED: {exc}")
            report["normal_paths"].append({"name": name, "ok": False, "reason": str(exc)})
            continue
        broken = _verify_path_edges(path, graphs)
        if terminal != expected:
            failures.append(f"NORMAL[{name}]: reached '{terminal}', expected '{expected}'")
            report["normal_paths"].append({"name": name, "ok": False, "terminal": terminal})
        elif broken:
            failures.append(f"NORMAL[{name}]: path has broken edges: {broken}")
            report["normal_paths"].append({"name": name, "ok": False, "broken_edges": broken})
        else:
            report["normal_paths"].append({"name": name, "ok": True, "terminal": terminal})

    # (C) anomaly paths — MUST be REJECTED
    anomalies = [
        ("bad intent",
         {"intent": "fix", "research_status": ["complete"], "review": "approved"}),
        ("bad research status",
         {"intent": "create", "research_status": ["maybe"], "review": "approved"}),
        ("validation fail",
         {"intent": "create", "research_status": ["complete"], "validation_pass": False,
          "review": "approved"}),
        ("bad review label",
         {"intent": "create", "research_status": ["complete"], "review": "looks_fine"}),
        ("bad revision_gate label",
         {"intent": "create", "research_status": ["incomplete"], "revision": ["loop"]}),
        ("retry bound overflow",
         {"intent": "create", "research_status": ["incomplete", "incomplete"],
          "revision": ["retry", "retry"]}),
    ]
    for name, scenario in anomalies:
        try:
            terminal, _ = simulate(scenario, graphs)
        except FlowRejected as exc:
            report["anomaly_paths"].append({"name": name, "rejected": True, "reason": str(exc)})
            continue
        # not rejected -> the anomaly leaked through; that is a FAILURE
        failures.append(f"ANOMALY[{name}]: NOT rejected (reached '{terminal}') — simulator gap")
        report["anomaly_paths"].append({"name": name, "rejected": False, "terminal": terminal})


# ============================================================================
# main
# ============================================================================
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Static + control-flow simulation regression for the AISP skill."
    )
    parser.add_argument("skill_root", nargs="?", default=".",
                        help="Skill root directory containing aisp.aisop.json (default '.').")
    args = parser.parse_args(argv)

    skill_root = Path(args.skill_root).resolve()
    report = {
        "skill_root": str(skill_root),
        "static": {},
        "normal_paths": [],
        "anomaly_paths": [],
        "failures": [],
        "pass": False,
    }

    try:
        system, user = load_skill(skill_root)
    except Exception as exc:  # noqa: BLE001
        report["failures"].append(f"LOAD: {exc}")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    check_static(system, user, report)
    check_readme_projection(skill_root, report)
    check_skill_md_projection(skill_root, report)
    check_no_cache_residue(skill_root, report)

    graphs = _graph_dicts(user)
    if graphs.get("main") and _is_creator_graph(graphs):
        run_simulations(graphs, report)
    elif graphs.get("main"):
        report["simulation_mode"] = "generic_graph_walk"
        run_generic_graph_walk(graphs, report)
    else:
        report["failures"].append("SIMULATE: aisop.main missing — cannot run path simulation")

    report["pass"] = not report["failures"]
    report["summary"] = {
        "static_failures": sum(1 for f in report["failures"] if f.startswith("STATIC")),
        "normal_ok": sum(1 for p in report["normal_paths"] if p.get("ok")),
        "normal_total": len(report["normal_paths"]),
        "anomaly_rejected": sum(1 for p in report["anomaly_paths"] if p.get("rejected")),
        "anomaly_total": len(report["anomaly_paths"]),
        "total_failures": len(report["failures"]),
        "simulation_mode": report.get("simulation_mode"),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
