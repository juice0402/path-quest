# 使っていない CSS を消す（何度でも走らせてよい）
# クラス名・ID が HTML にも JS にも出てこないセレクタだけを消す。動的に作るクラス（'lf-s-'+k、`k-${kd}`、' v'+n など）は残す
# usage: python3 tools/ui/prune_css.py [games/path-quest/index.html] [--dry]
import re, sys
P = next((a for a in sys.argv[1:] if not a.startswith('--')), 'games/path-quest/index.html')
DRY = '--dry' in sys.argv
s = open(P, encoding='utf-8').read()
D = re.compile(r'data:image/\w+;base64,[A-Za-z0-9+/=]+')
m = re.search(r'<style>(.*?)</style>', s, re.S); css = m.group(1); cs, ce = m.span(1)
rest = D.sub('', s[:cs] + s[ce:])

def alive(name):
    if re.search(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', rest): return True
    parts = name.split('-')
    for k in range(len(parts) - 1, 0, -1):  # 'lf-s-bee' made from 'lf-s-'+k
        pre = '-'.join(parts[:k]) + '-'
        if re.search(re.escape(pre) + r"(\$\{|'\s*\+|\"\s*\+)", rest): return True
    mm = re.match(r'^([a-z]{1,3})(\d+)$', name)  # 'v'+n, `r${g.r}`, 't'+k
    if mm: return True
    return False

def sel_alive(x):
    toks = re.findall(r'[.#]([A-Za-z_][\w-]*)', re.sub(r'\[[^\]]*\]', '', re.sub(r':not\([^)]*\)', '', x)))
    return all(alive(t) for t in toks)

out, i, removed, cut = [], 0, 0, 0
def walk(text):
    global removed, cut
    res, i = [], 0
    while i < len(text):
        j = text.find('{', i)
        if j < 0: res.append(text[i:]); break
        d, k = 0, j
        while k < len(text):
            if text[k] == '{': d += 1
            elif text[k] == '}':
                d -= 1
                if d == 0: break
            k += 1
        head, body = text[i:j], text[j + 1:k]
        lead = re.match(r'\s*(?:/\*.*?\*/\s*)*', head, re.S).group(0)  # comments before the rule stay
        sel = head[len(lead):].strip()
        if sel.startswith('@media') or sel.startswith('@supports'):
            inner = walk(body)
            if inner.strip(): res.append(f'{lead}{sel}{{{inner}}}')
            else: removed += 1; res.append(lead)
        elif sel.startswith('@') or sel.startswith(':root') or sel.startswith('from') or sel.startswith('to') or re.match(r'^[\d.%,\s]+$', sel):
            res.append(text[i:k + 1])
        else:
            parts = [x.strip() for x in sel.split(',')]
            keep = [x for x in parts if sel_alive(x)]
            if not keep: removed += 1; res.append(lead.rstrip(' ') if lead.strip() else lead)
            elif len(keep) < len(parts): cut += len(parts) - len(keep); res.append(f"{lead}{','.join(keep)}{{{body}}}")
            else: res.append(text[i:k + 1])
        i = k + 1
    return ''.join(res)

new = walk(css)
new = re.sub(r'\n{3,}', '\n\n', new)
print('rules removed', removed, 'selectors cut from lists', cut, 'bytes', len(css), '->', len(new))
if not DRY:
    s = s[:cs] + new + s[ce:]
    open(P, 'w', encoding='utf-8').write(s)
