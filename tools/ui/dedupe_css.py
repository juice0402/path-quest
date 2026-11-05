# 同じセレクタのルールがあとでもう一度同じプロパティを決めているとき、前のほうの宣言を消す（何度でも走らせてよい）
# 同じセレクタ・同じ場所（どちらも外側、または同じ @media の中）・同じプロパティ名・!important の強さが同じかあとのほうが強いときだけ消す
# usage: python3 tools/ui/dedupe_css.py [games/path-quest/index.html] [--dry]
import re, sys
P = next((a for a in sys.argv[1:] if not a.startswith('--')), 'games/path-quest/index.html')
DRY = '--dry' in sys.argv
s = open(P, encoding='utf-8').read()
m = re.search(r'<style>(.*?)</style>', s, re.S); css = m.group(1); cs, ce = m.span(1)

def blocks(text, base, ctx, out):
    i = 0
    while i < len(text):
        j = text.find('{', i)
        if j < 0: break
        d, k = 0, j
        while k < len(text):
            if text[k] == '{': d += 1
            elif text[k] == '}':
                d -= 1
                if d == 0: break
            k += 1
        head = re.sub(r'/\*.*?\*/', '', text[i:j], flags=re.S).strip()
        if head.startswith('@media') or head.startswith('@supports'):
            blocks(text[j + 1:k], base + j + 1, ctx + (re.sub(r'\s+', ' ', head),), out)
        elif not head.startswith('@'):
            out.append({'ctx': ctx, 'sel': re.sub(r'\s+', ' ', head), 'a': base + j + 1, 'b': base + k})
        i = k + 1
    return out

def decls(body):  # split on ; outside parentheses and quotes
    res, cur, d, q = [], '', 0, None
    for ch in body:
        if q:
            cur += ch
            if ch == q: q = None
            continue
        if ch in '"\'': q = ch
        elif ch == '(': d += 1
        elif ch == ')': d -= 1
        if ch == ';' and d == 0: res.append(cur); cur = ''
        else: cur += ch
    if cur.strip(): res.append(cur)
    return res

R = blocks(css, 0, (), [])
later = {}  # (ctx, sel) -> {prop: important}
edits = []  # (a, b, new body)
dropped = 0
for r in reversed(R):
    key = (r['ctx'], r['sel'])
    seen = later.setdefault(key, {})
    body = css[r['a']:r['b']]
    if '/*' in body: continue  # keep rules with comments inside as they are
    ds = decls(body); keep = []
    for dcl in ds:
        if ':' not in dcl or not dcl.strip(): keep.append(dcl); continue
        prop = dcl.split(':', 1)[0].strip().lower(); imp = '!important' in dcl
        if prop.startswith('--') or prop.startswith('-webkit-'): pass
        if prop in seen and (seen[prop] or not imp): dropped += 1; continue
        keep.append(dcl)
    for dcl in ds:
        if ':' in dcl:
            prop = dcl.split(':', 1)[0].strip().lower(); imp = '!important' in dcl
            seen[prop] = seen.get(prop, False) or imp
    if len(keep) != len(ds): edits.append((r['a'], r['b'], ';'.join(keep)))

new = css
for a, b, body in sorted(edits, reverse=True):
    new = new[:a] + body + new[b:]
# rules left with nothing in them go
new = re.sub(r'(?m)^[^{}@/\n][^{}\n]*\{\s*\}\n?', '', new)
print('declarations dropped', dropped, 'rules touched', len(edits), 'bytes', len(css), '->', len(new))
if not DRY:
    open(P, 'w', encoding='utf-8').write(s[:cs] + new + s[ce:])
