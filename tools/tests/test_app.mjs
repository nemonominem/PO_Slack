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
import { fileURLToPath } from 'node:url';

const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../page_based');
function mkEl(id) {
  const el = {
    innerHTML: '', textContent: '', value: '', hidden: false, style: {}, dataset: {},
    classList: { _s: new Set(), add(c){this._s.add(c)}, remove(c){this._s.delete(c)},
      toggle(c,f){ const has=this._s.has(c); const want=f===undefined?!has:!!f;
        if(want)this._s.add(c); else this._s.delete(c); return want; }, contains(c){return this._s.has(c)} },
    children: [], attrs: {},
    addEventListener(ev,fn){ (this._ev||(this._ev={}))[ev]=fn; },
    removeEventListener(){}, appendChild(c){ this.children.push(c); c.parentNode=this; return c; },
    remove(){ if (this.id && els[this.id] === this) delete els[this.id];
      if (this.parentNode) this.parentNode.children=this.parentNode.children.filter(c=>c!==this); },
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
  let elementId = id;
  Object.defineProperty(el, 'id', { get(){ return elementId; }, set(value){
    elementId=value;
    if (value) els[value]=el;
  }});
  if (id) els[id]=el;
  return el;
}
const els = {};
globalThis.document = {
  getElementById(id){
    if ((id === 'kindFilterPanel' || id === 'authorFilterPanel') && !els[id]) return null;
    return els[id] || (els[id] = mkEl(id));
  },
  createElement(t){ return mkEl('#'+t); },
  querySelector(){ return null; }, querySelectorAll(){ return []; },
  addEventListener(){}, body: mkEl('body'), documentElement: mkEl('html'),
};
globalThis.window = { addEventListener(){}, devicePixelRatio:1, innerWidth:1600, innerHeight:900 };
globalThis.getComputedStyle = () => ({ getPropertyValue(){ return ''; } });
globalThis.localStorage = { _m:{}, getItem(k){return this._m[k]??null}, setItem(k,v){this._m[k]=v}, removeItem(k){delete this._m[k]} };
globalThis.getComputedStyle = () => ({ getPropertyValue(){ return ''; } });
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
  getDocument: () => ({ promise: Promise.resolve({ numPages:1, getPage: async()=>({
    getViewport: ({scale}) => ({ width:612*scale, height:792*scale }),
    render: () => ({ promise: Promise.resolve(), cancel(){} }),
  }) }) }) };
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
const code = scripts.join('\n');
const tail = `
globalThis.__app = { SOURCES, KIND_DEFS, KIND_ALIASES, entryKind, kindDef,
  availableKinds, kindListed, loadKindFilter, saveKindFilter, loadData, doSearch,
  availableAuthors, entryAuthor, authorListed, entryVisible, filterEntries,
  displayResults, entryChipsHtml, threadMsgHtml, chipRefLabel, buildTimelineSeries, renderTimelineLegend, entryMapKey, highlightWithHits,
  rebuildSlackReplyAuthors, slackReplyMarkerInfo, slackReplyChipsHtml, stripSlackReplyChrome,
  formatEntryTime, setThreadFilter, setRedactionFilter, entryRedactionClass,
  buildKindFilterPanel, buildAuthorFilterPanel,
  toggleKindFilterPanel, toggleAuthorFilterPanel,
  clearSearch,
  openEntryRef, rebuildThreadDownLinks, KIND_HUE, kindColor, guideDocToSource,
  guideCitationLabel,
  toggleBookmark, isBookmarked, removeBookmark, openBookmark, renderBookmarks,
  bookmarksPayload, bmAppFor, refreshBookmarkToggles, openEntryByBmKey,
  get bookmarks(){ return bookmarks; },
  set bookmarks(v){ bookmarks = v; },
  get diaryData(){ return diaryData; },
  get browseMode(){ return browseMode; },
  get lastSearchResults(){ return lastSearchResults; },
  get threadFilter(){ return threadFilter; },
  get redactionFilter(){ return redactionFilter; },
  set kindFilter(v){ kindFilter = v; }, get kindFilter(){ return kindFilter; },
  set authorFilter(v){ authorFilter = v; }, get authorFilter(){ return authorFilter; },
  get timelineSeries(){ return timelineSeries; },
  get pageMaps(){ return pageMaps; } };
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
app.renderTimelineLegend();
const timelineLegendHtml = document.getElementById('timelineLegend').innerHTML;
const p1SourceChip = timelineLegendHtml.indexOf('Rand Paul - Slack P1, 1,329 items');
const p2SourceChip = timelineLegendHtml.indexOf('Rand Paul - Slack P2, 11,348 items');
ok('timeline source chips list Slack P1 before P2 with plain comma-formatted item totals',
   p1SourceChip >= 0 && p2SourceChip > p1SourceChip &&
   !/<b>[^<]*items/.test(timelineLegendHtml) &&
   /Rand Paul - Slack P1, 1,329 items/.test(timelineLegendHtml));

ok('Part 1 viewer uses the clean independent OCR PDF',
   /part1:\s*\{[\s\S]*?pdf:\s*'other_sources\/Proximal_Origin_Slack_OCRd\.pdf'/.test(pageHtml));
ok('entries loaded', app.diaryData && app.diaryData.entries.length > 12000, app.diaryData && app.diaryData.entries.length);
const searchInput = document.getElementById('searchInput');
const initialBrowse = window._searchResults || [];
const initialPanelHtml = document.getElementById('resultsPanel').innerHTML;
ok('first load browses entries with the default all-content filters',
   app.browseMode && !app.lastSearchResults && app.kindFilter === null &&
   app.authorFilter === null && app.threadFilter === null && app.redactionFilter === null &&
   document.getElementById('redactionFilter').value === 'all' &&
   /<option value="all">All Messages<\/option>/.test(pageHtml) &&
   /<option value="partial">Partly Redacted<\/option>/.test(pageHtml) &&
   /<option value="full">Fully Redacted<\/option>/.test(pageHtml) &&
   app.filterEntries(app.diaryData.entries).length === app.diaryData.entries.length &&
   initialBrowse.length > 0 && initialBrowse.length < app.diaryData.entries.length &&
   initialBrowse.every(r => app.entryVisible(r.entry)) &&
   searchInput.value === '' &&
   initialPanelHtml.includes('class="result-entry') &&
   !initialPanelHtml.includes('Search the P.O. record'));
ok('filter panels start closed and remain closed on background rebuild',
   !!document.getElementById('kindFilterPanel')?.hidden &&
   !!document.getElementById('authorFilterPanel')?.hidden);
app.toggleKindFilterPanel();
app.toggleAuthorFilterPanel();
ok('direct toolbar interaction opens both filter panels',
   !document.getElementById('kindFilterPanel').hidden &&
   !document.getElementById('authorFilterPanel').hidden);
app.toggleKindFilterPanel();
app.toggleAuthorFilterPanel();
app.buildKindFilterPanel();
app.buildAuthorFilterPanel();
ok('timeline-checkbox-style filter rebuild does not open toolbar panels',
   !!document.getElementById('kindFilterPanel').hidden &&
   !!document.getElementById('authorFilterPanel').hidden);
app.toggleKindFilterPanel();
app.buildKindFilterPanel();
ok('rebuilding an actively used toolbar filter keeps that dropdown open',
   !document.getElementById('kindFilterPanel').hidden &&
   !!document.getElementById('authorFilterPanel').hidden);
app.toggleKindFilterPanel();
searchInput.value = 'furin';
app.doSearch();
ok('explicit search still shows matching results',
   !app.browseMode && app.lastSearchResults && app.lastSearchResults.length > 0);
app.clearSearch();
ok('clearing search returns to filtered content browsing',
   app.browseMode && !app.lastSearchResults && window._searchResults.length > 0 &&
   document.getElementById('resultsPanel').innerHTML.includes('class="result-entry') &&
   !document.getElementById('resultsPanel').innerHTML.includes('Search the P.O. record'));
app.kindFilter = ['email'];
app.authorFilter = ['Jeremy Farrar'];
app.clearSearch();
ok('browse results honor non-default source and author filters',
   window._searchResults.length > 0 &&
   window._searchResults.every(r => app.entryKind(r.entry) === 'email' &&
     app.entryAuthor(r.entry) === 'Jeremy Farrar'));
app.kindFilter = null;
app.authorFilter = null;
app.clearSearch();
const part1 = app.diaryData.entries.filter(e => e.source === 'part1');
const part1Redactions = part1.filter(e => e.redaction_count);
const fullRedactions = part1Redactions.filter(e => app.entryRedactionClass(e) === 'full');
const partialRedactions = part1Redactions.filter(e => app.entryRedactionClass(e) === 'partial');
const estimatedRedactions = fullRedactions.filter(e => e.time);
const estimatedExample = estimatedRedactions.find(e => e.time === '13:36');
ok('timed standalone redactions have estimated placement metadata',
   estimatedRedactions.length === 14 && estimatedRedactions.every(e => e.time_estimated === true) &&
   fullRedactions.filter(e => !e.time).every(e => !e.time_estimated));
ok('estimated placement labels appear in card, stamp, thread and hit navigation',
   !!estimatedExample && app.formatEntryTime(estimatedExample) === '13:36 ET (estimated)' &&
   app.entryChipsHtml(estimatedExample).includes('13:36 ET (estimated)') &&
   !app.entryChipsHtml(estimatedExample).includes('Timestamp as printed') &&
   app.threadMsgHtml({...estimatedExample, thread_key:'test|estimated'}).includes('13:36 ET (estimated)'));
app.displayResults([{entry:estimatedExample, idx:estimatedExample.idx, hits:1, hitPositions:[]}], '', {autoSelect:false});
const estimatedCard = document.getElementById('resultsPanel').innerHTML;
ok('estimated time is visible in both card header and hit label',
   (estimatedCard.match(/13:36 ET \(estimated\)/g) || []).length === 3);
ok('estimated stamp is not labelled twice',
   !app.entryChipsHtml({...estimatedExample, stamp_line:'13:36 ET (estimated)'}).includes('(estimated) (estimated)'));
ok('source-visible partial redaction times are not estimated',
   partialRedactions.every(e => !e.time_estimated && !app.formatEntryTime(e).includes('(estimated)') &&
     !app.entryChipsHtml(e).includes('(estimated)')));
ok('all 90 Part 1 rectangles are represented', part1Redactions.reduce((n, e) => n + e.redaction_count, 0) === 90,
   part1Redactions.reduce((n, e) => n + e.redaction_count, 0) + ' annotations');
ok('standalone redactions have a synthetic Redacted sender',
   part1.filter(e => e.sender === 'Redacted' && e.content === '[Redacted]').length === 76);
ok('embedded redactions remain in their source message text',
   part1.filter(e => e.sender !== 'Redacted').reduce((n, e) => n + (e.redaction_count || 0), 0) === 14);
ok('embedded redactions retain source-verified times',
   part1.filter(e => e.sender !== 'Redacted' && e.redaction_count).every(e => !!e.time));
ok('redaction classification uses annotation metadata and author identity, not inferred dates',
   fullRedactions.length === 76 && partialRedactions.length === 12 &&
   fullRedactions.every(e => app.entryAuthor(e) === 'Redacted' && !!e.date) &&
   partialRedactions.every(e => app.entryAuthor(e) !== 'Redacted' && !!e.date) &&
   app.entryRedactionClass({sender:'Redacted', date:'2020-02-01'}) === null);
app.kindFilter = ['slack'];
app.authorFilter = null;
app.setRedactionFilter('partial');
const partlyFiltered = app.filterEntries(app.diaryData.entries);
const partlyRendered = window._searchResults || [];
ok('Partly Redacted selects only known-author annotated messages',
   app.redactionFilter === 'partial' && partlyFiltered.length === 12 &&
   partlyFiltered.every(e => app.entryRedactionClass(e) === 'partial') &&
   partlyRendered.length === 12 &&
   partlyRendered.every(r => app.entryRedactionClass(r.entry) === 'partial'));
app.setRedactionFilter('full');
const fullyFiltered = app.filterEntries(app.diaryData.entries);
const fullyRendered = window._searchResults || [];
ok('Fully Redacted selects synthetic unknown-author annotations despite placement dates',
   app.redactionFilter === 'full' && fullyFiltered.length === 76 &&
   fullyFiltered.every(e => app.entryRedactionClass(e) === 'full') &&
   fullyRendered.length === 76 &&
   fullyRendered.every(r => app.entryRedactionClass(r.entry) === 'full') &&
   localStorage.getItem('poSlackRedactionFilter') === 'full');
app.authorFilter = ['Redacted'];
ok('Authors=Redacted intersects with Fully Redacted as expected',
   app.filterEntries(app.diaryData.entries).length === 76);
app.setThreadFilter('side');
ok('Authors=Redacted plus Side threads correctly has no matching redaction entries',
   app.filterEntries(app.diaryData.entries).length === 0);
app.setThreadFilter('all');
app.authorFilter = null;
app.setRedactionFilter('all');
const allRedactionBrowse = window._searchResults || [];
ok('All Messages restores ordinary browsing after redaction filtering',
   app.redactionFilter === null && app.browseMode &&
   allRedactionBrowse.length > 0 && allRedactionBrowse.length < app.diaryData.entries.length &&
   allRedactionBrowse.every(r => app.entryVisible(r.entry)) &&
   allRedactionBrowse.some(r => app.entryRedactionClass(r.entry) !== 'full') &&
   localStorage.getItem('poSlackRedactionFilter') === null);
searchInput.value = 'redaction-filter-no-match-probe';
app.doSearch();
app.setRedactionFilter('full');
ok('redaction changes preserve an explicit search with zero matches',
   searchInput.value === 'redaction-filter-no-match-probe' &&
   app.lastSearchResults && app.lastSearchResults.length === 0);
app.clearSearch();
app.setRedactionFilter('all');
app.kindFilter = null;
app.clearSearch();
const page71Andrew = part1.find(e => e.sender === 'Andrew Rambaut' && e.time === '13:05' &&
  app.pageMaps.part1[String(e.idx)]?.start === 71);
const page71Garry = part1.find(e => e.sender === 'Robert Garry' && e.time === '13:37' &&
  app.pageMaps.part1[String(e.idx)]?.start === 71);
const page71Holmes = part1.find(e => e.sender === 'Eddie Holmes' && e.time === '15:43' &&
  app.pageMaps.part1[String(e.idx)]?.start === 71);
ok('page 71 Andrew Rambaut message is separated and corrected from source text',
   !!page71Andrew && page71Andrew.content.startsWith('On a visit to Shaoguan, Guangdong province') &&
   page71Andrew.content.includes('the Guardian and staff from CECGDF') &&
   page71Andrew.content.includes('https://www.theguardian.com/environment/2020/feb/25/') &&
   !page71Andrew.content.includes('sampling those animals') &&
   page71Andrew.stamp_line === '13:05 ET' && !page71Andrew.redaction_count);
ok('page 71 Robert Garry message is separate, partly redacted above and below its visible line',
   !!page71Garry && page71Garry.content ===
     '[Redacted]\nI hope some one is sampling those animals - would be a good place to generate diversity in covs.\n[Redacted]' &&
   page71Garry.redaction_count === 2 &&
   page71Garry.redaction_sources.some(r => r.top === 497 && r.bottom === 505) &&
   page71Garry.redaction_sources.some(r => r.top === 518 && r.bottom === 532) &&
   app.entryRedactionClass(page71Garry) === 'partial');
ok('page 71 Eddie Holmes message keeps its visible line and both redacted sections',
   !!page71Holmes && page71Holmes.content ===
     '[Redacted]\nI agree that we should use nCoV-19. Will do so from now on.\n[Redacted]' &&
   page71Holmes.redaction_count === 2 && page71Holmes.time === '15:43' &&
   page71Holmes.redaction_sources.some(r => r.top === 543 && r.bottom === 570) &&
   page71Holmes.redaction_sources.some(r => r.top === 584 && r.bottom === 628) &&
   app.entryRedactionClass(page71Holmes) === 'partial');
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
input.value = 'Redacted';
app.doSearch();
const redactionHtml = document.getElementById('resultsPanel').innerHTML;
ok('redaction chips render in matching message cards', /class="chip chip-redacted"/.test(redactionHtml));
ok('standalone redaction text is visible', redactionHtml.includes('[Redacted]'));

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

sec('Slack reply markers');
const rambautReplyRoot = app.diaryData.entries.find(e =>
  e.source === 'part2' && (e.slack_reply_authors || []).includes('Andrew Rambaut'));
ok('thread metadata resolves Andrew Rambaut as a reply author',
   !!rambautReplyRoot && app.slackReplyChipsHtml(rambautReplyRoot).includes('Andrew Rambaut'));
const multiReplyRoot = app.diaryData.entries.find(e =>
  e.source === 'part2' && (e.slack_reply_authors || []).length > 1);
ok('multiple reply authors render together in one chip',
   !!multiReplyRoot && (app.slackReplyChipsHtml(multiReplyRoot).match(/class="chip chip-reply"/g)||[]).length === 1 &&
   multiReplyRoot.slack_reply_authors.every(name => app.slackReplyChipsHtml(multiReplyRoot).includes(name)));
const countOnlyRoot = app.diaryData.entries.find(e => e.source === 'part1' &&
  /\b2\s+replies\b/i.test(e.content||'') &&
  !(e.side_thread_authors || []).length && !(e.slack_reply_authors || []).length);
const countOnlyHtml = countOnlyRoot ? app.slackReplyChipsHtml(countOnlyRoot) : '';
ok('reply count remains visible when author metadata is absent',
   !!countOnlyRoot && countOnlyHtml.includes('2 replies') && !countOnlyHtml.includes('Andrew Rambaut'));
ok('relative last-reply age is removed from visible Slack text',
   !!countOnlyRoot && !/Last reply|years?\s+ago/i.test(app.stripSlackReplyChrome(countOnlyRoot.content)));
if (countOnlyRoot) {
  app.displayResults([{
    entry: countOnlyRoot, idx: countOnlyRoot.idx, hits: 1, hitPositions: [],
    source: countOnlyRoot.source,
  }], '', { autoSelect: false });
  const renderedReply = document.getElementById('resultsPanel').innerHTML;
  ok('reply chip is appended after the message text',
     renderedReply.indexOf('slack-reply-markers') > renderedReply.lastIndexOf('</p>'));
  ok('relative reply age is absent from the rendered card',
     !/Last reply|3 years ago/i.test(renderedReply));
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

sec('Author filter, including redacted records');
const authorLabels = Object.keys(app.availableAuthors());
ok('abbreviated and reversed email authors resolve to corpus-supported full names',
   app.entryAuthor({sender:'Ian'}) === 'Ian Lipkin' &&
   app.entryAuthor({sender:'Lipkin'}) === 'Ian Lipkin' &&
   app.entryAuthor({sender:'Kristian'}) === 'Kristian G. Andersen' &&
   app.entryAuthor({sender:'Joao'}) === 'Joao Monteiro' &&
   app.entryAuthor({sender:'Chris'}) === 'Chris Emery' &&
   app.entryAuthor({sender:'"SMITH, lan Michae'}) === 'Ian Michael Smith' &&
   app.entryAuthor({sender:'Fauci, Anthony'}) === 'Anthony Fauci' &&
   app.entryAuthor({sender:'Pope, Andrew'}) === 'Andrew Pope' &&
   app.entryAuthor({sender:'Edward Holmes'}) === 'Edward C. Holmes' &&
   app.entryAuthor({sender:'R.A.M. Fouchier'}) === 'Ron Fouchier' &&
   app.entryAuthor({sender:'GPMB'}) === 'Global Preparedness Monitoring Board');
ok('ambiguous and OCR-corrupted authors are grouped under Redacted',
   app.entryAuthor({sender:'(iS'}) === 'Redacted' &&
   app.entryAuthor({sender:'eo'}) === 'Redacted' &&
   app.entryAuthor({sender:'iN'}) === 'Redacted' &&
   app.entryAuthor({sender:'ofu'}) === 'Redacted' &&
   app.entryAuthor({sender:'Jeanette'}) === 'Redacted' &&
   app.entryAuthor({sender:'SMITH'}) === 'Redacted' &&
   app.entryAuthor({sender:'medicine@us.nature.com'}) === 'Redacted' &&
   app.entryAuthor({sender:''}) === 'Redacted');
ok('author choices omit known malformed aliases',
   !['Ian','Lipkin','Kristian','Joao','Michael','Jeremy','Coleman','Chris',
     '(iS','ofu','medicine@us.nature.com','Fauci, Anthony','Pope, Andrew',
     'Shabman, Reed','Edward Holmes','Eddie Holmes','eo','iN','Jeanette','SMITH',
     '"SMITH, lan Michae','R.A.M. Fouchier','GPMB'].some(name => authorLabels.includes(name)));
const redactedSlack = {
  kind:'slack', source:'part1', sender:'redacted', date:'2020-02-01', time:'1200', raw_date:'',
  content:'redacted-author-filter-probe', pages:[1], thread_key:'test|redacted-slack'
};
const redactedEmail = {
  kind:'email', source:'po-emails', sender:'', author:'Redacted', date:'2020-02-01', time:'1201', raw_date:'',
  content:'redacted-author-filter-probe', pages:[1], thread_key:'test|redacted-email'
};
const existingRedactedAuthorCount = app.availableAuthors().Redacted || 0;
app.diaryData.entries.push(redactedSlack, redactedEmail);
app.kindFilter = null;
app.authorFilter = ['Redacted'];
const redactedEntries = app.filterEntries(app.diaryData.entries);
ok('Redacted author is normalized and selectable from sender/author fields',
   app.entryAuthor(redactedSlack) === 'Redacted' && app.entryAuthor(redactedEmail) === 'Redacted' &&
   app.availableAuthors().Redacted === existingRedactedAuthorCount + 2);
ok('author filter includes existing and probe redacted records',
   redactedEntries.includes(redactedSlack) && redactedEntries.includes(redactedEmail) &&
   redactedEntries.every(e => app.entryAuthor(e) === 'Redacted'));
input.value = 'redacted-author-filter-probe';
app.doSearch();
const redactedHtml = document.getElementById('resultsPanel').innerHTML;
ok('search returns a redacted multi-message block and redacted email',
   (redactedHtml.match(/class="result-entry/g)||[]).length === 2 &&
   /Slack P1/.test(redactedHtml) && /k-email/.test(redactedHtml));
app.diaryData.entries.splice(-2);
app.authorFilter = null;
input.value = 'passaging';
app.kindFilter = ['slack','email','attachment','note'];

sec('Slack side-thread filter and verified Holmes record');
const p2ThreadRoot = app.diaryData.entries.find(e =>
  e.source === 'part2' && e.idx === 2888);
const p2ThreadReply = app.diaryData.entries.find(e =>
  e.source === 'part2' && e.idx === 2890);
const p2ThreadInfo = p2ThreadRoot && app.slackReplyMarkerInfo(p2ThreadRoot);
const p2ReplyAuthor = app.entryAuthor({sender:'Eddie Holmes'});
ok('Part 2 thread-ID timestamp identifies Andrew root and Eddie reply without promoting reply',
   !!p2ThreadRoot && !!p2ThreadReply &&
   p2ThreadRoot.thread_id === '2020-12-01 22:49:04' &&
   p2ThreadRoot.date === '2020-12-02' && p2ThreadRoot.time === '01:49:04' &&
   p2ThreadRoot.stamp_line.startsWith('22:49:04 Pacific') &&
   p2ThreadReply.thread_id === p2ThreadRoot.thread_id &&
   p2ThreadInfo?.count === 1 && p2ThreadInfo.authors.includes(p2ReplyAuthor) &&
   app.slackReplyChipsHtml(p2ThreadRoot).includes('side-thread by ' + p2ReplyAuthor) &&
   !app.slackReplyMarkerInfo(p2ThreadReply));
app.setThreadFilter('side');
const p2ThreadFiltered = app.filterEntries([p2ThreadRoot, p2ThreadReply]);
ok('Part 2 thread-ID root is included in Side threads while its ordinary reply is not',
   p2ThreadFiltered.length === 1 && p2ThreadFiltered[0] === p2ThreadRoot);
app.setThreadFilter('all');
const holmesGenome = part1.find(e => e.idx === 906);
const andersonSideThread = part1.find(e => e.idx === 957);
const followingAndersonMessage = part1.find(e => e.idx === 958);
const reviewedSideThreads = [
  [66,5,1,['Andrew Rambaut']],
  [180,16,2,['Andrew Rambaut','Kristian Andersen']],
  [344,32,3,['Andrew Rambaut','Kristian Andersen']],
  [356,34,1,['Andrew Rambaut']],
  [374,35,1,['Kristian Andersen']],
  [497,47,5,['Andrew Rambaut','Kristian Andersen']],
  [530,49,1,['Andrew Rambaut']],
  [556,51,3,['Kristian Andersen','Eddie Holmes']],
  [630,57,1,['Andrew Rambaut']],
  [721,64,2,['Andrew Rambaut','Kristian Andersen']],
  [778,68,9,['Kristian Andersen','Robert Garry','Andrew Rambaut']],
  [835,73,3,['Andrew Rambaut','Robert Garry','Kristian Andersen']],
  [957,89,2,['Andrew Rambaut','Kristian Andersen']],
  [1128,115,4,['Kristian Andersen','Eddie Holmes']],
  [1257,131,1,['Andrew Rambaut']],
];
const reviewedEntries = reviewedSideThreads.map(([idx]) => part1.find(e => e.idx === idx));
const part1ThreadRoots = part1.filter(e => app.slackReplyMarkerInfo(e));
ok('all 15 specified REV pages map to confirmed reply-indicator roots',
   reviewedSideThreads.every(([idx,page]) =>
     !!app.pageMaps.part1[String(idx)] && app.pageMaps.part1[String(idx)].start === page) &&
   reviewedEntries.every(e => !!e && !!app.slackReplyMarkerInfo(e)));
ok('visible reply-avatar author sets and counts match the 15 source-page indicators',
   reviewedSideThreads.every(([idx,,count,authors]) => {
     const e = part1.find(x => x.idx === idx);
     const info = e && app.slackReplyMarkerInfo(e);
     return !!info && info.count === count &&
       authors.every(author => info.authors.includes(app.entryAuthor({sender:author})));
   }));
ok('known Part 1 reply-author metadata is canonical; only the unverified page-125 record has no author',
   part1ThreadRoots.length === 17 &&
   part1ThreadRoots.filter(e => app.slackReplyMarkerInfo(e).authors.length > 0).length === 16 &&
   part1ThreadRoots.filter(e => !app.slackReplyMarkerInfo(e).authors.length)
       .every(e => e.idx === 1218));
const reactionOnlyMessage = part1.find(e => e.idx === 501);
ok('reaction-only emoji controls are not classified as side threads',
   !!reactionOnlyMessage && !app.slackReplyMarkerInfo(reactionOnlyMessage));
const page89Times = {
  947:'14:28', 948:'15:41', 949:'16:07', 950:'16:08', 951:'17:09',
  952:'17:11', 953:'17:16', 954:'17:19', 955:'17:20', 956:'17:22',
  957:'17:56', 958:'18:07', 960:'19:33',
};
ok('printed Part 1 page 89 times populate their corresponding message records',
   Object.keys(page89Times).every(idx =>
     part1.find(e => e.idx === Number(idx))?.time === page89Times[idx]));
ok('Andersen page 89 message stays distinct and carries the visible @ mention',
   !!andersonSideThread && !!followingAndersonMessage &&
   andersonSideThread.sender === 'Kristian Andersen' &&
   andersonSideThread.content.startsWith('@Andrew Rambaut - do you have a tree/alignment') &&
   !andersonSideThread.content.includes("Alrighty, here's a clean version") &&
   followingAndersonMessage.content.startsWith("Alrighty, here's a clean version"));
ok('Andersen page 89 message has two side replies by the source-identified authors',
   !!andersonSideThread && app.slackReplyMarkerInfo(andersonSideThread).count === 2 &&
   app.slackReplyMarkerInfo(andersonSideThread).authors.includes('Andrew Rambaut') &&
   app.slackReplyMarkerInfo(andersonSideThread).authors.includes('Kristian G. Andersen') &&
   app.slackReplyChipsHtml(andersonSideThread).includes(
     'side-thread by Andrew Rambaut, Kristian G. Andersen') &&
   (app.slackReplyChipsHtml(andersonSideThread).match(/class="chip chip-reply"/g)||[]).length === 1);
ok('Holmes message text and printed time are corrected from Part 1 PDF page 84',
   !!holmesGenome && holmesGenome.sender === 'Eddie Holmes' && holmesGenome.time === '00:29' &&
   holmesGenome.content === "Loads more Chinese genomes coming. I'm not quite when, but they are coming.\n1 reply");
ok('Holmes reply author is shown when source avatar identifies Andrew Rambaut',
   !!holmesGenome && app.slackReplyMarkerInfo(holmesGenome).count === 1 &&
   app.slackReplyMarkerInfo(holmesGenome).authors.includes('Andrew Rambaut') &&
   app.slackReplyChipsHtml(holmesGenome).includes('side-thread by Andrew Rambaut') &&
   (app.slackReplyChipsHtml(holmesGenome).match(/class="chip chip-reply"/g)||[]).length === 1);
ok('reply count uses a clear fallback when the author is not identified',
   !!countOnlyRoot && app.slackReplyChipsHtml(countOnlyRoot).includes('side-thread · 2 replies') &&
   (app.slackReplyChipsHtml(countOnlyRoot).match(/class="chip chip-reply"/g)||[]).length === 1);
ok('combined reply author chips retain full names in the overflow title',
   !!multiReplyRoot && app.slackReplyChipsHtml(multiReplyRoot).includes('title="side-thread by ') &&
   app.slackReplyChipsHtml(multiReplyRoot).includes(' · '));
ok('timestamp labels are normalized to ET without inventing missing times',
   app.formatEntryTime(holmesGenome) === '00:29 ET' &&
   app.formatEntryTime({source:'po-emails', time:'1256'}) === '12:56 ET' &&
   app.formatEntryTime({source:'part2', time:'17:56:20'}) === '17:56:20 ET' &&
   app.formatEntryTime({source:'part1', time:null}) === '');
const sideThreadRoots = app.filterEntries(app.diaryData.entries.filter(e =>
  app.slackReplyMarkerInfo(e)));
app.kindFilter = ['slack'];
app.authorFilter = null;
input.value = '';
app.clearSearch();
app.setThreadFilter('side');
const sideFiltered = app.filterEntries(app.diaryData.entries);
ok('side-thread filter includes roots with reply metadata, including Holmes',
   sideFiltered.includes(holmesGenome) && sideFiltered.length === sideThreadRoots.length &&
   reviewedEntries.every(e => sideFiltered.includes(e)) &&
   sideFiltered.every(e => !!app.slackReplyMarkerInfo(e)));
const renderedSideThreads = window._searchResults || [];
ok('side-thread browse renders the full filtered result set, not just its initial 101-entry window',
   renderedSideThreads.length === sideFiltered.length &&
   renderedSideThreads.every(r => sideFiltered.includes(r.entry)));
ok('current corpus has 246 Slack side-thread roots across both releases',
   renderedSideThreads.length === 246 &&
   renderedSideThreads.filter(r => r.entry.source === 'part1').length === 17 &&
   renderedSideThreads.filter(r => r.entry.source === 'part2').length === 229);
ok('two additional Part 1 reply indicators map to pages 84 and 125',
   app.pageMaps.part1['906']?.start === 84 &&
   app.pageMaps.part1['1218']?.start === 125 &&
   [906,1218].every(idx => renderedSideThreads.some(r =>
     r.entry.source === 'part1' && r.entry.idx === idx)));
app.setThreadFilter('all');
const allMessageBrowse = window._searchResults || [];
ok('switching Side threads back to All messages restores a bounded ordinary browse window',
   app.threadFilter === null && app.browseMode &&
   allMessageBrowse.length > 0 && allMessageBrowse.length < sideFiltered.length &&
   allMessageBrowse.every(r => app.entryVisible(r.entry)) &&
   allMessageBrowse.some(r => !app.slackReplyMarkerInfo(r.entry)));
app.setThreadFilter('side');
ok('switching back to Side threads restores the complete side-thread set',
   !app.browseMode && (window._searchResults || []).length === sideFiltered.length &&
   (window._searchResults || []).every(r => !!app.slackReplyMarkerInfo(r.entry)));
app.setThreadFilter('all');
app.kindFilter = null;
const andersonThreadReply = app.diaryData.entries.find(e =>
  e.source === 'part2' && e.date === '2020-08-14' && e.time === '17:56:20' &&
  e.sender === 'Kristian Andersen');
ok('Andersen 17:56 message remains an ordinary reply in its source thread',
   !!andersonThreadReply && andersonThreadReply.thread_id === '2020-08-14 14:27:13' &&
   !app.slackReplyMarkerInfo(andersonThreadReply));
const andersonThreadRoot = app.diaryData.entries.find(e =>
  e.source === 'part2' && e.date === '2020-08-14' && e.time === '17:27:13' &&
  e.sender === 'Eddie Holmes');
ok('thread authors attach to the source root, not Andersen’s later reply',
   !!andersonThreadRoot &&
   andersonThreadRoot.slack_reply_authors.includes('Kristian G. Andersen') &&
   andersonThreadRoot.slack_reply_authors.includes('Andrew Rambaut') &&
   app.slackReplyChipsHtml(andersonThreadRoot).includes(
     'side-thread by Andrew Rambaut, Kristian G. Andersen'));
const redacted1756Email = emails.find(e => e.idx === 181);
const anderson1652Email = emails.find(e => e.idx === 185);
ok('17:56 email sender stays Redacted and is not merged with Andersen’s quoted message',
   !!redacted1756Email && !!anderson1652Email &&
   app.entryAuthor(redacted1756Email) === 'Redacted' &&
   app.formatEntryTime(redacted1756Email) === '12:56 ET' &&
   redacted1756Email.content.includes('Sorry. This is the final version (v2.2).') &&
   anderson1652Email.sender === 'Kristian G. Andersen' &&
   redacted1756Email.thread_key !== anderson1652Email.thread_key);
if (holmesGenome) {
  app.displayResults([{
    entry: holmesGenome, idx: holmesGenome.idx, hits: 1, hitPositions: [],
    source: holmesGenome.source,
  }], '', { autoSelect: false });
  const holmesHtml = document.getElementById('resultsPanel').innerHTML;
  ok('Holmes result card shows canonical author, time, text, and side-thread shield',
     holmesHtml.includes('Edward C. Holmes') && holmesHtml.includes('00:29 ET') &&
     holmesHtml.includes('Loads more Chinese genomes') &&
     holmesHtml.includes('side-thread by Andrew Rambaut'));
}

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
ok('guide covers every citation', guideResp.totals.citations === 322, String(guideResp.totals.citations));
const evNoKind = guideResp.sections.flatMap(s=>s.evidence).filter(e=>!e.kind);
ok('every guide citation is classified', evNoKind.length === 0);
const docs = guideResp.documents ? Object.values(guideResp.documents) : [];
ok('every cited document is catalogued', docs.length === 32, String(docs.length));


sec('Stacked timeline (one segment per kind, release sub-totals)');
app.buildTimelineSeries();
const ts = app.timelineSeries;
ok('timeline reset control has a dedicated collapse-state hook',
   /class="collapse-btn timeline-reset-zoom"/.test(pageHtml));
ok('collapsed landscape timeline hides the reset control',
   /body\.layout-landscape \.charts-panel\.collapsed \.timeline-reset-zoom\s*\{\s*display:\s*none;/.test(pageHtml));
ok('collapsed landscape timeline overrides resized inline width constraints',
   /body\.layout-landscape \.charts-panel\.collapsed\s*\{\s*width:\s*36px !important;\s*min-width:\s*36px !important;\s*max-width:\s*36px !important;/.test(pageHtml));
ok('collapsed landscape timeline centers its remaining expand control',
   /body\.layout-landscape \.charts-panel\.collapsed \.panel-header > div\s*\{\s*width:\s*100%;\s*justify-content:\s*center;/.test(pageHtml));
ok('collapsed portrait timeline hides the reset control',
   /body\.layout-portrait \.charts-panel\.collapsed \.timeline-reset-zoom\s*\{\s*display:\s*none;/.test(pageHtml));
ok('collapsed portrait timeline shrinks to its header',
   /body\.layout-portrait \.charts-panel\.collapsed\s*\{\s*height:\s*auto !important;\s*max-height:\s*none !important;\s*min-height:\s*0 !important;\s*flex:\s*0 0 auto;/.test(pageHtml));
ok('collapsed portrait timeline overrides resized inline height',
   /body\.layout-portrait \.charts-panel\.collapsed\s*\{\s*height:\s*auto !important;\s*max-height:\s*none !important;\s*min-height:\s*0 !important;/.test(pageHtml));
ok('timeline has one stacked segment per top-level kind', !!ts && Array.isArray(ts.stacks) && ts.stacks.length >= 4,
   ts ? ts.stacks.length + ' segments' : 'none');
const stackByKind = {};
(ts.stacks || []).forEach(function(seg) {
  (stackByKind[seg.kind] = stackByKind[seg.kind] || []).push(seg);
});
ok('each kind is exactly one segment (no per-release shading)',
   Object.keys(stackByKind).every(function(k) { return stackByKind[k].length === 1; }));
const slackSeg = (stackByKind.slack || [])[0];
ok('slack carries both releases as sub-totals, not separate segments',
   !!slackSeg && Array.isArray(slackSeg.sources) && slackSeg.sources.length === 2,
   slackSeg ? JSON.stringify(slackSeg.sources) : 'no slack segment');
ok('email and draft each have their own media colour',
   !!stackByKind.email && !!stackByKind.draft);
const stackTotal = (ts.stacks || []).reduce(function(a, seg) { return a + seg.total; }, 0);
const entryTotal = (ts.entryCounts || []).reduce(function(a, c) { return a + c; }, 0);
ok('stack totals equal the per-day entry counts', stackTotal === entryTotal,
   stackTotal + ' vs ' + entryTotal);

sec('Legend');
const legendEl = document.getElementById('timelineLegend');
ok('legend element exists in the markup', !!legendEl);

sec('Guide citation colours + PDF links (shared coding)');
ok('kindColor matches timeline hue for slack', /hsl\(210/.test(app.kindColor('slack')),
   app.kindColor('slack'));
ok('kindColor matches timeline hue for email', /hsl\(150/.test(app.kindColor('email')),
   app.kindColor('email'));
ok('kindColor gives grey for unclassified other', /hsl\(0, 0%/.test(app.kindColor('other')),
   app.kindColor('other'));
ok('guideDocToSource resolves Slack citations to Part 1 before the handover day',
   app.guideDocToSource('Proximal_Origin_Slack.pdf', '2020-02-11') === 'part1',
   String(app.guideDocToSource('Proximal_Origin_Slack.pdf', '2020-02-11')));
ok('guideDocToSource resolves Slack citations to Part 2 after the handover day',
   app.guideDocToSource('Proximal_Origin_Slack.pdf', '2021-01-01') === 'part2',
   String(app.guideDocToSource('Proximal_Origin_Slack.pdf', '2021-01-01')));
ok('guideDocToSource defaults undated Slack citations to Part 1',
   app.guideDocToSource('Proximal_Origin_Slack.pdf', null) === 'part1',
   String(app.guideDocToSource('Proximal_Origin_Slack.pdf', null)));
ok('guideDocToSource resolves the FOIA email PDF',
   app.guideDocToSource('Proximal_Origin_Emails.pdf') === 'po-emails',
   String(app.guideDocToSource('Proximal_Origin_Emails.pdf')));
ok('guideDocToSource resolves the SSCP drafts PDF',
   app.guideDocToSource('SSCP-Drafts-of-Proximal-Origin.pdf') === 'sscp',
   String(app.guideDocToSource('SSCP-Drafts-of-Proximal-Origin.pdf')));
ok('guideDocToSource resolves the Farrar-Fauci-Collins emails',
   app.guideDocToSource('farrar-fauci-comms-full.pdf') === 'farrar-fauci',
   String(app.guideDocToSource('farrar-fauci-comms-full.pdf')));
ok('guideDocToSource leaves genuinely un-ingested docs non-clickable',
   app.guideDocToSource('Baric-Emails-2.17.21.pdf') === null,
   String(app.guideDocToSource('Baric-Emails-2.17.21.pdf')));
ok('guideCitationLabel uses the document name when there is one',
   app.guideCitationLabel({ doc: 'Proximal_Origin_Emails.pdf', kind: 'email', raw: 'x' }) === 'Proximal_Origin_Emails.pdf');
ok('guideCitationLabel falls back to the citation\'s own text, footnote markers stripped',
   app.guideCitationLabel({ doc: null, kind: 'social', raw: 'Tedros’ tweet, 11 Jan[^9]' }) === 'Tedros’ tweet, 11 Jan',
   app.guideCitationLabel({ doc: null, kind: 'social', raw: 'Tedros’ tweet, 11 Jan[^9]' }));
ok('guideCitationLabel falls back to the bare kind only as a last resort',
   app.guideCitationLabel({ doc: null, kind: 'other', raw: '' }) === 'other');

sec('Bookmarks');
app.bookmarks = [];
const target = app.diaryData.entries.find(e => e.source === 'po-emails');
ok('every entry has a bookmark key', app.diaryData.entries.every(e => !!e.bm_key));
const keys = app.diaryData.entries.map(e => e.bm_key);
ok('bookmark keys are unique across releases', new Set(keys).size === keys.length,
   (keys.length - new Set(keys).size) + ' duplicates');
const p1 = app.diaryData.entries.find(e => e.source === 'part1');
const p2 = app.diaryData.entries.find(e => e.source === 'part2');
ok('part1 and part2 keys do not collide (idx is per-part)',
   p1 && p2 && p1.bm_key !== p2.bm_key && /part1/.test(p1.bm_key) && /part2/.test(p2.bm_key),
   p1 && p1.bm_key + ' vs ' + p2 && p2.bm_key);
ok('adding a bookmark returns true and records it',
   app.toggleBookmark(target.bm_key, { label: 'T', date: target.date }) === true &&
   app.isBookmarked(target.bm_key) && app.bookmarks.length === 1);
ok('clicking again removes it',
   app.toggleBookmark(target.bm_key, {}) === false &&
   !app.isBookmarked(target.bm_key) && app.bookmarks.length === 0);
app.toggleBookmark(target.bm_key, { label: 'Holmes', sub: 'Email', date: '2020-02-11' });
const payload = app.bookmarksPayload();
ok('the saved file names its format and version',
   payload.format === 'drastic-bookmarks' && payload.version === 1 && payload.count === 1,
   JSON.stringify({ f: payload.format, v: payload.version, c: payload.count }));
ok('the saved record carries key, app and url (portable across DRASTIC apps)',
   payload.bookmarks[0].key === target.bm_key && payload.bookmarks[0].app === 'po-slack' &&
   typeof payload.bookmarks[0].url === 'string');
ok('a bookmark resolves back to its entry',
   app.openEntryByBmKey(target.bm_key, 1) === true);
ok('an unknown key is refused rather than opening the wrong box',
   app.openEntryByBmKey('part1/does-not-exist') === false);
ok('bmAppFor recognises the sibling apps from a url',
   app.bmAppFor('../Fauci_Diary/page_based/index.html') === 'fauci-diary' &&
   app.bmAppFor('../DaszakCalendar/index.html') === 'daszak-calendar',
   app.bmAppFor('../Fauci_Diary/page_based/index.html') + ' / ' +
   app.bmAppFor('../DaszakCalendar/index.html'));
app.bookmarks = [];

sec('Email header + signature parsing');
const emailsAll = app.diaryData.entries.filter(e => e.source === 'po-emails');
const holmes = emailsAll.filter(e => /Holmes/.test(e.sender || ''));
ok('most subjects are recovered', emailsAll.filter(e => e.subject).length >= 70,
   emailsAll.filter(e => e.subject).length + ' of ' + emailsAll.length);
// A Subject line may still appear in a body, but only as quoted history: the
// message it quotes always carries its own header rule before it. What must
// never happen is this message's OWN subject being stranded in its own body --
// i.e. a Subject line above the first quoted To:/From: header.
const bodySubjectOnly = emailsAll.filter(function(e) {
  const parts = e.content.split('----------');
  if (parts.length < 3) return false;            // no quoted history at all
  const b = parts[1];
  const s = b.search(/(^|\n)Subject: /);
  if (s < 0) return false;
  const q = b.search(/(^|\n)(To|From|Cc): /);
  return q < 0 || s < q;                          // Subject before any quote header
});
ok('no message\'s own subject is stranded in its body', bodySubjectOnly.length === 0,
   bodySubjectOnly.map(e => e.date + ' ' + e.time + ' ' + e.subject).join(', '));
// A message whose scan lost its From: line (opens on Date:/Sent:) must not be
// fused into its neighbour: no entry may carry two Subjects or two stamps.
ok('no entry carries a doubled Subject (stitched messages)',
   emailsAll.every(e => (e.subject.match(/Invitation to edit/g) || []).length <= 1),
   emailsAll.filter(e => (e.subject.match(/Invitation to edit/g) || []).length > 1).length + ' doubled');
ok('no entry carries a doubled stamp (stitched messages)',
   emailsAll.every(e => ((e.stamp || '').match(/2020/g) || []).length <= 1),
   emailsAll.filter(e => ((e.stamp || '').match(/2020/g) || []).length > 1).length + ' doubled');
// Senders eaten with the From: line are recovered -- from an inline quote
// marker ("On <date>, <name> wrote:") when the message is a nested reply
// introduced that way, from the signature block otherwise -- and the
// attribution is recorded either way; anything else stays honestly empty.
ok('senders lost with their From: line are recovered and the method recorded',
   emailsAll.filter(e => e.sender_how && /signature|inline quote marker/.test(e.sender_how)).length >= 1,
   emailsAll.filter(e => e.sender_how && /signature|inline quote marker/.test(e.sender_how)).length + ' recovered');
ok('Cc is parsed as Cc, not the OCR\'s "Ce:"',
   emailsAll.some(e => /^Cc: /m.test(e.content)));
ok('no "Ce:" survives as a header line',
   !emailsAll.some(e => /(^|\n)Ce: /.test(e.content.split('----------')[0] || '')));
const sig = emailsAll.filter(e => e.signature);
ok('signature blocks are separated from the message text', sig.length > 0,
   sig.length + ' messages carry a signature');
ok('a signature keeps its own line returns',
   sig.some(e => e.signature.split('\n').length >= 3),
   'max lines: ' + Math.max(0, ...sig.map(e => e.signature.split('\n').length)));
ok('the signature is not also left in the message body',
   sig.every(e => !e.content.split('----------')[1].includes('FAA FRS')));
ok('scan-width wraps are rejoined (no artificial returns mid-sentence)',
   !app.diaryData.entries.some(e => e.source === 'po-emails' &&
     /gravitas\.\.\.plus\n/.test(e.content)),
   'found "gravitas...plus" still split across a return');

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
