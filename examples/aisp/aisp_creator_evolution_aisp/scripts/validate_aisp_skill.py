#!/usr/bin/env python3
"""Validate an AISP skill folder against M1-M6 (zero-dependency, stdlib only).

Usage:
    python validate_aisp_skill.py <path-to-skill-folder>

Exit code 0 + JSON report on stdout. m1_to_m6_pass / safety_pass drive the
caller's sys.assert gate. This is a checker, not a fixer: it never writes.

This is a self-contained subset of the canonical reference validator
(AISP-Protocol tools/aisp_validate.py); it uses the same AISP_E_* / AISP_W_*
codes so results read consistently. It covers M1-M6 + jsonflow graph integrity
+ loading_mode is fixed to "node" for AISP progressive disclosure, and a
  STATIC execute_mode declaration check (declarations only — it does NOT verify
  the runtime R7 dispatch property, which is observable only at execution time).
Mermaid graphs are not structurally parsed; SE/EC cross-checks live in the
canonical validator.
"""
import json
import os
import re
import sys

TRUST_WORDS = ("trusted", "verified", "safe")
REQUIRED_LOADING_MODE = "node"
VALID_EXECUTE_MODES = ("agent", "inline")
AGENT_STEP_RECOMMENDATION_THRESHOLD = 10
STEP_KEY_RE = re.compile(r"^step[1-9]\d*$")


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError("non-JSON numeric constant: %s" % value)


def _err(issues, code, msg):
    issues.append({"code": code, "msg": msg})


def _confined_path(base, relative):
    root = os.path.realpath(base)
    resolved = os.path.realpath(os.path.join(root, relative.replace("\\", os.sep)))
    if os.path.commonpath((root, resolved)) != root:
        raise ValueError("path resolves outside its scope")
    return resolved


def _step_count(fn):
    if not isinstance(fn, dict):
        return 0
    return sum(1 for key, value in fn.items() if isinstance(key, str) and STEP_KEY_RE.fullmatch(key) and isinstance(value, str))


def _numeric_step_items(fn):
    if not isinstance(fn, dict):
        return []
    return [(key, value) for key, value in fn.items() if isinstance(key, str) and STEP_KEY_RE.fullmatch(key)]


def _edges(spec):
    """All outgoing control-flow targets of a jsonflow node: next + branches + error.
    Tolerant of malformed shapes — never raises."""
    if not isinstance(spec, dict):
        return []
    out = []
    nxt = spec.get("next")
    if isinstance(nxt, list):
        out += [t for t in nxt if isinstance(t, str)]
    elif isinstance(nxt, str):
        out.append(nxt)
    br = spec.get("branches")
    if isinstance(br, dict):
        out += [t for t in br.values() if isinstance(t, str)]
    err = spec.get("error")
    if isinstance(err, str):
        out.append(err)
    return out


def _check_graphs(aisop, functions, issues):
    """M1: every jsonflow aisop graph must be a legal flow — edges resolve, a
    terminal exists and is reachable, no orphan nodes, every node has a function.
    Graphs given as a string (mermaid flow_format) are not structurally parsed here."""
    if not isinstance(aisop, dict):
        return
    for gname, nodes in aisop.items():
        if not isinstance(nodes, dict):
            if not isinstance(nodes, str):
                _err(issues, "AISP_E_M1_GRAPH", "graph %r must be an object or Mermaid string" % gname)
            continue  # Mermaid graphs are outside this lightweight parser.
        if not nodes:
            _err(issues, "AISP_E_M1_GRAPH", "graph %r is empty" % gname)
            continue
        names = list(nodes.keys())
        nameset = set(names)
        terminals = set()
        for n, spec in nodes.items():
            if not isinstance(spec, dict):
                _err(issues, "AISP_E_M1_GRAPH", "graph node %s.%s must be an object" % (gname, n))
                continue
            malformed = (
                "next" in spec and (not isinstance(spec["next"], list) or any(not isinstance(t, str) for t in spec["next"]))
            ) or (
                "branches" in spec and (not isinstance(spec["branches"], dict) or any(not isinstance(t, str) for t in spec["branches"].values()))
            ) or ("error" in spec and not isinstance(spec["error"], str))
            if malformed:
                _err(issues, "AISP_E_M1_EDGE_SHAPE", "graph node %s.%s has malformed edge fields" % (gname, n))
            for t in _edges(spec):
                if t not in nameset:
                    _err(issues, "AISP_E_M1_EDGE", "%s.%s -> %r: no such node" % (gname, n, t))
            if not spec.get("next") and not spec.get("branches"):
                terminals.add(n)
            if n not in functions:
                _err(issues, "AISP_E_M1_NODE_FUNCTION", "node %s.%s has no function" % (gname, n))
        if not terminals:
            _err(issues, "AISP_E_M1_TERMINAL", "graph %r has no terminal node" % gname)
        seen = set()
        stack = [names[0]]
        while stack:
            x = stack.pop()
            if x in seen or x not in nodes:
                continue
            seen.add(x)
            stack += _edges(nodes[x])
        unreachable = nameset - seen
        if unreachable:
            _err(issues, "AISP_E_M1_UNREACHABLE", "graph %r unreachable nodes: %s" % (gname, sorted(unreachable)))
        if terminals and not (terminals & seen):
            _err(issues, "AISP_E_M1_TERMINAL_UNREACHABLE", "graph %r: no terminal reachable from entry" % gname)


