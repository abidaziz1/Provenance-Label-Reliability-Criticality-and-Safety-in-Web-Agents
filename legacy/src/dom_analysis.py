"""
Idea 3 smoke test - core DOM / provenance / criticality analysis.

Ground truth provenance is derived from raw_html (class, id, iframe src, ad-network
tokens). Labelers see only the accessibility-tree-like view (cleaned_html: tag, role,
aria_label, alt, title, text) - which is what Prismata's labeler actually consumes.
This asymmetry is deliberate: it prevents the labeler and the ground truth from being
the same function.

Provenance classes (Prismata Sec 2): D developer-authored, U user content,
H hosted-party, E external.
Capability classes: RW read-write, RO read-only, P pruned.
"""
import json, re, hashlib
from lxml import html as LH
from lxml import etree
from deepparse import deep_parse, rendered_text

# ---------------------------------------------------------------- token utils
def class_tokens(el):
    c = el.get('class') or ''
    return [t.lower() for t in re.split(r'[\s_]+', c) if t]

def idtok(el):
    return (el.get('id') or '').lower()

def all_ident(el):
    """class tokens + id + data-testid style hooks, lowercased"""
    toks = class_tokens(el)
    i = idtok(el)
    if i: toks.append(i)
    for k, v in el.attrib.items():
        if k.startswith('data_') and isinstance(v, str) and len(v) < 60:
            toks.append(v.lower())
    return toks

def tok_match(toks, pats):
    """word-ish match: token equals pat, or pat appears delimited by - or start/end"""
    for t in toks:
        for p in pats:
            if t == p: return p
            if re.search(r'(^|[-.])' + re.escape(p) + r'($|[-.0-9])', t): return p
    return None

# ---------------------------------------------------------------- GT rulesets
UGC = ['review','reviews','comment','comments','testimonial','ugc','usercontent',
       'user-content','userpost','feedback','reply','replies','forum','thread',
       'discussion','qa','question','answer','post-body','commenttext','guestbook',
       'customer-review','user-review','rating-text','opinion','usergenerated']
HOSTED = ['seller','sellers','merchant','vendor','marketplace','storefront',
          'listing','listings','partner','affiliate','thirdparty','third-party',
          'shop-item','host-listing','property-desc','provider-desc']
EXTERNAL = ['ad','ads','adv','advert','advertisement','adslot','adunit','adwrapper',
            'adcontainer','adbox','adframe','sponsor','sponsored','promo-partner',
            'dfp','gpt','googlesyndication','doubleclick','taboola','outbrain',
            'criteo','adsystem','adsbygoogle','banner-ad','native-ad','sponsoredcontent']
DEV = ['nav','navbar','navigation','header','footer','masthead','sitenav','menu',
       'breadcrumb','toolbar','sidebar-nav','site-header','site-footer','global-nav',
       'utility-nav','skip-link','logo']
DEV_TAGS = {'nav','header','footer','main'}
DEV_ROLES = {'navigation','banner','contentinfo','menubar','main','search'}

AD_HOST = re.compile(r'(googlesyndication|doubleclick|taboola|outbrain|criteo|adnxs|'
                     r'adsystem|amazon-adsystem|rubiconproject|pubmatic|openx|'
                     r'facebook\.com/plugins|platform\.twitter|disqus)', re.I)

ACTIONABLE_TAGS = {'a','button','input','select','textarea','option'}
NONINTERACTIVE_INPUT = {'hidden'}

def is_actionable(el):
    if el.get('is_clickable') == 'true':
        return True
    t = el.tag if isinstance(el.tag, str) else ''
    t = t.lower()
    if t == 'input' and (el.get('type') or '').lower() in NONINTERACTIVE_INPUT:
        return False
    if t in ACTIONABLE_TAGS:
        return True
    if (el.get('role') or '').lower() in {'button','link','textbox','checkbox','menuitem','tab','combobox'}:
        return True
    return False

def gt_provenance(el, page_host=None):
    """Return (label, rule) or (None, None) if no strong signal at this node."""
    tag = el.tag.lower() if isinstance(el.tag, str) else ''
    toks = all_ident(el)
    role = (el.get('role') or '').lower()

    # external: cross-origin frames / known ad+embed networks (highest precision)
    if tag in ('iframe','embed','object'):
        src = el.get('src') or el.get('data_src') or ''
        if AD_HOST.search(src):
            return 'E', 'iframe:adnetwork'
        return 'E', 'iframe:crossorigin'
    m = tok_match(toks, EXTERNAL)
    if m: return 'E', f'ident:ad:{m}'
    for v in el.attrib.values():
        if isinstance(v, str) and AD_HOST.search(v):
            return 'E', 'attr:adnetwork'

    m = tok_match(toks, UGC)
    if m: return 'U', f'ident:ugc:{m}'
    m = tok_match(toks, HOSTED)
    if m: return 'H', f'ident:hosted:{m}'

    if tag in DEV_TAGS: return 'D', f'tag:{tag}'
    if role in DEV_ROLES: return 'D', f'role:{role}'
    m = tok_match(toks, DEV)
    if m: return 'D', f'ident:dev:{m}'
    return None, None

# ------------------------------------------------------- labeler-visible cues
CUE_WORDS = re.compile(r'\b(review|reviews|comment|comments|rating|ratings|customer'
                       r'|user|posted by|wrote|feedback|sponsored|advertisement|ad'
                       r'|promoted|seller|sold by|listing|from our partners|q&a'
                       r'|question|answer|reply|discussion|forum)\b', re.I)

