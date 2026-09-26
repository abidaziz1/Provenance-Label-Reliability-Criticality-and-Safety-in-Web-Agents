"""One test per claims-ledger row (K1 to K12): recompute the headline value from the committed
result file. Added 25 Sep 2026, task N0.1. No Mind2Web data needed."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
sys.path.insert(0, str(ROOT / "scripts"))


def pct(a, b):
    return round(100 * a / b, 2)


def _reconcile():
    return json.load(open(R / "reconcile_v2.json"))


def _on_target(g):
    rows = [x for x in _reconcile() if x["has_target"]]
    n = sum(x["G"][g]["n"] for x in rows)
    on = sum(x["G"][g]["on_target"] for x in rows)
    return len(rows), n, on


def test_K1_region_on_root_to_target_path():
    obs, n, on = _on_target("G0_region")
    assert (obs, n, on) == (1103, 5086, 88)
    assert pct(on, n) == 1.73


def test_K2_region_plus_items_on_root_to_target_path():
    obs, n, on = _on_target("G1_region_plus_items")
    assert (obs, n, on) == (1103, 10877, 123)
    assert pct(on, n) == 1.13


def test_K3_K4_K5_descendant_only_and_root_counted():
    d = json.load(open(R / "descendant_only_v2.json"))
    assert (d["57_n"], d["16_n"]) == (5317, 2054)
    assert pct(d["57_desc_pris"], d["57_n"]) == 49.93      # K3
    assert pct(d["16_desc_pris"], d["16_n"]) == 41.58      # K4
    assert pct(d["57_self_pris"], d["57_n"]) == 71.43      # K5, 57-site
    assert pct(d["16_self_pris"], d["16_n"]) == 75.85      # K5, 16-site


def test_K6_deployable_vs_oracle_gate():
    g = json.load(open(R / "gate_comparison.json"))
    assert (g["K"], g["n_obs"], g["regions"]) == (21, 410, 2596)
    assert (g["crit"]["label_aware"], g["crit"]["ORACLE"]) == (196, 106)
    assert round(g["crit"]["label_aware"] / g["crit"]["ORACLE"], 2) == 1.85
    assert round(100 - pct(g["agree"]["label_aware"], g["regions"]), 1) == 7.3


def test_K7_gate_width_curve_16_site():
    g = json.load(open(R / "C_gate_v2.json"))["gate16"]
    assert pct(*g["5"]) == 0.71
    assert pct(*g["1000000"]) == 75.99


def _l4(rows, env, atk, pol):
    xs = [r["L4"] for r in rows if (r["envelope"], r["attack"], r["policy"], r["arm"]) == (env, atk, pol, "injected")]
    return len(xs), round(100 * sum(xs) / len(xs), 1)


def test_K8_to_K11_ablation_rates():
    rows = json.load(open(R / "ablation_v2.json"))
    assert len(rows) == 5088 and len({r["site"] for r in rows}) == 27
    assert _l4(rows, "narrow", "A1", "P_err1_fixedgate") == (159, 0.0)   # K8
    assert _l4(rows, "page", "A1", "P_err1_fixedgate") == (159, 0.0)     # K8
    assert _l4(rows, "page", "A1", "P_err1_derived") == (159, 96.9)      # K9
    assert _l4(rows, "narrow", "A1", "P_err1_derived") == (159, 0.0)     # K9
    assert _l4(rows, "page", "A2", "P_correct") == (159, 43.4)           # K10
    assert _l4(rows, "narrow", "A2", "P_correct") == (159, 0.0)          # K10
    assert all(r["L4"] is False for r in rows if r["arm"] == "control")  # every paired control is 0.0%


def test_K9_K11_contrast_intervals():
    import ablation_contrasts as A
    res = {(c["envelope"], c["attack"], c["contrast"]): c for c in A.compute(A.load())}
    k9 = res[("page", "A1", "P_err1_derived - P_err1_fixedgate")]
    k11 = res[("page", "A2", "P_err1_fixedgate - P_correct")]
    k8 = res[("page", "A1", "P_err1_fixedgate - P_correct")]
    assert round(100 * k9["delta_L4"], 1) == 96.9 and [round(100 * v, 1) for v in k9["ci95"]] == [91.8, 100.0]
    assert round(100 * k11["delta_L4"], 1) == 33.3 and [round(100 * v, 1) for v in k11["ci95"]] == [15.0, 55.7]
    assert k8["delta_L4"] == 0.0 and k8["ci95"] == [0.0, 0.0]


def test_K12_actionability_clauses_on_archives():
    tot = {}
    for x in _reconcile():
        for k, v in x["clause"].items():
            tot[k] = tot.get(k, 0) + v
    assert tot == {"link": 298756, "formcontrol": 80531, "ariarole": 23307}


EXP = ROOT / "experiments"


def test_K16_K17_leaf_vs_region_criticality():
    s = json.load(open(EXP / "2026-09-25_N0.2_c1-robustness" / "results" / "c1_robustness.json"))["summary"]
    assert s["G4_leafpath"]["attr|nonhidden|desc|all"] == 1.58          # K16
    assert s["G4_leafpath"]["attr|nonhidden|desc|visunits"] == 2.10     # K16
    assert s["G0_region"]["attr|nonhidden|desc|visunits"] == 52.56      # K17
    assert s["G1_region_plus_items"]["attr|nonhidden|desc|visunits"] == 45.21
    assert s["G0_region"]["attr|any|desc|all"] == 49.93                 # same as K3


def test_K18_K19_K20_exposure_per_element_page_task():
    u = json.load(open(EXP / "2026-09-25_N0.2_unit-ladder" / "results" / "unit_ladder.json"))
    a = u["attr"]
    assert (u["pages"], u["tasks"], u["sites"]) == (1163, 145, 57)
    assert a["element_inside_untrusted_pct"] == 9.19                   # K18
    assert a["page_exposed_pct"] == 38.09 and a["page_exposed_ci95_site"] == [27.72, 49.05]   # K19
    assert a["task_exposed_pct"] == 59.31 and a["task_exposed_ci95_site"] == [47.18, 70.95]   # K19
    assert u["target_inside_untrusted_pct"] == 7.71                     # K20


def test_K21_archive_attribute_whitelist():
    a = json.load(open(EXP / "2026-09-25_1.8_attr-survival" / "results" / "attr_survival.json"))
    assert (a["sites"], a["pages"]) == (57, 1163)
    assert len(a["attribute_names_present"]) == 21
    assert list(a["data_attribute_names"]) == ["data_pw_testid_buckeye"]
    for k in ("on*", "tabindex", "contenteditable", "href", "for", "hidden", "style"):
        assert a["sites_with_defense_input_under_1_per_1k"][k] == 57


def test_K22_K23_ucm_selectors_on_archive():
    s = json.load(open(EXP / "2026-09-25_C7_ucm-selectors-on-archive" / "results" / "ucm_selectors_on_archive.json"))["summary"]
    assert s["archive_booking_pages"] == 131
    h, l = s["booking_hand_archive"], s["booking_llm_archive"]
    assert (h["match_on_ucm_captures"], h["of_those_match_nothing_on_archive"]) == (25, 24)
    assert (l["match_on_ucm_captures"], l["of_those_match_nothing_on_archive"]) == (68, 68)
    assert s["booking_hand"]["data_attr"]["pct"] == 92.0 and s["booking_llm"]["data_attr"]["pct"] == 95.7


def test_K25_stripping_alone_disables_ucm_booking_selectors():
    s = json.load(open(EXP / "2026-09-26_C7c_live-strip-vs-drift" / "results" / "live_strip_test.json"))["summary"]
    h, p = s["hand"], s["pooled"]
    assert (h["match_live"], h["of_those_match_nothing_after_strip"], h["share_disabled_by_strip_pct"]) == (13, 11, 84.6)
    assert (p["match_live"], p["of_those_match_nothing_after_strip"], p["share_disabled_by_strip_pct"]) == (57, 53, 93.0)
    assert (s["hashed_class_tokens"]["n"], s["hashed_class_tokens"]["present_live"]) == (23, 16)


def test_K24_labeler_sensitivity_band():
    r = json.load(open(EXP / "2026-09-25_N0.3b_labeler-sensitivity" / "results" / "labeler_sensitivity.json"))
    assert (r["pages"], r["tasks"], r["sites"], r["mismatch_vs_gt_provenance_sampled"]) == (1163, 145, 57, 0)
    v = r["variants"]
    assert (v["V0_base"]["page_pct"], v["V0_base"]["task_pct"]) == (38.09, 59.31)          # equals K19
    v5 = v["V5_E_only(ads+crossorigin iframes, class/id/src)"]
    assert (v5["page_pct"], v5["page_ci"], v5["task_pct"], v5["task_ci"]) == (24.33, [14.88, 35.55], 39.31, [27.08, 52.32])
    v4 = v["V4_strict(V1+V2+V3)"]
    assert (v4["page_pct"], v4["task_pct"], v4["elem_pct"], v4["target_pct"]) == (27.77, 45.52, 2.02, 1.0)
    d = r["V0_detail"]
    assert (d["g4_crit"], d["g4_vis_leaves"], d["g4_crit_with_all_children_seeded_D"]) == (808, 38477, 808)


def test_K26_actionability_rules():
    r = json.load(open(EXP / "2026-09-26_C7b_actionability-on-archive" / "results" / "actionability_on_archive.json"))
    assert (r["pages"], r["tasks"], r["sites"], r["anchors_with_href_total"]) == (1163, 145, 57, 0)
    r0, r1 = r["rules"]["R0_tag"], r["rules"]["R1_href_required"]
    assert (r0["G0_region_crit_visunits_pct"], r0["G3_node_crit_visunits_pct"], r0["G4_leafpath_crit_visunits_pct"]) == (52.56, 19.57, 2.1)
    assert (r0["page_exposed_pct"], r0["task_exposed_pct"]) == (38.09, 59.31)             # R0 reproduces K16, K17, K19
    assert r1["G3_node_crit_visunits_pct"] == 9.4 and r["R1_over_R0"]["G3_node"] == 0.48   # primary outcome
    assert r["exploratory_G3_ratio_ci95_site"] == [0.323, 0.638]
