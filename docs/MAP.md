# PATH QUEST の地図

直す前にここを見る → grep -n で場所をさがす → その前後だけ読む → 変わる所だけ Edit → ビルド → テスト。

## 出口とビルド
- 遊ぶ人が開くのは **games/path-quest/index.html**（1ファイルで動く・場所も名前もこのまま。工房の取りこみ・App Store・試遊リンクはこれを使う）。**自動で作るファイル・手で直さない・読まない**（2行目に見出しの印）
- 直すのは **games/path-quest/src/page.html**（コード・CSS・HTML。約440KB）と **games/path-quest/assets/**（絵 208こ・webp）
- 作る：`node tools/build/build.mjs`（Node の標準だけ。page.html の `{{asset:名前}}` に assets/名前 を base64 で埋めて index.html を書く）
- ずれていないか見る：`node tools/build/build.mjs --check`（ちがえば 1 で終わる）
- 絵を足す・かえる：assets/ にファイルを置き、page.html に `{{asset:ファイル名}}`（例 `<image href="{{asset:a-hero.webp}}">`・`url("{{asset:ui-plank.webp}}")`）。page.html に base64 を書いてしまったら `node tools/build/extract.mjs` で assets/ に出す
- 名前のきまり：`a-◯`＝`<symbol id="a-◯">` の絵（騎士くん・敵・装備・物）、`ui-◯`・`t-◯`＝CSS の `--ui-◯`・`--t-◯`、`cr-◯`・`cr_w-◯`＝景色の生き物（const CR・CR_W）
- セーブのキー：`pathquest.meta.v1`・`pathquest.run.v3`（page.html 1454行。変えない）

## ファイル
| ところ | 役目 |
|---|---|
| games/path-quest/src/page.html | ゲームの本体（下の見出し） |
| games/path-quest/assets/ | 絵のファイル（読まない。見るときは Read で画像として） |
| games/path-quest/index.html | ビルドで作る出口（読まない・手で直さない） |
| games/path-quest/RELEASES.md | 版を出す合図（工房のお知らせに出る） |
| tools/build/ | build.mjs（作る・--check）・extract.mjs（埋めこみの絵を assets/ に出す） |
| tools/test/ | テスト（index.html を開く → 直したら先に build） |
| tools/ui/tweak_*.py | その日の直しの記録（1回だけ当てたもの。もう走らせない） |
| tools/audio/ | 音：sound.js を直して `python3 tools/audio/build_sound.py`（page.html の /*SND:begin*/〜/*SND:end*/ に入る）→ build |
| tools/ui/prune_css.py・dedupe_css.py | 使っていない CSS をけずる（page.html に当てる）→ build |
| tools/art/・tools/build_art.py・tools/ui/build_ui_1104.py・build_stamp_1104.py | 古い絵の道具（base64 を index.html に直接入れる）。使うときは build → 道具 → `node tools/build/extract.mjs games/path-quest/index.html` → build |
| tools/release/ | main への push で RELEASES.md の版にタグを付ける（.github/workflows/release.yml） |

## src/page.html の見出し（行の目安）
- 1〜12 head・13〜1326 CSS
  - 386 画面の作り・499 木と紙の見た目・525〜1079 fx の CSS（A 板・B 動き・C 生きもの・D 立ち上がる物）
  - 778 お店・946 下の棚（スキル・サイコロ・手持ち）・1015 ごほうび・1089 結果の画面・1120 特別な積み木・1256 Canva の UI・1323 スタンプ
- 1330〜1333 絵の置き場（CSS の変数と `<svg class="art-defs">` の symbol。中身はほぼ `{{asset:…}}`）・1334〜1449 画面の HTML
- 1450〜4833 script
  - 1454 セーブのキー・1462 盤面の形・1477 FXH（効果のフック）・1488 景色（20段ごと）・1540 スプライト・1569 BLOCKS（積み木の色）
  - 1632 Canva の絵を描く関数（U・FA・blockSVG・roadSVG・tileArt0・LOOT・LX）・1723 敵（1724 FOES・1744 QK くせ）
  - 1853 装備（1858 GEAR）・1952 スキル（1954 SKILLS）・1990 meta（2005 UPS 強化・2035 LOCK 段で出てくる）・2054 冒険の状態
  - 2121 道のつながり・2163 描く（render・patchKids・setH・offPause）・2423 効果・2530 動き（置く・歩く・戦い）
  - 2766 冒険中のスキル・2998 立っている敵・3056 魔法と毒・3094 おもちゃ箱（3119 TOY）・3182 おもちゃの武器・3258 ごほうび
  - 3361 冒険の終わり・3426 紙・3438 お店（shopAct・detailHTML）・3610 タップとドラッグ・3693 ボタン
  - 3768〜4100 音（自動で入る：sound.js から。ここは手で直さない）
  - 4129 テスト用（#fxtest で window.PQ）・4134 App Store のスクショの場面（navigator.webdriver のときだけ。`location.hash='shot=title|climb|foe|reward|boss|shop'`。道は lay() で並べる。たしかめ tools/test/shot_store.py）
  - 4164 fx A 板・4275 fx B 動き・4524 fx C 生きもの（4536 CR 景色の生き物）

## アプリ（App Store）
- アイコン：docs/kobo/icon.png（1024px・透明なし。Canva の AI＝A。tools/ART.md）
- スクショの場面は上の #shot=。アプリの設定（ios-kobo の apps/path-quest/）は【ios】のチャットが作る

## 試遊リンク（claude.ai のアーティファクト）
- いつもの：index.html を publish。はじめて用：index.html の最初の `<script>` の直後に記録とセーブを消す1行・`<title>` を「PATH QUEST はじめて用」にしたコピー（作り方は引き継ぎ claude/path-handoff.md）

## つぎの分割（code-rules の B）
- ② コードを src/ に分ける（1ファイル500行くらいまで・データは src/data/）。build.mjs がまとめる
- ③ この地図を分けたファイルに合わせる
- ④ CI でビルドのずれを見る（build.mjs --check）
