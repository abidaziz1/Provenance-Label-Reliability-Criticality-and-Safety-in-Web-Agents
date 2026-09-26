"""Runs the 33-assertion suite for the six audit defects and the negative controls."""
import subprocess, sys
from pathlib import Path

def test_counterexamples_suite_passes():
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, str(root / "tests" / "counterexamples_suite.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "FAIL 0" in r.stdout
