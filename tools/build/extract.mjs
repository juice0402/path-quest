// 埋めこみの絵（data:…;base64,…）を games/path-quest/assets/ のファイルに出して、ページには {{asset:名前}} を残す。Node の標準だけ。
//
//   node tools/build/extract.mjs                      src/page.html の中の埋めこみを assets/ に出す（何度走らせてもよい）
//   node tools/build/extract.mjs games/path-quest/index.html
//                                                     index.html から src/page.html を作りなおす（見出しの行は外す）
//
// 名前は置き場所から：CSS の --ui-plank:url(…) → ui-plank.webp、<symbol id="a-imp"><image href=…> → a-imp.webp、
// const CR={"bee":"…"} → cr-bee.webp。同じ名前のファイルがあって中身がちがえば上書きする（絵を作りなおしたとき）。
// 古い絵の道具（tools/ui/build_ui_1104.py など、base64 を直接ページに入れるもの）は src/page.html に当ててから、これを走らせる。
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, join, dirname } from 'node:path';
import { SRC, ASSETS, HEADER } from './build.mjs';

const EXT = { 'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/svg+xml': 'svg', 'audio/mpeg': 'mp3', 'audio/ogg': 'ogg', 'audio/wav': 'wav', 'audio/mp4': 'm4a' };
const DATA = /data:([a-z]+\/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)/g;

function nameFor(text, at, b64) {
  const pre = text.slice(Math.max(0, at - 400), at);
  let m;
  if ((m = pre.match(/--([\w-]+):url\(["']?$/))) return m[1];
  if ((m = pre.match(/<symbol id="([^"]+)"[^>]*><image [^>]*href="$/))) return m[1];
  if ((m = pre.match(/"([^"\\]+)":"$/))) {
    const line = text.slice(text.lastIndexOf('\n', at) + 1, at);
    const objs = [...line.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\{/g)];
    return (objs.length ? objs[objs.length - 1][1].toLowerCase() + '-' : '') + m[1];
  }
  return 'img-' + createHash('sha1').update(b64).digest('hex').slice(0, 10);
}

const inPath = resolve(process.argv[2] || SRC);
let text = readFileSync(inPath, 'utf8');
if (text.includes(HEADER + '\n')) text = text.replace(HEADER + '\n', '');
mkdirSync(ASSETS, { recursive: true });
const taken = new Map(), lower = new Map();
let fresh = 0, changed = 0, same = 0;
text = text.replace(DATA, (whole, mime, b64, at) => {
  const ext = EXT[mime];
  if (!ext) return whole;
  const bytes = Buffer.from(b64, 'base64');
  if (bytes.toString('base64') !== b64) throw new Error('base64 の形がふつうでない（作りなおすと中身が変わる）: ' + whole.slice(0, 60));
  let base = nameFor(text, at, b64).replace(/[^A-Za-z0-9._-]/g, '_'), name = `${base}.${ext}`;
  for (let i = 2; (taken.has(name) && !taken.get(name).equals(bytes)) || (lower.has(name.toLowerCase()) && lower.get(name.toLowerCase()) !== name); i++) name = `${base}-${i}.${ext}`;
  if (!taken.has(name)) {
    taken.set(name, bytes); lower.set(name.toLowerCase(), name);
    const f = join(ASSETS, name);
    if (!existsSync(f)) { writeFileSync(f, bytes); fresh++; }
    else if (!readFileSync(f).equals(bytes)) { writeFileSync(f, bytes); changed++; }
    else same++;
  }
  return `{{asset:${name}}}`;
});
mkdirSync(dirname(SRC), { recursive: true });
writeFileSync(SRC, text);
console.log(`src/page.html を書いた（${(Buffer.byteLength(text) / 1024).toFixed(0)}KB）・assets：新しい ${fresh}・上書き ${changed}・同じ ${same}`);
