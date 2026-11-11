"""Run this before the workshop: python check_setup.py"""
import json
import os
import sys
import urllib.request

ok = True


def report(passed: bool, label: str, fix: str = "") -> None:
    global ok
    ok = ok and passed
    print(("[ OK ] " if passed else "[FAIL] ") + label + ("" if passed else f"\n       Fix: {fix}"))


v = sys.version_info
report((3, 10) <= v[:2] <= (3, 13), f"Python {v.major}.{v.minor}", "install Python 3.10-3.13 (3.14 is not supported)")

try:
    import crewai
    report(True, f"CrewAI {crewai.__version__}")
except ImportError:
    report(False, "CrewAI", "activate your venv, then: pip install -r requirements.txt")

wanted = os.getenv("WORKSHOP_MODEL", "ollama/llama3.1").removeprefix("ollama/")
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
        names = [m["name"] for m in json.load(r)["models"]]
    report(True, "Ollama is running")
    full = wanted if ":" in wanted else wanted + ":latest"
    if full in names:
        report(True, f"Model {wanted}")
    else:
        # e.g. llama3.1:8b is installed but the code asks for llama3.1 (= llama3.1:latest)
        base = full.split(":")[0]
        other = next((n for n in names if n.split(":")[0] == base), None)
        fix = f"ollama cp {other} {full}" if other else f"ollama pull {wanted}"
        report(False, f"Model {wanted}" + (f" (found {other}, but the code asks for {full})" if other else ""), fix)
except OSError:
    report(False, "Ollama is running", "start the Ollama app (or run: ollama serve)")

print("\nALL GOOD - ready for the workshop." if ok else "\nFix the items above, then run this again.")
sys.exit(0 if ok else 1)
