Do these two things:

## 1. Modify the React SPA (index.html + JS bundles)

The SPA at `/Users/fudongli/Projects/poker_analysis/` is a Vite-built React app.

**File to read first:** `/Users/fudongli/Projects/poker_analysis/assets/index-nzS1R7TH.js`

**Changes needed in the main JS bundle:**

a) Change the navbar "DAILY TIP" link href from `#daily-tips` to `./daily-tips.html`. The current code around line 60 is:
`{label:"DAILY TIP",href:"#daily-tips"}`
Change it to:
`{label:"DAILY TIP",href:"./daily-tips.html"}`

b) Make the DailyTipsSection component render NOTHING (null/fragment). The component is loaded via:
`A.lazy(()=>na(()=>import("./DailyTipsSection-D9lpSvnH.js"),...))`

The easiest approach: edit `/Users/fudongli/Projects/poker_analysis/assets/DailyTipsSection-D9lpSvnH.js` and replace its export with a component that returns null. Find the default export and make the component render nothing.

## 2. Add a return link to daily-tips.html

Read `/Users/fudongli/Projects/poker_analysis/daily-tips.html`. 

Inside the `.brand` h1 element (which currently says `The River — Daily Tips`), wrap it in an anchor tag that links to `./index.html`. The brand text should now link back to The River main page.

So change:
`<h1 class="brand">The River <span>— Daily Tips</span></h1>`
to:
`<h1 class="brand"><a href="./index.html" style="color:inherit;text-decoration:none">The River <span>— Daily Tips</span></a></h1>`

Or better, just make the whole brand text clickable to go to `./index.html`.

## IMPORTANT
- Edit the files directly (do NOT create generator scripts)
- After editing the JS files, verify syntax with `node --check assets/index-nzS1R7TH.js` and `node --check assets/DailyTipsSection-D9lpSvnH.js`
- All paths use `./` prefix (subdirectory-safe)
