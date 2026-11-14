#!/usr/bin/env python3
"""Build a self-contained HTML cluster map (open it in a browser, hover a dot for the details).
Usage: python cluster_map.py pages.ndjson table.tsv out.html [--title "Site name"] [--note "filter and date note"]
pages.ndjson: one JSON object per line with "Address" and "content" (the crawler's visible-text export).
table.tsv columns (header row required): URL, Group, Group type, Role in group, Folder, Decision, Action, Target,
  Clicks, Impressions, Sessions, Text similarity to top performer  (extra columns are ignored, blanks allowed).
Layout: TF-IDF on boilerplate-stripped page text, SVD to 50 dimensions, t-SNE to 2D (the same family of method as the
Screaming Frog Content Cluster Diagram, which runs t-SNE on its embeddings). Needs numpy and scikit-learn.
Crawled values, the title and the note are HTML-escaped before they reach the page."""
import sys, json, csv, collections, html, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE

def main():
    a = sys.argv[1:]
    if len(a) < 3: print(__doc__); sys.exit(2)
    title = a[a.index('--title') + 1] if '--title' in a else 'Content cluster map'
    note = a[a.index('--note') + 1] if '--note' in a else ''
    rows = list(csv.DictReader(open(a[1], encoding='utf-8'), delimiter='\t'))
    txt = {}
    for l in open(a[0]):
        r = json.loads(l); txt.setdefault(r['Address'], r['content'])
    rows = [r for r in rows if r['URL'] in txt]
    lc = collections.Counter()
    for r in rows:
        for ln in set(x.strip() for x in txt[r['URL']].split('\n') if x.strip()): lc[ln] += 1
    bp = {l for l, c in lc.items() if c >= max(8, int(0.04 * len(rows)))}
    docs = [' '.join(x.strip() for x in txt[r['URL']].split('\n') if x.strip() and x.strip() not in bp) for r in rows]
    X = TfidfVectorizer(sublinear_tf=True, stop_words='english', min_df=2, max_df=0.5, ngram_range=(1, 2), max_features=100000).fit_transform(docs)
    Z = TruncatedSVD(50, random_state=0).fit_transform(X)
    Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9
    P = TSNE(2, perplexity=min(30, len(rows) // 4), init='pca', learning_rate='auto', random_state=0, metric='cosine').fit_transform(Z)
    P = (P - P.min(0)) / (P.max(0) - P.min(0))
    P = P + np.random.default_rng(0).normal(0, 1e-4, P.shape)
    for _ in range(80):  # spread points that sit on top of each other so each dot can be hovered
        D2 = P[:, None, :] - P[None, :, :]; dist = np.maximum(np.linalg.norm(D2, axis=2), 1e-6) + np.eye(len(P))
        push = np.where((dist < 0.011)[..., None], D2 / dist[..., None] * (0.011 - dist)[..., None] / 2, 0).sum(1)
        P = np.clip(P + push, 0, 1)
    def num(v):
        try: return float(v)
        except (TypeError, ValueError): return 0
    pts = [dict(u=r['URL'], x=round(float(P[i][0]), 4), y=round(float(P[i][1]), 4), g=r.get('Group') or '-', gt=r.get('Group type') or '',
                role=r.get('Role in group') or '', f=r.get('Folder') or '', d=r.get('Decision') or '', ac=r.get('Action') or '',
                t=r.get('Target') or '', c=num(r.get('Clicks')), i=num(r.get('Impressions')), s=num(r.get('Sessions')),
                sim=r.get('Text similarity to top performer') or '') for i, r in enumerate(rows)]
    # JSON inside a <script> tag: escape <, > and & so a crawled value cannot close the tag
    data = json.dumps(pts, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    page = TEMPLATE.replace('__DATA__', data).replace('__TITLE__', html.escape(title)).replace('__NOTE__', html.escape(note))
    open(a[2], 'w', encoding='utf-8').write(page)
    print(f'{len(pts)} pages written to {a[2]}')

TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{color-scheme:light;--bg:#fcfcfb;--panel:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--line:#e4e3de;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--ring:#0b0b0b}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--bg:#1a1a19;--panel:#242423;--ink:#fff;--ink2:#c3c2b7;--muted:#8f8e86;--line:#3a3a38;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--ring:#fff}}
:root[data-theme=dark]{color-scheme:dark;--bg:#1a1a19;--panel:#242423;--ink:#fff;--ink2:#c3c2b7;--muted:#8f8e86;--line:#3a3a38;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--ring:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:14px 16px 8px}h1{font-size:18px;margin:0 0 2px}.sub{color:var(--ink2);font-size:13px}
.bar{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;padding:8px 16px;border-bottom:1px solid var(--line)}
.bar input,.bar select,.bar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:5px 8px}
.bar #q{min-width:220px}.leg{display:flex;gap:12px;flex-wrap:wrap}.leg label{display:flex;gap:6px;align-items:center;cursor:pointer;color:var(--ink2)}
.sw{width:10px;height:10px;border-radius:50%;display:inline-block}
main{display:grid;grid-template-columns:1fr 320px;gap:0;height:calc(100vh - 150px);min-height:420px}
#wrap{position:relative;background:var(--bg)}canvas{width:100%;height:100%;display:block;cursor:crosshair}
aside{border-left:1px solid var(--line);padding:12px 14px;overflow:auto;background:var(--panel)}
aside h2{font-size:13px;margin:0 0 6px;color:var(--ink2);font-weight:600}aside .u{word-break:break-all;font-weight:600}
#tip{position:fixed;pointer-events:none;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12.5px;max-width:360px;box-shadow:0 4px 14px rgba(0,0,0,.18);display:none;z-index:5}
#tip b{word-break:break-all}#tip .k{color:var(--muted)}table{border-collapse:collapse;width:100%;font-size:12px}td,th{padding:3px 4px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:500}.mem{cursor:pointer}.mem:hover{background:var(--bg)}
footer{padding:8px 16px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
@media(max-width:860px){main{grid-template-columns:1fr;height:auto}#wrap{height:60vh}aside{border-left:0;border-top:1px solid var(--line)}}
</style></head><body>
<header><h1>__TITLE__</h1><div class="sub">Each dot is a live page. Pages close together share a topic. Hover for details, click to pin a page and list its group, scroll to zoom, drag to pan.</div></header>
<div class="bar"><input id="q" placeholder="Search URL" aria-label="Search URL">
<select id="fo" aria-label="Folder"><option value="">All folders</option></select>
<select id="gt" aria-label="Group type"><option value="">All group types</option></select>
<div class="leg" id="leg"></div><button id="rs">Reset view</button></div>
<main><div id="wrap"><canvas id="cv"></canvas></div><aside id="side"><h2>Selected page</h2><div id="sel" class="sub">Click a dot.</div></aside></main>
<div id="tip"></div>
<footer>Layout: t-SNE on TF-IDF text vectors (page text with menus and footers removed). Dot size follows impressions. Colour is the audit decision. __NOTE__</footer>
<script>
const D=__DATA__;const cs=getComputedStyle(document.documentElement);
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const COL={Remain:'--s1',Redirect:'--s2',Retire:'--s3'};
const cv=document.getElementById('cv'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
let W,H,dpr,zoom=1,ox=0,oy=0,hov=-1,pin=-1,vis=D.map(()=>true),showD={Remain:true,Redirect:true,Retire:true};
const byG={};D.forEach((p,i)=>{if(p.g!=='-')(byG[p.g]=byG[p.g]||[]).push(i)});
const fo=document.getElementById('fo'),gt=document.getElementById('gt'),q=document.getElementById('q');
[...new Set(D.map(p=>p.f))].sort().forEach(v=>fo.add(new Option(v||'(none)',v)));
[...new Set(D.map(p=>p.gt))].sort().forEach(v=>gt.add(new Option(v||'(none)',v)));
const leg=document.getElementById('leg');
Object.keys(COL).forEach(k=>{const l=document.createElement('label');l.innerHTML=`<input type="checkbox" checked data-k="${k}"><span class="sw" style="background:var(${COL[k]})"></span>${k}`;leg.appendChild(l)});
leg.onchange=e=>{showD[e.target.dataset.k]=e.target.checked;filt()};
function filt(){const s=q.value.toLowerCase();vis=D.map(p=>showD[p.d]!==false&&(!fo.value||p.f===fo.value)&&(!gt.value||p.gt===gt.value)&&(!s||p.u.toLowerCase().includes(s)));draw()}
[q,fo,gt].forEach(e=>e.oninput=filt);
function size(){dpr=devicePixelRatio||1;const r=cv.getBoundingClientRect();W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;draw()}
const pad=30;function sx(p){return pad+p.x*(W-2*pad)*zoom+ox}function sy(p){return pad+p.y*(H-2*pad)*zoom+oy}
function rad(p){return 2.5+Math.min(5,Math.sqrt(p.i)/14)}
function draw(){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
 const hi=hov>=0?hov:pin;const grp=hi>=0&&D[hi].g!=='-'?byG[D[hi].g]:null;
 D.forEach((p,i)=>{if(!vis[i])return;ctx.beginPath();ctx.arc(sx(p),sy(p),rad(p),0,6.283);ctx.fillStyle=cs.getPropertyValue(COL[p.d]||'--s1');
  ctx.globalAlpha=grp&&!grp.includes(i)?.18:.85;ctx.fill();ctx.lineWidth=1.5;ctx.strokeStyle=cs.getPropertyValue('--bg');ctx.stroke()});
 ctx.globalAlpha=1;
 if(grp){const top=grp.find(i=>D[i].role==='Top performer');ctx.strokeStyle=cs.getPropertyValue('--ring');ctx.lineWidth=1;
  grp.forEach(i=>{if(!vis[i])return;ctx.globalAlpha=.7;ctx.beginPath();ctx.arc(sx(D[i]),sy(D[i]),rad(D[i])+2,0,6.283);ctx.stroke();
   if(top!==undefined&&i!==top){ctx.globalAlpha=.4;ctx.beginPath();ctx.moveTo(sx(D[top]),sy(D[top]));ctx.lineTo(sx(D[i]),sy(D[i]));ctx.stroke();ctx.globalAlpha=1}})}
 if(hi>=0){ctx.strokeStyle=cs.getPropertyValue('--ring');ctx.lineWidth=2;ctx.beginPath();ctx.arc(sx(D[hi]),sy(D[hi]),rad(D[hi])+4,0,6.283);ctx.stroke()}}
function near(mx,my){let b=-1,bd=1e9;D.forEach((p,i)=>{if(!vis[i])return;const d=(sx(p)-mx)**2+(sy(p)-my)**2,r=Math.max(rad(p)+4,9);if(d<r*r&&d<bd){bd=d;b=i}});return b}
const n0=v=>Math.round(v).toLocaleString();
function info(p){return `<b>${esc(p.u.replace('https://www.',''))}</b><br><span class="k">Decision</span> ${esc(p.d)} · ${esc(p.ac)}${p.t?'<br><span class="k">Target</span> '+esc(p.t.replace('https://www.','')):''}<br><span class="k">Group</span> ${p.g==='-'?'none':esc(p.g)+' ('+esc(p.gt)+', '+(byG[p.g]||[]).length+' pages)'}${p.role&&p.role!=='-'?'<br><span class="k">Role</span> '+esc(p.role):''}${p.sim!==''?'<br><span class="k">Text similarity to top performer</span> '+esc(p.sim):''}<br><span class="k">Clicks</span> ${n0(p.c)} · <span class="k">Impressions</span> ${n0(p.i)} · <span class="k">Sessions</span> ${n0(p.s)}`}
cv.onmousemove=e=>{if(drag){ox+=e.movementX;oy+=e.movementY;draw();return}const r=cv.getBoundingClientRect(),i=near(e.clientX-r.left,e.clientY-r.top);
 if(i!==hov){hov=i;draw()}if(i>=0){tip.style.display='block';tip.innerHTML=info(D[i]);const x=Math.min(e.clientX+14,innerWidth-380);tip.style.left=x+'px';tip.style.top=Math.min(e.clientY+14,innerHeight-170)+'px'}else tip.style.display='none'};
cv.onmouseleave=()=>{hov=-1;tip.style.display='none';draw()};
let drag=false;cv.onmousedown=()=>{drag=true};addEventListener('mouseup',()=>{drag=false});
cv.onclick=e=>{const r=cv.getBoundingClientRect(),i=near(e.clientX-r.left,e.clientY-r.top);if(i>=0){pin=i;sel()}draw()};
cv.onwheel=e=>{e.preventDefault();const r=cv.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,z=e.deltaY<0?1.2:1/1.2,nz=Math.max(1,Math.min(40,zoom*z));
 const k=nz/zoom;ox=mx-(mx-ox)*k;oy=my-(my-oy)*k;zoom=nz;draw()};
document.getElementById('rs').onclick=()=>{zoom=1;ox=oy=0;draw()};
function sel(){const p=D[pin],m=p.g!=='-'?byG[p.g]:[pin];
 document.getElementById('sel').innerHTML=`<div class="u">${esc(p.u)}</div><div class="sub" style="margin:4px 0 8px">${info(p).split('<br>').slice(1).join('<br>')}</div><h2>Group ${p.g==='-'?'(none)':esc(p.g)+' · '+m.length+' pages'}</h2><table><tr><th>Page</th><th>Imp.</th><th>Decision</th></tr>${m.slice().sort((a,b)=>D[b].i-D[a].i).map(i=>`<tr class="mem" data-i="${i}"><td>${esc(D[i].u.replace(/^https?:\/\/[^\/]+/,'')||'/')}${D[i].role==='Top performer'?' ★':''}</td><td>${n0(D[i].i)}</td><td>${esc(D[i].d)}</td></tr>`).join('')}</table>`;
 document.querySelectorAll('.mem').forEach(r=>r.onclick=()=>{pin=+r.dataset.i;sel();draw()})}
addEventListener('resize',size);size();
</script></body></html>'''

if __name__ == '__main__': main()
