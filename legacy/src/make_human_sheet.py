import json, random, collections
items=json.load(open('results/label_items.json'))
sc=json.load(open('results/label_scores.json'))
rows={r['i']:r for r in sc['rows']}
random.seed(20260826)
dis=[i for i,r in rows.items() if not r['exact']]
agr=[i for i,r in rows.items() if r['exact']]
random.shuffle(dis); random.shuffle(agr)
# stratified: 22 disagreements (where adjudication decides something) + 18 agreements
# (to detect the case where BOTH labelers are wrong the same way). Reweight after.
sel=sorted(dis[:22]+agr[:18])
print(f"sheet: {len(sel)} items = {len([i for i in sel if i in dis])} disagreement + "
      f"{len([i for i in sel if i in agr])} agreement")
out=["# Provenance annotation sheet - Idea 3 smoke test",
"",
"You are labeling **who authored this block of page content**. This is the same",
"judgement Prismata's labeler makes. You see only what the labeler sees: the user's",
"task, the accessibility-tree path, and the rendered text. No CSS class names.",
"",
"## The four labels",
"",
"- **D** developer-authored - the site's own content and chrome: navigation, footers,",
"  filters, the site's own editorial/catalog copy, first-party promotions.",
"- **U** user content - written by end users: reviews, ratings text, comments, forum",
"  posts, testimonials, user-submitted media.",
"- **H** hosted-party - supplied by a third party the platform hosts: marketplace",
"  seller listings, Airbnb host listings, Eventbrite organiser events, travel supplier",
"  deals, crowdfunding project entries.",
"- **E** external - content from outside the platform: ads, sponsored placements,",
"  third-party embeds and survey widgets.",
"",
"Rule of thumb for D vs H: if an attacker could get text in here by signing up as a",
"seller/host/organiser, it is H. If only the site's own staff can edit it, it is D.",
"",
"Write your label in the LABEL line. If genuinely torn, write two letters (e.g. `D/H`).",
"",
"---",""]
for n,i in enumerate(sel,1):
    it=items[i]
    out+=[f"## {n}. item {i}  [site: {it['site']}]","",
          f"**User task:** {it['task']}","",
          f"**Path:** `{it['path'][-200:]}`","",
          f"**Interactive elements inside:** {it['n_actionable_inside']}","",
          "**Text:**","```",it['text'][:700],"```","",
          "LABEL: ____","","---",""]
open('results/human_annotation_sheet.md','w').write("\n".join(out))
json.dump(dict(selected=sel,strata={str(i):('disagree' if i in dis else 'agree') for i in sel},
               n_disagree_total=len(dis),n_agree_total=len(agr)),
          open('results/human_sheet_key.json','w'))
print("wrote results/human_annotation_sheet.md")
