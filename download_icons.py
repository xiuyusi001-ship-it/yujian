"""Fetch actual favicons; failed sites are reported, never replaced by fake images."""
import concurrent.futures as cf, io, json, hashlib, os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'icons'; OUT.mkdir(exist_ok=True)
items=json.loads((ROOT/'icon-manifest.json').read_text(encoding='utf-8'))
Image.MAX_IMAGE_PIXELS=4_000_000

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; YujianIconFetcher/1.1)'}),timeout=8) as r:
        data=r.read(1_000_001)
    if len(data)>1_000_000: raise ValueError('image too large')
    with Image.open(io.BytesIO(data)) as im:
        if min(im.size)<16: raise ValueError('icon too small')
        im=im.convert('RGBA'); im.thumbnail((64,64),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(64,64)); canvas.paste(im,((64-im.width)//2,(64-im.height)//2))
        if not canvas.getbbox(): raise ValueError('empty icon')
        buf=io.BytesIO(); canvas.save(buf,format='PNG',optimize=True); return buf.getvalue()

def work(host):
    dest=OUT/(host+'.png')
    if dest.exists(): return {'host':host,'status':'existing','sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    sources=[f'https://{host}/favicon.ico',f'https://api.iowen.cn/favicon/{quote(host)}.png',f'https://favicon.cccyun.cc/{quote(host)}',f'https://www.google.com/s2/favicons?domain={quote(host)}&sz=64']
    for src in sources:
        try:
            data=fetch(src); dest.write_bytes(data)
            return {'host':host,'status':'downloaded','source':src,'sha256':hashlib.sha256(data).hexdigest()}
        except Exception: pass
    return {'host':host,'status':'failed'}

with cf.ThreadPoolExecutor(max_workers=12) as pool:
    rows=list(pool.map(work,sorted({x['host'] for x in items})))
# Identify identical files for review (some sites share genuine brand icons; others may be generic).
groups={}
for row in rows:
    if 'sha256' in row: groups.setdefault(row['sha256'],[]).append(row['host'])
for row in rows:
    if len(groups.get(row.get('sha256'),[]))>1: row['review']='identical image across multiple domains; verify visually'
(ROOT/'icon-download-report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Available: {sum(r['status']!='failed' for r in rows)}/{len(rows)}; inspect icon-download-report.json for failures and duplicates.")
