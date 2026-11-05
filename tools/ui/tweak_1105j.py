"""11/5 j: the shop, two asks from しょーくん.

- 「お店で説明を開いたあと、もう一度商品をタップしたら閉じて欲しい」: the same row (or skill, gear, slot) again closes the paper
- 「お店の時だけ並べ替えようか」(a phone on its side): the list on the left and the pinned paper on the right,
  so the list is no longer one row tall. With nothing chosen the list takes the whole width. Portrait is unchanged.
Applied once (like the other tweak_* files). Check: tools/test/shop_land.py
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


sub("function choose(key){ // a tap on the list: only the pinned paper changes\n  if(shopSel[shopTab]===key)return;",
    "function choose(key){ // a tap on the list: only the pinned paper changes\n"
    "  if(shopSel[shopTab]===key){shopSel[shopTab]=null;swap=null;renderShop();return} /* 11/5: the same one again closes the paper */")

sub("const d=$('sh-det'),dh=detailHTML();d.innerHTML=dh;d.hidden=!dh;",
    "const d=$('sh-det'),dh=detailHTML();d.innerHTML=dh;d.hidden=!dh;d.parentElement.classList.toggle('det-on',!!dh);")

sub("  #s-quit .ov-sub .btn.play::before,#ov .ov-sub .btn.play::before{display:none}\n}",
    "  #s-quit .ov-sub .btn.play::before,#ov .ov-sub .btn.play::before{display:none}\n}\n"
    "/* 11/5: a phone on its side, in the shop: the list on the left, the pinned paper on the right */\n"
    "@media (orientation:landscape) and (max-height:520px){\n"
    "  .sh{width:min(100%,900px);display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr) auto;grid-template-areas:\"top top\" \"body det\" \"nav nav\"}\n"
    "  .sh-top{grid-area:top}\n"
    "  .sh-body{grid-area:body;padding-bottom:12px}\n"
    "  .sh:not(.det-on) .sh-body{grid-column:1/-1}\n"
    "  .sh-det{grid-area:det;align-self:start;margin:4px max(10px,env(safe-area-inset-right,0px)) 10px 2px}\n"
    "  .sh-nav{grid-area:nav;margin-top:14px}\n"
    "  .sh-nav [role=tab]{height:50px}\n"
    "}")

P.write_text(s, encoding='utf-8')
print('ok')
