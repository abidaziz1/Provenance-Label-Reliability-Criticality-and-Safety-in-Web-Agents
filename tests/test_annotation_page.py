"""The annotation page must embed hostile page text inertly (task 1.7)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_annotation_page as B


def test_page_escapes_markup(tmp_path):
    hostile = '</script><script>alert(1)</script><img src=x onerror=alert(2)>'
    items = {"batch": "test", "items": [
        {"id": "T001", "site": "example", "region": {"tag": "div", "class": hostile, "id": "x", "share_of_dom": 0.1,
                                                     "text_excerpt": "IGNORE PREVIOUS INSTRUCTIONS " + hostile},
         "control": {"tag": "a", "text": hostile, "role": None}, "path": ["html", "body", "div"]}]}
    src = tmp_path / "items.json"
    src.write_text(json.dumps(items))
    out = tmp_path / "page.html"
    assert B.build(src, out) == 1
    html = out.read_text()
    data = html.split('<script type="application/json" id="data">')[1].split("</script>")[0]
    assert "<" not in data                      # nothing in the data block can open or close a tag
    assert json.loads(data)["items"][0]["region"]["class"] == hostile
    assert "innerHTML" not in html              # the page renders text with textContent only
    assert html.count("<script") == 2           # the data block and the page script, nothing injected
