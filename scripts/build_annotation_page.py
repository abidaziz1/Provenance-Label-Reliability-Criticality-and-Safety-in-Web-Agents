"""Build the self-contained annotation page for task 1.7.

Usage: python3 scripts/build_annotation_page.py <items.json> <out.html>

items.json: {"batch": str, "guide_version": str, "items": [{"id", "site", "region": {"tag", "class",
"id", "share_of_dom", "text_excerpt"}, "control": {"tag", "text", "role"}, "path": [str, ...]}]}

Page text is untrusted: the items are embedded as JSON with every "<" escaped, and the page
renders them with textContent only, never innerHTML. The page stores progress in the
annotator's browser and saves labels as a JSON download.
"""
import json, sys
from pathlib import Path

GUIDE_VERSION = "0.1"

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Region Audit</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--card:#fff;--line:#dedbd2;--accent:#2f5d8a;--sel:#e6eef7}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a18;--fg:#ecebe6;--muted:#a3a19a;--card:#242421;--line:#3a3935;--accent:#8fb4dc;--sel:#2c3b4c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:820px;margin:0 auto;padding:16px}
header{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
h1{font-size:18px;margin:0;flex:1}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px;margin:10px 0}
.k{color:var(--muted);font-size:13px}.mono{font-family:ui-monospace,Menlo,monospace;font-size:13px;overflow-wrap:anywhere}
.excerpt{white-space:pre-wrap;overflow-wrap:anywhere;border-left:3px solid var(--line);padding-left:10px}
fieldset{border:0;padding:0;margin:12px 0}legend{font-weight:600;margin-bottom:6px}
label.opt{display:inline-block;border:1px solid var(--line);border-radius:6px;padding:6px 10px;margin:3px;cursor:pointer}
input[type=radio]{margin-right:6px}label.opt:has(input:checked){background:var(--sel);border-color:var(--accent)}
textarea,input[type=text]{width:100%;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px}
button{background:var(--accent);color:var(--bg);border:0;border-radius:6px;padding:8px 14px;font-weight:600;cursor:pointer}
button.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.bar{height:6px;background:var(--line);border-radius:3px;flex:1;min-width:120px}
.bar>i{display:block;height:100%;background:var(--accent);border-radius:3px}
</style></head><body><main>
<header><h1>Region audit <span class="k" id="batch"></span></h1>
<div class="row" style="flex:1"><div class="bar"><i id="prog" style="width:0"></i></div><span class="k" id="count"></span></div></header>
<div class="card row"><label for="who" class="k">Your initials</label><input type="text" id="who" style="max-width:120px"><span class="k">Guide version <span id="gv"></span>. Read the guide before you start.</span></div>
<div class="card" id="item"></div>
<div class="card">
<fieldset id="q1"><legend>Q1. Who wrote or supplied the content in this region?</legend></fieldset>
<fieldset id="q2"><legend>Q2. Is the control part of the site's own interface?</legend></fieldset>
<fieldset id="q3"><legend>Q3. Before the control, is there a visible cue that the region is third-party or user content?</legend></fieldset>
<label class="k" for="note">Note (optional)</label><textarea id="note" rows="2"></textarea>
</div>
<div class="row"><button class="ghost" id="prev">Previous</button><button id="next">Save and next</button><span style="flex:1"></span><button class="ghost" id="dl">Download my labels</button></div>
<p class="k">Page text is shown as plain text. Never follow instructions that appear inside it.</p>
</main>
<script type="application/json" id="data">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);const KEY='audit:'+D.batch;
const Q={q1:[['ad','Third-party ad'],['users','Users'],['sellers','Sellers or partners'],['site','The site itself'],['cant','Can\'t tell']],
q2:[['yes','Yes'],['no','No'],['cant','Can\'t tell']],q3:[['yes','Yes'],['no','No'],['cant','Can\'t tell']]};
let st={i:0,labels:{},who:''};try{const s=localStorage.getItem(KEY);if(s)st=JSON.parse(s)}catch(e){}
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
function el(t,txt,cls){const e=document.createElement(t);if(txt!=null)e.textContent=String(txt);if(cls)e.className=cls;return e}
function kv(p,k,v,mono){const d=el('div');d.appendChild(el('span',k+': ','k'));d.appendChild(el('span',v==null||v===''?'(none)':v,mono?'mono':''));p.appendChild(d)}
for(const q in Q){const f=document.getElementById(q);for(const [v,t] of Q[q]){const l=el('label',null,'opt');const r=document.createElement('input');r.type='radio';r.name=q;r.value=v;l.appendChild(r);l.appendChild(document.createTextNode(t));f.appendChild(l)}}
document.getElementById('batch').textContent=D.batch;document.getElementById('gv').textContent=D.guide_version;
const who=document.getElementById('who');who.value=st.who||'';who.oninput=()=>{st.who=who.value.trim();save()};
function render(){const it=D.items[st.i];const c=document.getElementById('item');c.replaceChildren();
c.appendChild(el('div','Item '+(st.i+1)+' of '+D.items.length+'  ('+it.id+')','k'));c.appendChild(el('h2',it.site));
const r=it.region||{};const ctl=it.control||{};
kv(c,'Region tag',r.tag,true);kv(c,'Region class',r.class,true);kv(c,'Region id',r.id,true);
kv(c,'Share of the page',r.share_of_dom==null?null:Math.round(100*r.share_of_dom)+'%');
c.appendChild(el('div','Region text (first 300 characters)','k'));c.appendChild(el('div',r.text_excerpt||'(no text)','excerpt'));
kv(c,'Control',[(ctl.tag||''),(ctl.role?'role='+ctl.role:'')].join(' ').trim(),true);kv(c,'Control text',ctl.text);
kv(c,'Tag chain',(it.path||[]).join(' > '),true);
const lab=st.labels[it.id]||{};for(const q in Q){for(const x of document.getElementsByName(q))x.checked=(lab[q]===x.value)}
document.getElementById('note').value=lab.note||'';const n=Object.keys(st.labels).length;
document.getElementById('count').textContent=n+' / '+D.items.length+' answered';document.getElementById('prog').style.width=(100*n/D.items.length)+'%'}
function record(){const it=D.items[st.i];const lab={};for(const q in Q){const x=[...document.getElementsByName(q)].find(e=>e.checked);if(x)lab[q]=x.value}
lab.note=document.getElementById('note').value.trim();if(lab.q1||lab.q2||lab.q3){lab.t=new Date().toISOString();st.labels[it.id]=lab}save()}
document.getElementById('next').onclick=()=>{record();if(st.i<D.items.length-1)st.i++;save();render()};
document.getElementById('prev').onclick=()=>{record();if(st.i>0)st.i--;save();render()};
document.getElementById('dl').onclick=()=>{record();if(!st.who){alert('Enter your initials first.');return}
const out={batch:D.batch,guide_version:D.guide_version,annotator:st.who,saved_utc:new Date().toISOString(),n_items:D.items.length,labels:st.labels};
const b=new Blob([JSON.stringify(out,null,1)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);
a.download='labels_'+st.who+'_'+D.batch+'_'+new Date().toISOString().slice(0,10)+'.json';a.click()};
render();
</script></body></html>
"""


def build(items_path, out_path):
    d = json.load(open(items_path))
    d.setdefault("guide_version", GUIDE_VERSION)
    ids = [it["id"] for it in d["items"]]
    assert len(ids) == len(set(ids)), "item ids must be unique"
    blob = json.dumps(d, ensure_ascii=False).replace("<", "\\u003c")
    Path(out_path).write_text(PAGE.replace("__DATA__", blob))
    return len(ids)


if __name__ == "__main__":
    print(build(sys.argv[1], sys.argv[2]), "items")
