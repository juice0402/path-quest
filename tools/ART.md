# PATH QUEST の絵（Canva）

画風：やわらかい 3D のおもちゃ（色を塗った木とソフビ）・パステル・つやなし・白い背景。
1 回の生成で格子にまとめて作り、切り出して `games/path-quest/index.html` の `<!--ART-->` のまとまりに入れる。

## Canva
- 作業用デザイン：DAHZ0_Lb0zA「PATH QUEST 素材（作業用）」。1 ページめは使わない（自動で作られた絵）
- 2 ページめ以降に生成した絵を `insert_fill` でページいっぱいに置き、`export-design`（png・pro・ページの幅）で書き出す
- 生成した絵（メディア ID）
  - p2 キャラ 3×2（1536×1024）：MAHZ026MNNQ → hero, soldier, bugle, cannon, robot, boss
  - p3 装備 4×4（1264）：MAHZ1EXQlaU → w1〜w5, s1〜s5, c1〜c5, coin
  - p4 フィールドの物 4×4（1264）：MAHZ1KR_xwo → house, tree, pond, snowman, wall, fence, box, marble, candy, heart, bag, dice, door, stack, flag, key
  - p5 地面 3×2（1536×1024）：MAHZ1HeabO8 → grass, forest, lake, snow, castle（6 つめの石の床は未使用）
  - p6 積み木 3×2（1536×1024）：MAHZ1HpKFDM → b0〜b4（6 つめのクリーム色は未使用）
  - p7 タイトル（1024×1536）
- 生成は 1 枚ずつ、3 分以上あける（続けると待ち時間になる）

## 作り方
1. `python3 tools/slice_art.py 書き出し.png cut 行 列 名前,名前,…`（白い背景を外側からだけぬく。白い物は `--lo 250 --tol 5`、中の白い穴もぬくときは `--holes`）
2. 地面は切り出したあと内側の正方形だけ使い、もとの地面の色へ少し寄せる（g-grass など）
3. `python3 tools/build_art.py cut` で `<!--ART-->` のまとまりを作り直す（ゲームのコードはさわらない）

## ゲームの中
- 絵は `<symbol id="a-名前">`。`U(名前,x,y,w,h)` で 100×100 のマスに置く（下ぞろえ・形はそのまま）
- 地面とタイトルは CSS の変数（`--t-g-grass`・`--t-title`）
- `HAS_ART` が偽のとき（まとまりがないとき）は、前の SVG の絵のまま動く
- 騎士のぜんまいのかぎは、絵の後ろで今までどおり回る
