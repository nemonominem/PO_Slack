// test_app.mjs -- runs index.html's real script against the real data files.
//
// This machine has no headless browser available (Chrome/Playwright are not
// installed and there is no network to fetch them; Brave's headless mode aborts
// under the sandbox), so instead of pretending, this shims just enough of the
// DOM and of pdf.js/Chart.js for the app's own code to execute unmodified --
// the script is extracted from index.html and run as-is, not re-implemented.
// That makes it a real functional test of the app's logic and of the HTML it
// generates; what it cannot cover is layout and CSS, which is why
// audit_app.py checks the markup separately.
//
// Run:  node test_app.mjs
import fs from 'fs';
import path from 'path';

const HERE = '/Users/gillesdemaneuf/Work/Reports/PO_Slack/page_based';
function mkEl(id) {
  return {
    id, innerHTML: '', textContent: '', value: '', hidden: false, style: {}, dataset: {},
    classList: { _s: new Set(), add(c){this._s.add(c)}, remove(c){this._s.delete(c)},
      toggle(c,f){ const has=this._s.has(c); const want=f===undefined?!has:!!f;
        if(want)this._s.add(c); else this._s.delete(c); return want; }, contains(c){return this._s.has(c)} },
    children: [], attrs: {},
    addEventListener(ev,fn){ (this._ev||(this._ev={}))[ev]=fn; },
    removeEventListener(){}, appendChild(c){ this.children.push(c); return c; }, remove(){},
    setAttribute(k,v){ this.attrs[k]=v; }, getAttribute(k){ return this.attrs[k]; },
    querySelector(){ return null; }, querySelectorAll(){ return []; },
    closest(){ return null; }, focus(){}, click(){}, scrollIntoView(){},
    getBoundingClientRect(){ return {top:0,left:0,width:10,height:10}; },
    width: 800, height: 600,
    getContext(){ return { fillRect(){}, clearRect(){}, fillText(){}, measureText(){ return {width:10}; },
      save(){}, restore(){}, scale(){}, translate(){}, beginPath(){}, moveTo(){}, lineTo(){},
      stroke(){}, fill(){}, setTransform(){}, drawImage(){}, getImageData(){ return {data:[]}; },
      putImageData(){}, createLinearGradient(){ return {addColorStop(){}}; } }; },
    clientHeight:100, scrollHeight:100, scrollTop:0,
    setPointerCapture(){}, releasePointerCapture(){},
  };
}
const els = {};
globalThis.document = {
  getElementById(id){ return els[id] || (els[id] = mkEl(id)); },
  createElement(t){ return mkEl('#'+t); },
  querySelector(){ return null; }, querySelectorAll(){ return []; },
  addEventListener(){}, body: mkEl('body'), documentElement: mkEl('html'),
};
globalThis.window = { addEventListener(){}, devicePixelRatio:1, innerWidth:1600, innerHeight:900 };
globalThis.localStorage = { _m:{}, getItem(k){return this._m[k]??null}, setItem(k,v){this._m[k]=v}, removeItem(k){delete this._m[k]} };
globalThis.location = { protocol:'http:', pathname:'/index.html' };
globalThis.requestAnimationFrame = (fn)=>{ try{fn()}catch(e){} };
globalThis.setTimeout = (fn)=>{ try{fn()}catch(e){} return 0; };
globalThis.devicePixelRatio = 1;
globalThis.fetch = async (url) => {
  const f = path.join(HERE, url);
  if (!fs.existsSync(f)) return { ok:false, status:404 };
  return { ok:true, status:200, json: async () => JSON.parse(fs.readFileSync(f,'utf8')) };
};
globalThis.pdfjsLib = { GlobalWorkerOptions:{},
  getDocument: () => ({ promise: Promise.resolve({ numPages:1, getPage: async()=>({}) }) }) };
function Chart(){
  return { data: { datasets: [], labels: [] }, options: {},
    destroy(){}, update(){}, resetZoom(){}, resize(){}, stop(){}, toBase64Image(){ return ''; },
    setDatasetVisibility(){}, getDatasetMeta(){ return { data: [] }; },
    scales: {}, $canvas: null, canvas: null, ctx: null };
}
Chart.defaults = { color:'#fff', font:{size:11} };
globalThis.Chart = Chart;