def validate(folder):
    issues = []
    folder = os.path.abspath(folder)
    name = os.path.basename(folder.rstrip(os.sep))
    skill_file = os.path.join(folder, "aisp.aisop.json")

    # M2 (folder / file naming)
    if not name.endswith("_aisp"):
        _err(issues, "AISP_E_M2_SUFFIX", "folder name does not end with _aisp")
    if not os.path.isfile(skill_file):
        _err(issues, "AISP_E_M2_FILENAME", "aisp.aisop.json not found")
        return _report(issues)

    try:
        _confined_path(folder, "aisp.aisop.json")
    except (OSError, ValueError, RuntimeError) as e:
        _err(issues, "AISP_E_SE1_PATH", "skill entry is not confined: %s" % e)
        return _report(issues)

    try:
        with open(skill_file, encoding="utf-8-sig") as stream:
            doc = json.load(stream, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except Exception as e:  # noqa: BLE001
        _err(issues, "AISP_E_M1_JSON", "aisp.aisop.json is not valid JSON: %s" % e)
        return _report(issues)

    # M1 (legal AISOP program shape)
    if not isinstance(doc, list) or len(doc) != 2:
        _err(issues, "AISP_E_M1_SHAPE", "not a 2-message array")
        return _report(issues)
    if any(not isinstance(message, dict) for message in doc) or [message.get("role") for message in doc] != ["system", "user"]:
        _err(issues, "AISP_E_M1_ROLES", "messages must have system/user roles in order")
    system = doc[0].get("content") if isinstance(doc[0], dict) else {}
    user = doc[1].get("content") if isinstance(doc[1], dict) else {}
    if not isinstance(system, dict):
        system = {}
    if not isinstance(user, dict):
        user = {}
    if system.get("protocol") != "AISP V1.0.0":
        _err(issues, "AISP_E_M1_PROTOCOL", "protocol is not 'AISP V1.0.0'")
    if system.get("axiom_0") != "Human_Sovereignty_and_Wellbeing":
        _err(issues, "AISP_E_M1_AXIOM", "axiom_0 must be 'Human_Sovereignty_and_Wellbeing'")
    for f in ("name", "version", "flow_format"):
        if not isinstance(system.get(f), str) or not system[f].strip():
            _err(issues, "AISP_E_M1_FIELD", "system.content.%s is missing" % f)
    for f in ("summary", "description", "license", "system_prompt"):
        if f in system and not isinstance(system[f], str):
            _err(issues, "AISP_E_M1_FIELD", "system.content.%s must be a string when present" % f)
    if "params" in system and not isinstance(system["params"], dict):
        _err(issues, "AISP_E_M1_FIELD", "system.content.params must be an object when present")
    if "user_input" in user and not isinstance(user["user_input"], str):
        _err(issues, "AISP_E_M1_FIELD", "user.content.user_input must be a string when present")
    if system.get("flow_format") not in ("mermaid", "jsonflow", "hybrid"):
        _err(issues, "AISP_E_M1_FIELD", "flow_format must be mermaid, jsonflow or hybrid")
    if system.get("loading_mode") != REQUIRED_LOADING_MODE:
        _err(issues, "AISP_E_M1_LOADING_MODE", "system.content.loading_mode must be 'node'")
    instruction = user.get("instruction", "")
    if not isinstance(instruction, str) or "aisp_contract" not in instruction or "RUN aisop.main" not in instruction:
        _err(issues, "AISP_E_M1_INSTRUCTION", "instruction must name aisp_contract and RUN aisop.main")
    sid = system.get("id")
    if sid != name:
        _err(issues, "AISP_E_M2_ID_MISMATCH", "id (%r) != folder name (%r)" % (sid, name))
    license_value = system.get("license")
    if "license" not in system or (isinstance(license_value, str) and not license_value.strip()):
        _err(issues, "AISP_W_M1_LICENSE", "license missing or blank (SHOULD be set)")
    if "tools" in system and (not isinstance(system["tools"], list) or any(
        not isinstance(tool, str) or not tool.strip() for tool in system["tools"]
    )):
        _err(issues, "AISP_E_M1_FIELD", "system.content.tools must be an array of non-empty strings")
    aisop = user.get("aisop")
    if not isinstance(aisop, dict):
        aisop = {}
    if "main" not in aisop:
        _err(issues, "AISP_E_M1_MAIN", "aisop.main is missing")
    functions = user.get("functions")
    if not isinstance(functions, dict):
        functions = {}
    if not functions:
        _err(issues, "AISP_E_M1_FUNCTIONS", "user.content.functions is missing or empty")
    _check_graphs(aisop, functions, issues)

    # M3 (contract)
    contract = user.get("aisp_contract")
    if isinstance(user.get("aisp_contract"), str):
        _err(issues, "AISP_E_M3_STRING", "aisp_contract is a JSON-in-string")
    if not isinstance(contract, dict):
        _err(issues, "AISP_E_M3_CONTRACT", "user.content.aisp_contract is not a real object")
        contract = {}
    profile = contract.get("profile", "")
    if not isinstance(profile, str) or not re.fullmatch(r"aisp\.skill\.v[0-9]+", profile):
        _err(issues, "AISP_E_M3_PROFILE", "profile must match aisp.skill.v<major>")
    if "invocation" not in contract:
        _err(issues, "AISP_E_M3_INVOCATION", "aisp_contract.invocation is missing")
    if "non_negotiable" not in contract:
        _err(issues, "AISP_E_M3_NON_NEGOTIABLE", "aisp_contract.non_negotiable is missing")

    # M4 (enforced_by resolves)
    nn_list = contract.get("non_negotiable")
    if not isinstance(nn_list, list):
        nn_list = []
    for nn in nn_list:
        if not isinstance(nn, dict):
            _err(issues, "AISP_E_M4_GRAMMAR", "non_negotiable entry is not an object")
            continue
        eb = nn.get("enforced_by", "")
        if eb == "aisop.main":
            continue
        if eb == "tools":
            tools = system.get("tools")
            if not isinstance(tools, list) or not tools:
                _err(issues, "AISP_E_M4_TOOLS", "enforced_by tools requires a non-empty restricted tools allow-list")
            continue
        m = re.fullmatch(r"([A-Za-z0-9_]+)\.([A-Za-z0-9_]+):(sys\.[A-Za-z0-9_.]+)", eb) if isinstance(eb, str) else None
        if not m:
            _err(issues, "AISP_E_M4_GRAMMAR", "enforced_by %r is malformed" % eb)
            continue
        node, step, mech = m.group(1), m.group(2), m.group(3)
        fn = functions.get(node)
        if not isinstance(fn, dict) or not STEP_KEY_RE.fullmatch(step) or step not in fn:
            _err(issues, "AISP_E_M4_PHANTOM", "enforced_by %r points to a missing node/step" % eb)
        elif not re.match(re.escape(mech) + r"\s*\(", str(fn.get(step, "")).strip()):
            _err(issues, "AISP_E_M4_NO_MECHANISM", "%s.%s does not begin with %s" % (node, step, mech))

    # M5 (resource paths)
    res_list = contract.get("resources")
    if not isinstance(res_list, list):
        res_list = []
    for r in res_list:
        if not isinstance(r, dict):
            _err(issues, "AISP_E_M5_RESOURCE", "resource entry is not an object")
            continue
        p = r.get("path")
        p = p if isinstance(p, str) else ""
        if not p or "\x00" in p:
            _err(issues, "AISP_E_M5_RESOURCE", "resource path must be a non-empty filesystem path")
            continue
        # Normalize BOTH separators so Windows backslash traversal (..\evil) is
        # caught as well as POSIX '../evil'. Splitting only on '/' previously
        # let '..\\evil.txt' false-pass M5.
        parts = re.split(r"[\\/]", p)
        if p.startswith("/") or p.startswith("\\") or ".." in parts or re.match(r"^[A-Za-z]:", p):
            _err(issues, "AISP_E_M5_PATH_ESCAPE", "resource path %r is absolute or escapes" % p)
            continue
        scope = r.get("scope", "skill")
        if scope not in ("skill", "shared"):
            _err(issues, "AISP_E_M5_SCOPE", "resource scope is invalid")
            continue
        try:
            base = _confined_path(os.path.dirname(folder), "_shared") if scope == "shared" else folder
            _confined_path(base, p)
        except (OSError, ValueError, RuntimeError) as e:
            _err(issues, "AISP_E_SE1_PATH", "resource path is not confined: %s" % e)
        if r.get("mode") not in ("read_only", "execute_only", "read_and_execute"):
            _err(issues, "AISP_E_M5_MODE", "resource %r has an invalid mode" % (r.get("id")))
        if r.get("kind") == "script" and not r.get("requires_tools"):
            _err(issues, "AISP_W_M5_NO_REQUIRES_TOOLS", "script resource %r lacks requires_tools" % r.get("id"))

    # M6 (no self-declared trust)
    blob = json.dumps(contract).lower()
    if re.search(r'"(trusted|verified|safe)"\s*:\s*(true|"?(trusted|verified|safe)"?)', blob):
        _err(issues, "AISP_E_M6_SELF_TRUST", "skill self-declares trust (trusted/verified/safe)")

    # STATIC execute_mode checks (P3): every function-node execute_mode value,
    # when present, MUST be one of {"agent","inline"}. Missing execute_mode
    # falls back to inline and is reported as a warning for auditability. Non-agent
    # nodes above the step threshold are review warnings only; the threshold is
    # not a restriction on shorter agent nodes. This is a STATIC, structural check
    # only. HONESTY BOUNDARY (§23): this does NOT —
    # and statically CANNOT — verify the runtime R7 property that an
    # execute_mode:agent node is actually dispatched (not collapsed inline);
    # runtime dispatch is observable only at execution time.
    for fname, fn in functions.items():
        if not isinstance(fn, dict):
            _err(issues, "AISP_E_M1_FUNCTION_SHAPE", "function %r must be an object" % fname)
            continue
        step_items = _numeric_step_items(fn)
        if not step_items:
            _err(issues, "AISP_E_M1_STEP_SHAPE", "function %r must contain at least one numeric string step" % fname)
        for step_key, step_value in step_items:
            if not isinstance(step_value, str):
                _err(issues, "AISP_E_M1_STEP_SHAPE", "function %r.%s must be a string" % (fname, step_key))
        if "on_error" in fn:
            routing = fn["on_error"]
            if not isinstance(routing, dict) or any(
                not isinstance(target, str) or not target or target not in functions for target in routing.values()
            ):
                _err(issues, "AISP_E_M1_ON_ERROR", "function %r on_error must target existing function nodes" % fname)
        em = fn.get("execute_mode")
        valid_dispatch_intent = True
        if "execute_mode" not in fn:
            _err(issues, "AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE",
                 "function %r omits execute_mode; runtime falls back to inline" % fname)
            effective = "inline"
        elif not isinstance(em, str) or em not in VALID_EXECUTE_MODES:
            _err(issues, "AISP_E_M1_EXECUTE_MODE",
                 "function %r execute_mode %r not in {agent, inline}" % (fname, em))
            effective = "inline"
            valid_dispatch_intent = False
        else:
            effective = em
        count = _step_count(fn)
        if valid_dispatch_intent and count > AGENT_STEP_RECOMMENDATION_THRESHOLD and effective != "agent":
            _err(issues, "AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED",
                 "function %r has %d steps and is not agent; review whether execute_mode: agent is appropriate" % (fname, count))

    return _report(issues)


def _report(issues):
    hard = [i for i in issues if not i["code"].startswith("AISP_W_")]
    safety_codes = ("AISP_E_M5_PATH_ESCAPE", "AISP_E_SE1_PATH", "AISP_E_M4_PHANTOM", "AISP_E_M4_NO_MECHANISM", "AISP_E_M6_SELF_TRUST")
    safety = [i for i in issues if i["code"] in safety_codes]
    return {
        "m1_to_m6_pass": len(hard) == 0,
        "m7_checked": False,
        "coverage_note": "Lightweight M1-M6 subset only; mandatory M7 requires the bundled reference validator and executor-interface check.",
        "safety_pass": len(safety) == 0,
        "issues": issues,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_aisp_skill.py <skill-folder>", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(validate(sys.argv[1]), indent=2, ensure_ascii=False))
