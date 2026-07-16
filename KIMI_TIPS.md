Create a single file at `/Users/fudongli/Projects/poker_analysis/daily-tips.html`.

This is a fully self-contained static HTML page (all CSS and JS inline) that shows 48 poker tips in a split-pane layout.

## DATA

Read the tips from `/Users/fudongli/Projects/poker_analysis/data/tips.json`. Embed the data INLINE as a JavaScript array in the HTML. Do NOT load from external file at runtime.

Each tip has: day (int), category (string), title (string), summary (string with \n\n between paragraphs). Also compute a date field from the day.

## LAYOUT

**Filter bar (top):** Category buttons (ALL, PREFLOP, POSTFLOP, MATH, PSYCHOLOGY, LIVE PLAY, SESSIONS) and a search input. Active filter highlighted in gold.

**Left sidebar (320px, scrollable):** List of tip items. Each shows: day circle, title, colored category badge. Click to select. Active item has gold left border highlight and gold day circle.

**Right panel:** Shows selected tip full content. Empty state when nothing selected. Smooth fade-in on switch.

## STYLE

Dark theme (#0a0a0a bg, #f5f5f0 text). Gold accent (#d4af37). Fonts: Inter (body), Playfair Display (headings) from Google Fonts. Glassmorphism feel. Custom scrollbars. Mobile responsive (sidebar slides in as overlay on small screens).

## CATEGORY COLORS

Preflop → #d4af37, Postflop → #27AE60, Math → #4A90D9, Psychology → #E74C3C, Live Play → #E67E22, Sessions → #9B59B6

Normalize category names: Mental Game→Psychology, Bankroll→Sessions, Tournament→Live Play, Live Reads→Live Play, Hand Reading→Postflop, Turn/River→Postflop, Positional→Preflop

## IMPORTANT

- Write the HTML file directly — do NOT create a generator script
- All CSS in a single <style> tag
- All JS in a single <script> tag at the bottom
- Tips data embedded inline as a JavaScript array
- Works from any subdirectory (no base tag needed)
- Must be valid when opened directly in a browser (file:// or http://)