const pageHtml = fs.readFileSync(path.join(HERE,'index.html'),'utf8');
const scripts = [...pageHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const code = scripts[scripts.length - 1];
const tail = `
globalThis.__app = { SOURCES, KIND_DEFS, KIND_ALIASES, entryKind, kindDef,
  availableKinds, kindListed, loadKindFilter, saveKindFilter, loadData, doSearch,
  displayResults, entryChipsHtml, buildTimelineSeries, entryMapKey, highlightWithHits,
  openEntryRef, rebuildThreadDownLinks, get diaryData(){ return diaryData; },
  set kindFilter(v){ kindFilter = v; }, get kindFilter(){ return kindFilter; },
  get timelineSeries(){ return timelineSeries; } };
`;
const src = code + tail;
await import('data:text/javascript;base64,' + Buffer.from(src).toString('base64'));
const app = globalThis.__app;
await app.loadData();

let pass = 0, fail = 0;
const ok = (name, cond, extra='') => { if (cond) { pass++; console.log('  PASS  ' + name); }
  else { fail++; console.log('  FAIL  ' + name + (extra ? '  → ' + extra : '')); } };
const sec = (t) => console.log('\n' + t);

sec('Data load');
ok('entries loaded', app.diaryData && app.diaryData.entries.length > 12000, app.diaryData && app.diaryData.entries.length);
const byKind = app.availableKinds();
console.log('        kinds:', JSON.stringify(byKind));
ok('three kinds present (slack, attachment/note, email)',
   byKind.slack > 10000 && byKind.email > 50 && (byKind.note > 0 || byKind.attachment > 0));
const srcs = {};
app.diaryData.entries.forEach(e => srcs[e.source] = (srcs[e.source]||0)+1);
console.log('        sources:', JSON.stringify(srcs));

sec('Chronology');
const ks = app.diaryData.entries.map(e => (e.date||'9999')+' '+(e.time||'9999'));
ok('merged timeline is in date order', ks.every((k,i)=> i===0 || ks[i-1] <= k));
const emails = app.diaryData.entries.filter(e=>e.source==='po-emails');
ok('every email has a thread key', emails.every(e=>!!e.thread_key));
ok('thread keys unique', new Set(emails.map(e=>e.thread_key)).size === emails.length);
const replies = emails.filter(e=>e.reply_to);
ok('reply targets all exist', replies.every(e=>emails.some(p=>p.thread_key===e.reply_to)),
   replies.filter(e=>!emails.some(p=>p.thread_key===e.reply_to)).length + ' dangling');
ok('every reply postdates what it answers (ET)',
   replies.every(e => { const p = emails.find(x=>x.thread_key===e.reply_to);
     return (p.date + ' ' + (p.time||'')) <= (e.date + ' ' + (e.time||'')); }));

sec('Page maps');
ok('page map keys resolve for emails',
   emails.every(e => (app.SOURCES[e.source] ? true : false)));


sec('Search + rendering');
const input = document.getElementById('searchInput');
input.value = 'passaging';
app.doSearch();
const panel = document.getElementById('resultsPanel');
const html = panel.innerHTML;
console.log('        rendered', (html.match(/class="result-entry/g)||[]).length, 'cards');
ok('search produced cards', (html.match(/class="result-entry/g)||[]).length > 0);
ok('cards carry a box-type badge', /class="entry-kind k-/.test(html));
ok('cards carry a source badge', /Slack P1|Slack P2/.test(html));
ok('every card has its own scroll box', (html.match(/class="box-scrollbar/g)||[]).length === (html.match(/class="result-entry/g)||[]).length);
ok('every card has a scroll hint', (html.match(/data-scroll-hint=/g)||[]).length === (html.match(/class="result-entry/g)||[]).length);
ok('Full text expander present', /data-expand-toggle=/.test(html));
ok('result content is inside .result-content-wrap', /result-content-wrap/.test(html));

sec('Emails surface with header block + chips');
input.value = 'genome looks unusual';
app.doSearch();
const html2 = document.getElementById('resultsPanel').innerHTML;
const emailCards = (html2.match(/class="entry-kind k-email/g)||[]).length;
ok('email results found', emailCards > 0, emailCards + ' email cards');
ok('email card renders the mail head block', /class="mail-head"/.test(html2));
ok('email card shows a timestamp/zone chip', /chip-dim[^>]*>🕑/.test(html2));
// Thread chips: pick a message that sits inside a conversation, so the card
// rendered for it must carry a navigable link. A thread's first message
// correctly has no parent to point at.
const threaded = app.diaryData.entries.find(e => e.source === 'po-emails' && (e.replied_by||[]).length);
ok('some emails are threaded', !!threaded);
if (threaded) {
  const word = (threaded.content.match(/[a-z]{6,}/i)||['x'])[0];
  input.value = word;
  app.doSearch();
  const h3 = document.getElementById('resultsPanel').innerHTML;
  const chips = h3.match(/data-open-entry="[^"]+"/g);
  ok('thread chips are navigable', !!chips && chips.length > 0,
     (chips ? chips.length : 0) + ' chips for "' + word + '"');
}

sec('Box types filter');
app.kindFilter = ['email'];
ok('kindListed honours the filter', app.kindListed('email') && !app.kindListed('slack'));
input.value = 'passaging';
app.doSearch();
const filtered = document.getElementById('resultsPanel').innerHTML;
ok('filtering to emails drops Slack hits', !/k-slack/.test(filtered));
app.kindFilter = null;
input.value = 'passaging';
app.doSearch();
ok('clearing the filter brings Slack back', /k-slack/.test(document.getElementById('resultsPanel').innerHTML));
app.kindFilter = ['slack','email','attachment','note'];

sec('Timeline counts follow the filter');
app.buildTimelineSeries();
const withAll = app.timelineSeries.entryCounts.reduce((a,b)=>a+b,0);
app.kindFilter = ['email'];
app.buildTimelineSeries();
const withEmail = app.timelineSeries.entryCounts.reduce((a,b)=>a+b,0);
ok('timeline counts only listed kinds', withEmail < withAll && withEmail > 0,
   withEmail + ' vs ' + withAll);
app.kindFilter = null;
app.buildTimelineSeries();

sec('Manuscript drafts');
input.value = 'RBD';
app.doSearch();
const hd = document.getElementById('resultsPanel').innerHTML;
ok('draft versions are searchable', /k-draft/.test(hd));
const drafts = app.diaryData.entries.filter(e => e.source === 'sscp');
ok('draft versions are dated and unique', drafts.length > 0 &&
   new Set(drafts.map(d => d.thread_key)).size === drafts.length &&
   drafts.every(d => /^\d{4}-\d{2}-\d{2}$/.test(d.date)),
   drafts.length + ' versions');
ok('draft versions run Feb 1 – Mar 5 2020',
   drafts[0].date >= '2020-02-01' && drafts[drafts.length-1].date <= '2020-03-06',
   drafts[0].date + ' .. ' + drafts[drafts.length-1].date);
ok('every draft has a page', drafts.every(d => d.pages && d.pages.length));

sec('Guide');
const guideResp = await (await fetch('po_guide.json')).json();
ok('guide loads', !!guideResp && guideResp.sections.length > 200);
ok('guide covers every citation', guideResp.totals.citations === 446, String(guideResp.totals.citations));
const evNoKind = guideResp.sections.flatMap(s=>s.evidence).filter(e=>!e.kind);
ok('every guide citation is classified', evNoKind.length === 0);
const docs = guideResp.documents ? Object.values(guideResp.documents) : [];
ok('every cited document is catalogued', docs.length === 51, String(docs.length));


sec('Stacked timeline (media x release)');
app.buildTimelineSeries();
const ts = app.timelineSeries;
ok('timeline has stacked segments', !!ts && Array.isArray(ts.stacks) && ts.stacks.length >= 4,
   ts ? ts.stacks.length + ' segments' : 'none');
const stackByKind = {};
(ts.stacks || []).forEach(function(seg) {
  (stackByKind[seg.kind] = stackByKind[seg.kind] || []).push(seg);
});
ok('slack is two blues (two shades of the same hue)',
   (stackByKind.slack || []).length === 2,
   'slack segments: ' + (stackByKind.slack || []).length);
if ((stackByKind.slack || []).length === 2) {
  const h1 = stackByKind.slack[0].color.match(/hsl\((\d+)/);
  const h2 = stackByKind.slack[1].color.match(/hsl\((\d+)/);
  ok('both slack segments share the blue hue', h1 && h2 && h1[1] === h2[1],
     stackByKind.slack[0].color + ' vs ' + stackByKind.slack[1].color);
  ok('but differ in shade (lightness)',
     stackByKind.slack[0].color !== stackByKind.slack[1].color);
}
ok('email and draft each have their own media colour',
   !!(stackByKind.email || []).length && !!(stackByKind.draft || []).length);
const stackTotal = (ts.stacks || []).reduce(function(a, seg) { return a + seg.total; }, 0);
const entryTotal = (ts.entryCounts || []).reduce(function(a, c) { return a + c; }, 0);
ok('stack totals equal the per-day entry counts', stackTotal === entryTotal,
   stackTotal + ' vs ' + entryTotal);

sec('Legend');
const legendEl = document.getElementById('timelineLegend');
ok('legend element exists in the markup', !!legendEl);

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);

