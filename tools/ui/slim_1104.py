# 11/4 軽くする：使っていない JS と HTML を消す（tweak_1104j.py のあとの index.html に1回だけ当てる）
# このあと tools/ui/prune_css.py で使っていない CSS を消す
import sys, re
P = sys.argv[1] if len(sys.argv) > 1 else 'games/path-quest/index.html'
s = open(P, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)

def cut_line(start):  # a whole line that begins with this text
    global s
    i = s.index(start); j = s.index('\n', i) + 1; s = s[:i] + s[j:]

# the critters no longer sit in a panel: the old drawing of one in a cell goes
i = s.index('  function critterHTML(i,k){'); j = s.index('  /* the obstacle\'s pose:', i); s = s[:i] + s[j:]
# the skill paper no longer says what a skill aims at
cut_line('const SKILL_AIM={')
# the old icon helper nobody calls
cut_line('const ICON=n=>U(n,28,30,44,44);')
# the drawer's pull tab was never put on the page
rep("const drawerIn=$('drawer-in'),drawer=drawerIn,pullBtn=document.createElement('button');", "const drawerIn=$('drawer-in'),drawer=drawerIn;")
cut_line("pullBtn.addEventListener('click',()=>setDrawer(!drawerOpen,false));")
# the climb gauge has been hidden since the status became one row: its markup and its update go
cut_line('    <div class="prog" id="prog" aria-hidden="true">')
i = s.index("  {const st=stepOf(run.top),nx=st%10;$('p-step')"); j = s.index('\n', i) + 1; s = s[:i] + s[j:]
s = s.replace(".prog{display:none!important}\n", "")

open(P, 'w', encoding='utf-8').write(s)
print('ok', len(s))
