// Downloads the AI-generated images listed in generated-images.json
// into site/assets/img/ (runs in CI where the CDN is reachable).
import fs from 'fs';
import path from 'path';

const map = JSON.parse(fs.readFileSync('scripts/generated-images.json', 'utf8'));
const dir = 'site/assets/img';
fs.mkdirSync(dir, { recursive: true });

for (const [name, url] of Object.entries(map)) {
  const dest = path.join(dir, name);
  if (fs.existsSync(dest) && fs.statSync(dest).size > 0) continue;
  const res = await fetch(url);
  if (!res.ok) {
    console.log(`FAILED ${name}: HTTP ${res.status}`);
    continue;
  }
  fs.writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
  console.log(`ok ${name}`);
}
