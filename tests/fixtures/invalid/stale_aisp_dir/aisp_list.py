import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    (ROOT / "aisp_list.json").write_text(json.dumps({"aisp_list_version": "1.0", "skills": []}), encoding="utf-8")
