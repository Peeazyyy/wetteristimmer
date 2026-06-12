"""Download extra generated images (from extra-images.json) and store them as
WebP in site/assets/img/. Runs in CI where the image CDN is reachable."""
import json, os, io, urllib.request
from PIL import Image

m = json.load(open('scripts/extra-images.json'))
os.makedirs('site/assets/img', exist_ok=True)

for name, url in m.items():
    dest = os.path.join('site/assets/img', name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print('skip', name); continue
    data = urllib.request.urlopen(url, timeout=60).read()
    if name.lower().endswith('.webp'):
        Image.open(io.BytesIO(data)).convert('RGB').save(dest, 'WEBP', quality=82, method=6)
    else:
        open(dest, 'wb').write(data)
    print('ok', name, os.path.getsize(dest), 'bytes')
