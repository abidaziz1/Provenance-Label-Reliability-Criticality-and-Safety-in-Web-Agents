import json, collections, numpy as np
items=json.load(open('results/label_items.json'))
lab={}
for b in ('b1','b2','b3'):
    lab.update({int(k):v for k,v in json.load(open(f'results/claude_labels_{b}.json')).items()})
print(f"labeled {len(lab)}/{len(items)} items")
UNT={'U','H','E'}
rows=[]
for i,it in enumerate(items):
    if i not in lab: continue
    gt=it['gt']; pd=lab[i]
    rows.append(dict(i=i,site=it['site'],gt=gt,pred=pd,
                     gt_unt=gt in UNT, pred_unt=pd in UNT,
                     false_trust=(gt in UNT and pd=='D'),
                     false_prune=(gt=='D' and pd in UNT),
                     exact=(gt==pd)))
n=len(rows)
print(f"\n=== 4-way exact agreement (Claude vs structural GT): "
      f"{100*sum(r['exact'] for r in rows)/n:.1f}%  (n={n})")
print("\nconfusion (rows=structural GT, cols=Claude):")
labs=['D','U','H','E']
print("      "+"".join(f"{c:>6s}" for c in labs))
for g in labs:
    print(f"  {g:3s} "+"".join(f"{sum(1 for r in rows if r['gt']==g and r['pred']==c):6d}" for c in labs))
gu=[r for r in rows if r['gt_unt']]; gd=[r for r in rows if not r['gt_unt']]
ft=sum(r['false_trust'] for r in gu); fp=sum(r['false_prune'] for r in gd)
print(f"\n=== security-relevant binary view ===")
print(f"  FALSE-TRUST rate  P(label=trusted | GT untrusted) = {ft}/{len(gu)} = {100*ft/len(gu):.1f}%")
print(f"  FALSE-PRUNE rate  P(label=untrusted | GT trusted) = {fp}/{len(gd)} = {100*fp/len(gd):.1f}%")
print(f"  [Prismata reports 1-precision = 1.3% (nano) to 4.5% (mini) on WebArena]")
# reweight to corpus base rate
M=json.load(open('results/C_measurements.json'))
base=M['totals']['untrusted']/M['totals']['nodes']
prec = (1-ft/len(gu))*base / max((1-ft/len(gu))*base + (fp/len(gd))*(1-base), 1e-9)
print(f"\n  corpus untrusted base rate = {100*base:.2f}%")
print(f"  base-rate-corrected 'allowed-element precision' analogue = {100*(1-(ft/len(gu))*base/max(base*(ft/len(gu))+(1-base)*(1-fp/len(gd)),1e-9)):.2f}%")
print(f"\n=== per-site error structure (the correlation question) ===")
bysite=collections.defaultdict(lambda: dict(n=0,ft=0,nu=0,fp=0,nd=0,err=0))
for r in rows:
    b=bysite[r['site']]; b['n']+=1; b['err']+=(not r['exact'])
    if r['gt_unt']: b['nu']+=1; b['ft']+=r['false_trust']
    else: b['nd']+=1; b['fp']+=r['false_prune']
print(f"  {'site':16s} {'n':>3s} {'4way err':>9s} {'untrusted n':>12s} {'false-trust':>12s}")
for s,b in sorted(bysite.items(), key=lambda kv:-kv[1]['err']/max(kv[1]['n'],1)):
    ftr=f"{b['ft']}/{b['nu']}" if b['nu'] else "-"
    print(f"  {s:16s} {b['n']:3d} {100*b['err']/b['n']:8.1f}% {b['nu']:12d} {ftr:>12s}")
# ICC of binary exact-error by site (one-way random effects)
grp=collections.defaultdict(list)
for r in rows: grp[r['site']].append(0.0 if r['exact'] else 1.0)
k=len(grp); N=len(rows); gm=np.mean([0.0 if r['exact'] else 1.0 for r in rows])
ssb=sum(len(v)*(np.mean(v)-gm)**2 for v in grp.values())
ssw=sum(sum((x-np.mean(v))**2 for x in v) for v in grp.values())
msb=ssb/(k-1); msw=ssw/(N-k); n0=N/k
icc=(msb-msw)/(msb+(n0-1)*msw)
print(f"\n  ICC of labeling error by SITE = {icc:.3f}")
print(f"  overall 4-way error rate = {100*gm:.1f}%")
# bootstrap CI on ICC
rng=np.random.default_rng(20260826); boots=[]
sites=list(grp)
for _ in range(4000):
    bs=rng.choice(sites,size=len(sites),replace=True)
    vals=[]; g2={}
    for j,s in enumerate(bs): g2[f'{s}_{j}']=grp[s]
    kk=len(g2); allv=[x for v in g2.values() for x in v]; NN=len(allv)
    if kk<2 or NN<=kk: continue
    gm2=np.mean(allv)
    b_=sum(len(v)*(np.mean(v)-gm2)**2 for v in g2.values())/(kk-1)
    w_=sum(sum((x-np.mean(v))**2 for x in v) for v in g2.values())/(NN-kk)
    n02=NN/kk
    boots.append((b_-w_)/(b_+(n02-1)*w_) if (b_+(n02-1)*w_)!=0 else 0)
print(f"  bootstrap 95% CI for site ICC = [{np.percentile(boots,2.5):.3f}, {np.percentile(boots,97.5):.3f}]  (B={len(boots)})")
json.dump(dict(n=n,false_trust=ft,n_untrusted=len(gu),false_prune=fp,n_trusted=len(gd),
               icc_error_site=float(icc),
               icc_ci=[float(np.percentile(boots,2.5)),float(np.percentile(boots,97.5))],
               exact_agreement=float(sum(r['exact'] for r in rows)/n),
               rows=rows), open('results/label_scores.json','w'))
