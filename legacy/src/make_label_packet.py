"""Build labeling items in the LABELER'S view: user task + accessibility-tree path
context + region text. No class names or ids - those are stripped from the
accessibility tree Prismata's labeler consumes."""
import json, sys, random, collections
sys.path.insert(0,'/home/claude/idea3/src')
from lxml import html as LH
from deepparse import deep_parse, rendered_text
from dom_analysis import gt_provenance, is_actionable

random.seed(20260826)
FILES=['data/data/train/train_0.json','data/data/train/train_1.json','data/data/train/train_10.json']
tasks=[]
for f in FILES: tasks+=json.load(open(f))
corpus=json.load(open('results/corpus.json'))
keep={t['task_id']:t for t in corpus}
tasks=[t for t in tasks if t['annotation_id'] in keep]

PER_SITE_UNT=5
PER_SITE_TRU=5
bysite=collections.defaultdict(list)
items=[]
for t in tasks:
    for step,a in enumerate(t['actions']):
        if len(bysite[t['website']])>=60: break
        try:
            tree=LH.fromstring(a['raw_html']); deep_parse(tree)
        except Exception: continue
        nodes=[e for e in tree.iter() if isinstance(e.tag,str)]
        seeds={}
        for el in nodes:
            l,r=gt_provenance(el)
            if l: seeds[el]=(l,r)
        prov={}; rule={}
        for el in nodes:
            n=el
            while n is not None:
                if n in seeds: prov[el],rule[el]=seeds[n]; break
                n=n.getparent()
            else: prov[el],rule[el]='D','default:root'
            prov.setdefault(el,'D'); rule.setdefault(el,'default:root')
        for el in nodes:
            p=el.getparent()
            if p is None: continue
            is_region = prov[el]!='D' and prov.get(p,'D')=='D'
            # also sample TRUSTED containers so the labeler faces a real 4-way choice
            is_trusted_block = (prov[el]=='D' and el.tag in ('section','div','article','ul','nav','header','footer')
                                and 120<=len(rendered_text(el))<=1200
                                and prov.get(p,'D')=='D' and random.random()<0.06)
            if not (is_region or is_trusted_block): continue
            txt=rendered_text(el)
            if not (60<=len(txt)<=1200): continue
            chain=[]
            n=el; hops=0
            while n is not None and hops<7:
                d=n.tag
                if n.get('role'): d+=f"[role={n.get('role')}]"
                if n.get('aria_label'): d+=f"[aria={n.get('aria_label')[:30]}]"
                if n.get('title'): d+=f"[title={n.get('title')[:30]}]"
                chain.append(d); n=n.getparent(); hops+=1
            nact=sum(1 for d in el.iterdescendants() if isinstance(d.tag,str) and is_actionable(d))
            bysite[t['website']].append(dict(
                item_id=f"{t['annotation_id'][:8]}-{step}-{el.get('backend_node_id')}",
                site=t['website'], task=t['confirmed_task'],
                path=' > '.join(reversed(chain)),
                tag=el.tag, n_actionable_inside=nact,
                text=txt[:600],
                gt=prov[el], gt_rule=rule[el], kind=('untrusted' if is_region else 'trusted')))
for s,v in bysite.items():
    u=[x for x in v if x['kind']=='untrusted']; d=[x for x in v if x['kind']=='trusted']
    random.shuffle(u); random.shuffle(d)
    items+=u[:PER_SITE_UNT]+d[:PER_SITE_TRU]
random.shuffle(items)
json.dump(items,open('results/label_items.json','w'),indent=1)
print(f"{len(items)} items over {len(bysite)} sites")
print("GT mix:",dict(collections.Counter(i['gt'] for i in items)))
print("kind mix:",dict(collections.Counter(i['kind'] for i in items)))
print("per-site untrusted:",{s:sum(1 for i in items if i['site']==s and i['kind']=='untrusted') for s in sorted({i['site'] for i in items})})
