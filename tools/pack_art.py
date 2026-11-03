"""Pack cut sprites into a JS object of WebP data URIs.

usage: python3 pack_art.py OUT.js name=path:maxside[:q] ...
writes: const ART={name:{u:'data:image/webp;base64,…',w:…,h:…},…};
w/h are the packed pixel size, so the game can keep each sprite's aspect.
"""
import sys, base64, io, json
from PIL import Image

def main():
    out = sys.argv[1]; art = {}
    total = 0
    for spec in sys.argv[2:]:
        name, rest = spec.split('=', 1)
        parts = rest.split(':')
        path, side = parts[0], int(parts[1]); q = int(parts[2]) if len(parts) > 2 else 82
        im = Image.open(path).convert('RGBA')
        s = side / max(im.size)
        if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6)
        b = buf.getvalue(); total += len(b)
        art[name] = {'u': 'data:image/webp;base64,' + base64.b64encode(b).decode(), 'w': im.width, 'h': im.height}
        print(f'{name}: {im.width}x{im.height} {len(b)//1024}KB')
    with open(out, 'w') as f:
        f.write('const ART=' + json.dumps(art, separators=(',', ':')) + ';\n')
    print('total', total // 1024, 'KB')

if __name__ == '__main__':
    main()
