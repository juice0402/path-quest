// PATH QUEST のビルド：games/path-quest/src/page.html と games/path-quest/assets/ から、遊ぶ人が開く games/path-quest/index.html を作る。
// 絵は {{asset:名前}} の所に base64 で埋めこむ（index.html は今までどおり1ファイルで動く）。Node の標準だけ。
//
//   node tools/build/build.mjs          作る
//   node tools/build/build.mjs --check  作りなおした中身が index.html と同じか見るだけ（ちがえば 1 で終わる）
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
export const GAME = join(ROOT, 'games/path-quest');
export const SRC = join(GAME, 'src/page.html');
export const ASSETS = join(GAME, 'assets');
export const OUT = join(GAME, 'index.html');
// index.html の2行目（<!doctype html> のすぐ下）に入る
export const HEADER = '<!-- 自動で作るファイル・手で直さない。直すのは games/path-quest/src/page.html と games/path-quest/assets/ で、node tools/build/build.mjs で作る（地図 docs/MAP.md） -->';
export const MARK = /\{\{asset:([A-Za-z0-9._-]+)\}\}/g;
export const MIME = { webp: 'image/webp', png: 'image/png', jpg: 'image/jpeg', gif: 'image/gif', svg: 'image/svg+xml', mp3: 'audio/mpeg', ogg: 'audio/ogg', wav: 'audio/wav', m4a: 'audio/mp4' };

export function build(page, assetsDir = ASSETS) {
  const used = new Set(), missing = [];
  let out = page.replace(MARK, (m, name) => {
    const f = join(assetsDir, name);
    if (!existsSync(f)) { missing.push(name); return m; }
    const mt = MIME[name.split('.').pop().toLowerCase()];
    if (!mt) throw new Error('知らないファイルの形: ' + name);
    used.add(name);
    return `data:${mt};base64,` + readFileSync(f).toString('base64');
  });
  if (missing.length) throw new Error('assets/ にないファイル: ' + missing.join(', '));
  if (!/^<!doctype html>\r?\n/i.test(out)) throw new Error('src/page.html の1行目は <!doctype html> にする');
  const nl = out.indexOf('\n') + 1;
  out = out.slice(0, nl) + HEADER + '\n' + out.slice(nl);
  return { out, used };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const check = process.argv.includes('--check');
  const { out, used } = build(readFileSync(SRC, 'utf8'));
  const unused = readdirSync(ASSETS).filter(f => !used.has(f));
  if (unused.length) console.log(`使っていない assets（${unused.length}）: ${unused.join(' ')}`);
  if (check) {
    const same = existsSync(OUT) && readFileSync(OUT, 'utf8') === out;
    console.log(same ? 'index.html は src/page.html と assets/ から作ったものと同じ' : 'index.html がずれている：node tools/build/build.mjs で作りなおす');
    process.exit(same ? 0 : 1);
  }
  writeFileSync(OUT, out);
  console.log(`index.html を作った（${(Buffer.byteLength(out) / 1024).toFixed(0)}KB・絵 ${used.size}こ）`);
}
