"""11/5 i: a broken run save must never freeze the page (found by tools/test/ui_robust.py corrupt).

- a run save without its numbers (top, hp…) passed the check and the result screen then looped forever
  looking for the next captain from step NaN → the check now wants the numbers, and stepOf turns NaN into 0
- a save that stops in the middle of a walk toward a cell that is not there goes back to building
Applied once (like the other tweak_* files).
"""
import pathlib, sys

P = pathlib.Path(__file__).resolve().parents[2] / 'games/path-quest/index.html'
s = P.read_text(encoding='utf-8')


def sub(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        sys.exit(f'expected {n} of: {old[:80]!r} (found {c})')
    s = s.replace(old, new)


sub("const stepOf=r=>Math.max(0,r-1);",
    "const stepOf=r=>Math.max(0,(r|0)-1); /* 11/5: a missing row number counts as the start, never NaN (the loops that look for the next captain would never end) */")
sub("if(run&&!(run.rows&&run.hand&&run.at>=0))run=null;",
    "const okNum=x=>typeof x==='number'&&isFinite(x);\n"
    "if(run&&!(run.rows&&typeof run.rows==='object'&&Array.isArray(run.hand)&&okNum(run.at)&&run.at>=0&&okNum(run.top)&&okNum(run.hp)&&okNum(run.maxHp)&&okNum(run.made)))run=null; /* 11/5: a save without its numbers starts fresh */\n"
    "if(run&&typeof run.phase!=='string')run.phase='build';")
sub("  if(run.phase==='walk'&&run.target>=0)return proceed();",
    "  if(run.phase==='walk'&&run.target>=0&&cellAt(run.target))return proceed(); /* 11/5: a walk toward a cell that is not there: build again */")

sub("const cellAt=i=>{const row=run.rows[rowOf(i)];return row?row[colOf(i)]:null};",
    "const cellAt=i=>{const row=run.rows[rowOf(i)];return row?row[colOf(i)]:null};\n"
    "if(run&&!cellAt(run.at)){run=null;store.del(SAVE)} /* 11/5: the knight's own cell is missing from the save: start fresh */")

P.write_text(s, encoding='utf-8')
print('ok')
