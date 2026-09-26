"""Task 1.13: the committed Colab notebooks are exactly what their builders produce, and notebook 03's
batch scoring path (score tables) gives the same gate decisions as the direct scorer."""
import json, os, random, subprocess, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDERS = {
    "build_nb1_v2.py": "01_corpus_fidelity_and_structure_only_detection_v2.ipynb",
    "build_nb2_v2.py": "02_cross_vendor_coupling_at_power_v2.ipynb",
    "build_nb3_v2.py": "03_agent_compliance_pilot_v2.ipynb",
}


@pytest.mark.parametrize("builder,notebook", sorted(BUILDERS.items()))
def test_committed_notebook_matches_its_builder(tmp_path, builder, notebook):
    env = dict(os.environ, IDEA3_NB_OUT=str(tmp_path))
    r = subprocess.run([sys.executable, str(ROOT / "notebooks" / "builders" / builder)],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    built = (tmp_path / notebook).read_bytes()
    committed = (ROOT / "notebooks" / "colab" / notebook).read_bytes()
    assert built == committed, f"{notebook} differs from {builder}: run the builder and commit the result"


def _cells(nb_name, *markers):
    nb = json.load(open(ROOT / "notebooks" / "colab" / nb_name))
    out = []
    for m in markers:
        out.append(next("".join(c["source"]) for c in nb["cells"]
                        if c["cell_type"] == "code" and m in "".join(c["source"])))
    return out


def test_nb03_score_tables_match_direct_scoring():
    shard = ROOT / "data" / "mind2web" / "data" / "train" / "train_10.json"
    if not shard.exists():
        pytest.skip("Mind2Web shard not present (scripts/fetch_mind2web.py)")
    sys.path.insert(0, str(ROOT / "src"))
    import pipeline_v2 as P
    ns = {k: getattr(P, k) for k in dir(P) if not k.startswith("__")}
    import re
    from lxml import html as LH
    ns.update(re=re, LH=LH, OBS_CHARS=60_000)
    builder_cell, scorer_cell = _cells("03_agent_compliance_pilot_v2.ipynb", "def build_trial", "def score_table")
    exec(builder_cell, ns)
    exec(scorer_cell, ns)
    tasks = json.load(open(shard))
    rng = random.Random(7)
    checked = 0
    for t in tasks:
        for act in t["actions"][:2]:
            for env, atk, pol in (("page", "A2_influence_escape", "P_correct"), ("page", "A1_containment", "P_err1_derived"),
                                  ("narrow", "A1_containment", "P_err1_fixedgate"), ("page", "A2_influence_escape", "P_none")):
                for inject in (True, False):
                    tr = ns["build_trial"](t, act, env, atk, pol, inject=inject)
                    if tr is None:
                        continue
                    tab = ns["score_table"](tr)
                    rendered = re.findall(r"\[id=(\d+)\]", tr["obs_sent"])
                    picks = {None, tr["tid"], tr["a2_id"], "999001", "123456789", ns["controller_choose"](tr)}
                    picks |= set(rng.sample(rendered, min(3, len(rendered))))
                    for sel in picks:
                        a = ns["score"](tr, sel); b = ns["score_from_table"](tab, sel)
                        a.pop("gate_reason"); b.pop("gate_reason")
                        assert a == b, (env, atk, pol, inject, sel)
                        checked += 1
    assert checked > 50
