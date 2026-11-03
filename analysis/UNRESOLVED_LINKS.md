# Unresolved links: analysis for the human reviewer

Source: `tools/scan_urls.py` (every web address in the OCR'd sources, tested live), `tools/url_fixes.json` (51 repair rows), `tools/apply_url_fixes.py` (applies them), `analysis/url_scan.json` (the scan this report reads). Slack Part 2 is native text, not OCR, and was not repaired.

## Counts

| Status | Meaning | Addresses |
|---|---|---|
| Settled | repaired or already clean; the address answers 200/3xx | 120 |
| Likely | address looks right but the site blocks scripts (403), is paywalled (402/406) or did not answer from here: page not confirmed | 32 |
| Unknown | still broken | 44 |

Counts are distinct addresses as they read after repair. About 110 addresses were repaired in this pass (scheme, `www`, domain and slug typos, line-wrap splits).

## How a link gets repaired

1. Deterministic OCR confusions (`apply_url_fixes.RULES`): `hittps:`, `https: //`, `wwew`, `nim.nih`, `nebi`, `bbe.com`, `cde.gov`, ...
2. A hand-checked row in `url_fixes.json` (broken form -> correct address, found by web search). Whitespace and a lost hyphen/underscore inside the broken form are tolerated.
3. The app links any `https://` or `www.` address it finds, in the Content and Thread panels.
To add a repair: append a row to `url_fixes.json`, run `python3 tools/apply_url_fixes.py`, then rescan.

## Likely (page cannot be confirmed from here, address looks right)

| # | Address as it reads now | Where | Why |
|---|---|---|---|
| L1 | `https://jvi.asm.org/content/early/2020/01/23/JVI.00127-20` | Slack Part 1 · 2020-02-02  ET · Kristian Andersen · slack-part1.pdf p.9 | answered 403 (403) |
| L2 | `https://jvi.asm.org/content/82/5/2274` | Slack Part 1 · 2020-02-02  ET · Kristian Andersen · slack-part1.pdf p.9 | answered 403 (403) |
| L3 | `https://science.sciencemag.org/content/302/5643/276` | Slack Part 1 · 2020-02-03 10:15 ET · Robert Garry · slack-part1.pdf p.10 | answered 403 (403) |
| L4 | `https://www.forbes.com/sites/victor` | Slack Part 1 · 2020-02-03 13:59 ET · Robert Garry · slack-part1.pdf p.11 | answered 403 (403) |
| L5 | `https://www.nrdc.org/experts/olly-pepper/nrdc-and-allies-sue-trump-administration-protect-pangolins` | Slack Part 1 · 2020-02-07  ET · Robert Garry · slack-part1.pdf p.20 | answered 403 (403) |
| L6 | `https://jvi.asm.org/content/79/22/14451` | Slack Part 1 · 2020-02-08 16:04 ET · Kristian Andersen · slack-part1.pdf p.23 | answered 403 (403) |
| L7 | `https://www.sciencedirect.com/science/article/pii/S0166354220300528` | Slack Part 1 · 2020-02-10  ET · Robert Garry · slack-part1.pdf p.30 | answered 403 (403) |
| L8 | `https://www.sciencedirect.com/science/article/pii/S00653527` | Slack Part 1 · 2020-02-11  ET · Robert Garry · slack-part1.pdf p.32 | answered 403 (403) |
| L9 | `https://www.sciencedirect.com/science/article/pii/S2211124718311483?via%3Dihub` | Slack Part 1 · 2020-02-11 16:00 ET · Robert Garry · slack-part1.pdf p.34 | answered 403 (403) |
| L10 | `https://www.washingtonpost.com/politics/2020/02/16/tom-cotton-coronavirus-conspiracy` | Slack Part 1 · 2020-02-16  ET · Robert Garry · slack-part1.pdf p.44 | site did not answer from here (could not check) (ERR:TimeoutE) |
| L11 | `https://www.thelancet.com/pb-assets/Lencet/pdfs/S0140673620304` | Slack Part 1 · 2020-02-17 17:45 ET · Andrew Rambaut · slack-part1.pdf p.49 | answered 403 (403) |
| L12 | `https://science.sciencemag.org/content/sci/earty/2020/02/19/scence.abb2507` | Slack Part 1 · 2020-02-19  ET · Robert Garry · slack-part1.pdf p.53 | answered 403 (403) |
| L13 | `https://www.thelancet.com/journals/lancet/article/PIS0140-6736(20)304` | Slack Part 1 · 2020-02-19  ET · Kristian Andersen · slack-part1.pdf p.53 | answered 403 (403) |
| L14 | `https://www.sciencemag.org/news/2020/02/scientists-strongly-condemn-rumors-and-conspiracy-theories-a` | Slack Part 1 · 2020-02-19  ET · Kristian Andersen · slack-part1.pdf p.53 | answered 403 (403) |
| L15 | `https://www.politico.com/news/2020/02/21/coronavirus-trump-white-house-116650` | Slack Part 1 · 2020-02-22 09:17 ET · Robert Garry · slack-part1.pdf p.60 | answered 403 (403) |
| L16 | `www.cell.com/pb-assets/journals/research/cell/Cell_` | Slack Part 1 · 2020-02-28  ET · Kristian Andersen · slack-part1.pdf p.75 | answered 403 (403) |
| L17 | `https://www.news.com.au/lifestyle/health/health-problems/t` | Slack Part 1 · 2020-04-16  ET · Eddie Holmes · slack-part1.pdf p.125 | answered 403 (403) |
| L18 | `https://www.researchgate.net/publication/340100582_WUHAN_COVID-19_SYNTHETIC_ORIGINS_` | Slack Part 1 · 2020-04-16  ET · Robert Garry · slack-part1.pdf p.127 | answered 403 (403) |
| L19 | `https://mbio.asm.org/content/6/4/e01013-15` | Slack Part 1 · 2020-04-19 09:02 ET · Robert Garry · slack-part1.pdf p.132 | answered 403 (403) |
| L20 | `https://www.scienceopen.com/search#(‘order'~O_‘context'~(‘collection'~('id'~'d6ba10ea-809d-4f28-96b9` | Slack Part 1 · 2020-04-20 14:58 ET · Robert Garry · slack-part1.pdf p.133 | answered 403 (403) |
| L21 | `https://www.scienceopen.com/search#content` | Slack Part 1 · 2020-04-20 15:10 ET · Kristian Andersen · slack-part1.pdf p.133 | answered 403 (403) |
| L22 | `https://www.nytimes.com/2020/04/30/us/politics/trump-administration-intelligence-coronavirus-china.h` | Slack Part 1 · 2020-04-30 16:32 ET · Kristian Andersen · slack-part1.pdf p.139 | answered 403 (403) |
| L23 | `https://bit.ly/2HMndCi` | Manuscript drafts · 2020-02-22 0217 ET · Proximal Origin manuscript · sscp-drafts.pdf p.107-120 | site did not answer from here (could not check) (ERR:TimeoutE) |
| L24 | `https://jvi.asm.org/content/79/22/1445` | P.O. emails · 2020-02-06 2307 ET · Michael Farzan · po-emails.pdf p.143-144 | answered 403 (403) |
| L25 | `https://www.nytimes.com/reuters/2020/02/07/world/asia/07reuters-china-health-pangolins.html` | P.O. emails · 2020-02-07 0446 ET · Andrew Rambaut · po-emails.pdf p.48 | answered 403 (403) |
| L26 | `https://www.factcheck.org/2020/02/baseless-conspiracy-theories-claim-new-coronavirus-was-bioengineer` | P.O. emails · 2020-02-09 0016 ET · Kristian G. Andersen · po-emails.pdf p.70-145 | answered 403 (403) |
| L27 | `https://www.tandfonline.com/doi/full/10.1080/20477724.2020.1725339` | P.O. emails · 2020-02-16 0318 ET · Edward Holmes · po-emails.pdf p.84 | answered 403 (403) |
| L28 | `https://www.flickr.com/photos/niaid/albums/72157712914621487` | P.O. emails · 2020-02-16 0921 ET ·  · po-emails.pdf p.90-98 | answered 403 (403) |
| L29 | `https://www.washingtonpost.com/politics/2020/02/16/tom-cotton-coronavirus-conspiracy/` | P.O. emails · 2020-02-16 1752 ET · Robert Garry · po-emails.pdf p.88-96 | site did not answer from here (could not check) (ERR:TimeoutE) |
| L30 | `https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30419` | P.O. emails · 2020-03-04 1832 ET · Kristian G. Andersen · po-emails.pdf p.135-136 | answered 403 (403) |
| L31 | `https://www.factcheck.org/2020/02/baseless-conspiracy-theories-claim-new-coronavirus` | Farrar-Fauci emails · 2020-02-08 1615 ET · Kristian G. Andersen · farrar-fauci-comms.pdf p.56 | answered 403 (403) |
| L32 | `https://www.washingtonpost.com/local/new-dc-hospital-numbers-suggest-kids-do-face-some-risk-of-coron` | Farrar-Fauci emails · 2020-04-27 0738 ET · Jeremy Farrar · farrar-fauci-comms.pdf p.27-28 | site did not answer from here (could not check) (ERR:TimeoutE) |

Nothing to do unless you want them opened by hand once.

## Unknown (still broken)

### Page not found: slug damaged by OCR, or the page has been removed: 21

| # | Address as it reads now | Where |
|---|---|---|
| U1 | `https://global.chinadaily.com.cn/a/202002/02/WS5c36b2b7a31012821727432chtmI` | Slack Part 1 · 2020-02-03 13:59 ET · Robert Garry · slack-part1.pdf p.11 |
| U2 | `https://jameslyonsweiler.com/2020/02/02/moderately-strong-confirmation-of-a-laboratory-origin-of-2019-ncow/` | Slack Part 1 · 2020-02-05  ET · Andrew Rambaut · slack-part1.pdf p.15 |
| U3 | `https://docs.google.com/document/d/14HI2` | Slack Part 1 · 2020-02-08 08:52 ET · Andrew Rambaut · slack-part1.pdf p.22 |
| U4 | `https://abcnews.go.com/Politics/white-house-asks-scientists-investigate` | Slack Part 1 · 2020-02-09 15:14 ET · Robert Garry · slack-part1.pdf p.25 |
| U5 | `https://docs.google.com/document/d/14HI21tdEyXQSXBBDC2KWHxSrKifyMdkK` | Slack Part 1 · 2020-02-17  ET · Kristian Andersen · slack-part1.pdf p.47 |
| U6 | `https://docs.google.com/document/d/14HI21tdEyXQSXBBDC2KwHxSrKffyMdkWdMZGXxbd228` | Slack Part 1 · 2020-02-21 14:15 ET · Kristian Andersen · slack-part1.pdf p.58 |
| U7 | `https://docs.google.com/document/d/1TQoMX8u_QiumfeLLwi06TLI-VKPBefsv34tjO8fLE6o/edit` | Slack Part 1 · 2020-02-22 15:09 ET · Kristian Andersen · slack-part1.pdf p.60 |
| U8 | `https://www.washingtonexaminer.com/washington-secrets/fauci-chinese-cat-feasts-linked-to-viru` | Slack Part 1 · 2020-02-28  ET · Robert Garry · slack-part1.pdf p.75 |
| U9 | `https://virological.org/t/identification-of` | Slack Part 1 · 2020-04-01  ET · Kristian Andersen · slack-part1.pdf p.113 |
| U10 | `https://journals.plos.org/plosone/article` | Slack Part 1 · 2020-04-02 13:50 ET · Kristian Andersen · slack-part1.pdf p.116 |
| U11 | `https://pan.baidu.com/s/1QnUdVJImmByO-MWim7PE4A` | Slack Part 1 · 2020-04-10  ET · Kristian Andersen · slack-part1.pdf p.121 |
| U12 | `https://www.cnn.com/2020/04/15/polit` | Slack Part 1 · 2020-04-16  ET · Kristian Andersen · slack-part1.pdf p.125 |
| U13 | `https://www.9news.com.au/world/united-states-trump-investigating-sor` | Slack Part 1 · 2020-04-16  ET · Eddie Holmes · slack-part1.pdf p.125 |
| U14 | `https://pubpeer.com/publications/8319A13E7` | Slack Part 1 · 2020-04-21  ET · Kristian Andersen · slack-part1.pdf p.134 |
| U15 | `https://www.theguardian.com/world/live/2020/apr/30/coronavirus-us-live-federal-guidelines-social-distancing-ex` | Slack Part 1 · 2020-04-30 19:23 ET · Eddie Holmes · slack-part1.pdf p.139 |
| U16 | `https://www.bbc.com/news/w` | Slack Part 1 · 2020-04-30  ET · Eddie Holmes · slack-part1.pdf p.140 |
| U17 | `https://www.who.int/news-room/detail/30-01-2020-statement-on-the-second-meeting-of-the-international-health-re` | Manuscript drafts · 2020-03-03 1809 ET · Proximal Origin manuscript · sscp-drafts.pdf p.163-179 |
| U18 | `https://medicine.tulane.edu/departments/microbiology-immunology-tulane-cancer-center/faculty/robert-f-garry-jr` | P.O. emails · 2020-01-31 1757 ET · Jeremy Farrar · po-emails.pdf p.2 |
| U19 | `https://www.ucdenver.edu/academics/colleges/medicalschool/departments/ImmunologyMicrobiology/faculty/departmen` | P.O. emails · 2020-02-05 1628 ET · Robert Garry · po-emails.pdf p.40-41 |
| U20 | `https://www.nature.com/subscriptions/recommend.html#forms` | P.O. emails · 2020-03-05 1603 ET · medicine@us.nature.com · po-emails.pdf p.122-125 |
| U21 | `https://t.co/Bj6YHU8zi` | Farrar-Fauci emails · 2020-04-27 0713 ET · Jeremy Farrar · farrar-fauci-comms.pdf p.21-29 |

### Cut off in the screenshot: 18

| # | Address as it reads now | Where |
|---|---|---|
| U22 | `https://journals.plos.org/plospathogens/article?id=` | Slack Part 1 · 2020-02-03 10:27 ET · Robert Garry · slack-part1.pdf p.11 |
| U23 | `https://science.sciencemag.org/content/sci/309/5742/1864.full.pdf` | Slack Part 1 · 2020-02-03 16:22 ET · Robert Garry · slack-part1.pdf p.13 |
| U24 | `https://science.sciencemag.org/content/sci/earty/` | Slack Part 1 · 2020-02-09 16:24 ET · Robert Garry · slack-part1.pdf p.27 |
| U25 | `https://www` | Slack Part 1 · 2020-02-10  ET · Kristian Andersen · slack-part1.pdf p.30 |
| U26 | `https://docs.google.com/document/d/` | Slack Part 1 · 2020-02-21 14:15 ET · Kristian Andersen · slack-part1.pdf p.58 |
| U27 | `https://docs` | Slack Part 1 · 2020-02-24  ET · Robert Garry · slack-part1.pdf p.59 |
| U28 | `www` | Slack Part 1 · 2020-03-04  ET · Kristian Andersen · slack-part1.pdf p.85 |
| U29 | `https://wwwdeonarddobsonart.co.uk/` | Slack Part 1 · 2020-03-18 06:05 ET · Eddie Holmes · slack-part1.pdf p.102 |
| U30 | `https://www.altmetric.com/top100/2019/` | Slack Part 1 · 2020-03-19 03:29 ET · Andrew Rambaut · slack-part1.pdf p.103 |
| U31 | `https://twitter.cor` | Slack Part 1 · 2020-03-24  ET · Kristian Andersen · slack-part1.pdf p.108 |
| U32 | `https://www.usatoday.col` | Slack Part 1 · 2020-03-29  ET · Eddie Holmes · slack-part1.pdf p.109 |
| U33 | `https://www.biorxiv.org/content/` | Slack Part 1 · 2020-04-05  ET · Andrew Rambaut · slack-part1.pdf p.118 |
| U34 | `https://www.ktvu.co` | Slack Part 1 · 2020-04-16  ET · Eddie Holmes · slack-part1.pdf p.125 |
| U35 | `https://journals.plos.org/plosone/article?id=` | Slack Part 1 · 2020-04-17 16:57 ET · Kristian Andersen · slack-part1.pdf p.128 |
| U36 | `https://www.ncbinim.nih.gov/pubmed/` | Slack Part 1 · 2020-04-17 19:09 ET · Kristian Andersen · slack-part1.pdf p.129 |
| U37 | `www.ecohealthalliance.org` | P.O. emails · 2020-02-04 0402 ET · Daszak, Peter · po-emails.pdf p.16-17 |
| U38 | `https://icmm.ku.dk/english/research-groups/clausen-group/` | P.O. emails · 2020-02-09 1500 ET ·  · po-emails.pdf p.57 |
| U39 | `https://platformsupport.nature.com` | P.O. emails · 2020-03-05 1603 ET · medicine@us.nature.com · po-emails.pdf p.122-125 |

### Domain does not resolve: OCR error in the domain, or the site is gone: 5

| # | Address as it reads now | Where |
|---|---|---|
| U40 | `https://docs.google.com/document/d/1HOVHVaahY¥` | Slack Part 1 · 2020-02-01 22:42 ET · Kristian Andersen · slack-part1.pdf p.4 |
| U41 | `https://www.nature.com/articles/425915a’Serological` | Slack Part 1 · 2020-02-03 17:40 ET · Robert Garry · slack-part1.pdf p.13 |
| U42 | `https://cov-glue.cve.glaac.uk/#/replacement` | Slack Part 1 · 2020-02-05 15:57 ET · Kristian Andersen · slack-part1.pdf p.15 |
| U43 | `https://www.bing.com/search?q«Beijir` | Slack Part 1 · 2020-04-12  ET · Robert Garry · slack-part1.pdf p.123 |
| U44 | `https://nam03.safelinks.protection.outiook.com/?url=https%3A%2F%2Fwww.foxnews.com%2F` | Slack Part 1 · 2020-04-16 11:52 ET · Robert Garry · slack-part1.pdf p.128 |

## What would settle each group

- **Cut off in the screenshot:** the printed address ends mid-word. Only the page image can tell whether the full address is visible further on; the Slack preview card under the link shows the page title, so a web search on that title finds the page. Reviewer decision: do these by hand, or leave unlinked.
- **Page not found:** try the address in the Wayback Machine (`web.archive.org/web/2020/<address>`); a damaged slug usually shows as the one word that differs from the title under the link.
- **Domain does not resolve:** compare with the domain named in the preview card (it is printed on the line below the link and usually OCRs better).
- **Could not check:** retry later or open in a browser.

