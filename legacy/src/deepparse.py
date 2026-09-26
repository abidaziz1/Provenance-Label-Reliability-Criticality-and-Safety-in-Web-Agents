"""
Mind2Web raw_html embeds nested frame/ad content as ESCAPED MARKUP inside text
nodes. Naive itertext() therefore returns serialized tags as if they were visible
text, and every interactive element inside a third-party frame is invisible to a
tag-based actionable-element detector.

deep_parse() recursively unescapes and splices that content back into the tree so
untrusted third-party regions are measured as what they actually are.
"""
import re
from lxml import html as LH

TAGLIKE = re.compile(r'<\s*(div|span|a|iframe|img|p|ul|li|button|input|table|tr|td|'
                     r'section|article|h[1-6]|form|label|select|option|video|svg)\b',
                     re.I)

def looks_like_markup(s):
    return bool(s) and len(s) > 40 and TAGLIKE.search(s) is not None

def deep_parse(tree, max_levels=5, stats=None):
    """Iterative: each pass unescapes one nesting level across the WHOLE tree.
    (An earlier recursive version capped descent depth and silently missed ad
    frames at DOM depth 11-19. Kept as a note: this class of bug inflates
    'no third-party interactive content' conclusions.)"""
    if stats is None: stats = {'levels': 0, 'spliced': 0, 'nodes_added': 0}
    for level in range(max_levels):
        spliced_this = 0
        for el in list(tree.iter()):
            if not isinstance(el.tag, str):
                continue
            if looks_like_markup(el.text):
                frag = _parse(el.text)
                if frag is not None and len(frag):
                    el.text = None
                    for i, c in enumerate(list(frag)):
                        el.insert(i, c)
                    spliced_this += 1
                    stats['nodes_added'] += len(list(frag.iter())) - 1
            parent = el.getparent()
            if parent is not None and looks_like_markup(el.tail):
                frag = _parse(el.tail)
                if frag is not None and len(frag):
                    el.tail = None
                    idx = list(parent).index(el) + 1
                    for j, cc in enumerate(list(frag)):
                        parent.insert(idx + j, cc)
                    spliced_this += 1
                    stats['nodes_added'] += len(list(frag.iter())) - 1
        stats['spliced'] += spliced_this
        if spliced_this == 0:
            break
        stats['levels'] = level + 1
    return stats


def rendered_text(el):
    """Visible text only: excludes anything that is still serialized markup."""
    out = []
    for t in el.itertext():
        if not t: continue
        t = t.strip()
        if not t: continue
        if looks_like_markup(t):
            continue
        out.append(t)
    return ' '.join(out)

def _parse(s):
    try:
        return LH.fragment_fromstring(s, create_parent='div')
    except Exception:
        try:
            return LH.fromstring('<div>' + s + '</div>')
        except Exception:
            return None