SELF_CUE = re.compile(r'(sponsored|advertisement|\badvert\b|promoted|paid partnership'
                      r'|posted by|written by|reviewed by|verified purchase|out of 5'
                      r'|stars?\b|helpful\?|report abuse|sold by|ships from|listed by'
                      r'|\d+\s+reviews?|comments?\s*\(\d+\)|reply\b)', re.I)

def visible_cue(el):
    """Cue an accessibility-tree labeler could actually see on THIS node."""
    for k in ('role','aria_label','alt','title','name','placeholder'):
        v = el.get(k)
        if v and CUE_WORDS.search(v):
            return f'{k}:{v[:40]}'
    if isinstance(el.tag, str) and el.tag.lower() in ('h1','h2','h3','h4','h5','h6'):
        txt = ' '.join(el.itertext())[:80]
        if CUE_WORDS.search(txt):
            return f'heading:{txt.strip()[:40]}'
    return None

def preceding_visible_cue(el, root, max_back=6):
    """Prismata claim: untrusted content on a critical path is preceded by a
    structural cue. Test whether such a cue exists IN THE LABELER'S INPUT."""
    # 1. self / ancestors
    node = el
    hops = 0
    while node is not None and hops <= max_back:
        c = visible_cue(node)
        if c: return f'ancestor[{hops}]:{c}'
        node = node.getparent(); hops += 1
    # 2. preceding siblings of self and of ancestors (headings above a region)
    node = el; hops = 0
    while node is not None and hops <= 3:
        sib = node.getprevious(); back = 0
        while sib is not None and back < max_back:
            c = visible_cue(sib)
            if c: return f'prevsib[{hops}/{back}]:{c}'
            for d in sib.iterdescendants():
                c = visible_cue(d)
                if c: return f'prevsib-desc[{hops}/{back}]:{c}'
                break
            sib = sib.getprevious(); back += 1
        node = node.getparent(); hops += 1
    return None

# ------------------------------------------------------------- core analysis
def analyse_observation(raw_html, cleaned_html=None, obs_id=None, site=None,
                        step=None, task_id=None):
    try:
        tree = LH.fromstring(raw_html)
    except Exception:
        return None
    dp = deep_parse(tree)                      # splice escaped third-party markup
    nodes = tree.xpath('//*')
    if not nodes: return None

    seeds = {}
    for el in nodes:
        lab, rule = gt_provenance(el)
        if lab: seeds[el] = (lab, rule)

    prov, provrule = {}, {}
    for el in nodes:
        node = el
        while node is not None:
            if node in seeds:
                prov[el], provrule[el] = seeds[node]; break
            node = node.getparent()
        else:
            prov[el], provrule[el] = 'D', 'default:root'
        if el not in prov:
            prov[el], provrule[el] = 'D', 'default:root'

    actionables = [el for el in nodes if is_actionable(el)]
    n_action = len(actionables)

    # GT reliability diagnostic: share of class tokens that are semantic (not hashed).
    sem = tot_tok = 0
    for el in nodes:
        for t in class_tokens(el):
            tot_tok += 1
            if len(t) >= 3 and re.search(r'[aeiou]', t) and not re.fullmatch(r'_?[a-z0-9]{6,10}', t):
                sem += 1
    semantic_class_ratio = sem / tot_tok if tot_tok else 0.0

    # node-level Claim-1: untrusted nodes that are ANCESTORS of an actionable element
    act_ancestors = set()
    for a_ in actionables:
        n_ = a_
        while n_ is not None:
            act_ancestors.add(id(n_)); n_ = n_.getparent()
    n_untrusted_on_critical_path = sum(1 for el in nodes
                                       if prov[el] != 'D' and id(el) in act_ancestors)

    untrusted_regions = []
    for el in nodes:
        if prov[el] == 'D': continue
        p_ = el.getparent()
        if p_ is None or prov.get(p_, 'D') == 'D':
            untrusted_regions.append(el)

    recs = []
    for r in untrusted_regions:
        desc_actions = [d for d in r.iterdescendants() if is_actionable(d)]
        if is_actionable(r): desc_actions.append(r)
        text = rendered_text(r)
        cue = preceding_visible_cue(r, tree)
        lead = text[:150]
        cue_selftext = bool(SELF_CUE.search(lead)) if lead else False
        cue_aria = any((r.get(k) and CUE_WORDS.search(r.get(k))) for k in
                       ('role','aria_label','alt','title','name'))
        n_desc = sum(1 for d in r.iterdescendants() if isinstance(d.tag, str))
        recs.append(dict(
            task_id=task_id, obs_id=obs_id, site=site, step=step,
            tag=r.tag if isinstance(r.tag, str) else 'na',
            prov=prov[r], rule=provrule[r],
            n_desc_nodes=n_desc,
            n_desc_actionable=len(desc_actions),
            text_len=len(text),
            text_snippet=text[:400],
            c1=len(desc_actions) > 0,
            c2=(len(text) >= 40 and n_action > 0),
            visible_cue=cue,
            has_visible_cue=cue is not None,
            cue_selftext=cue_selftext,
            cue_aria=cue_aria,
            cue_any=bool(cue is not None or cue_selftext or cue_aria),
        ))
    return dict(
        task_id=task_id, obs_id=obs_id, site=site, step=step,
        n_nodes=len(nodes), n_actionable=n_action,
        n_untrusted_regions=len(untrusted_regions),
        n_untrusted_nodes=sum(1 for v in prov.values() if v != 'D'),
        n_untrusted_actionable=sum(1 for e in actionables if prov[e] != 'D'),
        n_untrusted_on_critical_path=n_untrusted_on_critical_path,
        semantic_class_ratio=semantic_class_ratio,
        deep_parse=dp,
        regions=recs,
    )
