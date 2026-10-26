# tools/tests: checks for the app

- `test_app.mjs`: runs `page_based/index.html`'s own script against the real data files. Run: `node test_app.mjs`.
- `test_browser.mjs`: opens the app in a browser and checks it. It expects the app to be served at `http://localhost:8099/`.
