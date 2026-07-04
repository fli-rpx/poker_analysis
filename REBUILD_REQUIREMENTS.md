# Poker Decision Flowchart — Rebuild Requirements

## Overview
Rebuild the existing poker decision flowchart at `https://snt3wfprbaopc.kimi.page` to blend theoretical strategy with actual player data from 7,911 hands of hand history.

## Current State
The page is a React + Tailwind CSS SPA with:
- 4 selectors: Position (EP/MP/LP/Blinds), Hand (Good/Medium/Junk), Opponents (3 Aggressive/1W+2A/2W+1A/3 Weak), Stage (Pre-flop/Flop/Turn/River)
- Shows a single "Recommended Action" from a theoretical decision matrix
- Dark green theme, card-based layout
- Hosted as a Kimi Page static site

## Required Changes

### 1. Data Source
The play data is at `/Users/fudongli/.hermes/profiles/hermes4/poker/poker_flow_data.json` (81KB JSON).
Key structure:
```json
{
  "meta": { "total_hands": 7911 },
  "flows": {
    "EP|Junk|2 Weak + 1 Agg|preflop": {
      "position": "EP", "category": "Junk", "opponents": "2 Weak + 1 Agg", "stage": "preflop",
      "theoretical": "Fold",
      "total_hands": 756,
      "actions": {
        "Fold":  { "count": 533, "avg_net": -5997, "total_net": -3196136 },
        "Call":  { "count": 160, "avg_net": -11551, "total_net": -1848124 },
        "Raise": { "count": 60,  "avg_net": -16185, "total_net": -971089 }
      },
      "data_driven_best": "Fold",
      "data_driven_best_avg": -5997
    }
  }
}
```

Embed this JSON directly in the JS bundle (inline it at build time).

### 2. UI Changes — Results Display

When user selects a flow, show two columns side by side:

**Left Column — Theoretical (current behavior)**
- Icon: 📖 or book
- Label: "Strategy Guide"
- Shows: recommended action from the matrix
- Small text: "Based on standard 4-handed GTO framework"

**Right Column — Your Data (new)**
- Icon: 📊 or chart
- Label: "Your Track Record"
- Shows:
  - **Best action** (the one with highest avg_net in your data) with chip icon
  - **Sample size**: "Based on X hands" with a visual confidence indicator:
    - ≥ 50 hands: 🟢 High confidence
    - 20-49 hands: 🟡 Medium confidence
    - 5-19 hands: 🟠 Low confidence
    - < 5 hands: ⚪ Insufficient data
  - **Net per hand**: big number, green if positive, red if negative
  - **Action comparison table** showing all actions you've taken with count and avg net

**When both agree**: Show ✅ "Data confirms strategy" green badge
**When they disagree**: Show ⚠️ "Your data suggests a different approach" amber badge, with explanation

### 3. New Feature — "By the Numbers" Section

Below the two-column result, add a section showing:
- Total hands in this flow
- Win/Loss record
- Showdown win rate (if available)
- Most common action you take (actual habit vs recommended)

### 4. Visual Design
- Keep existing dark green theme (Tailwind classes: `bg-gradient-to-br from-[#0a1f0a] via-[#0d2818] to-[#0a1f14]`)
- Use emerald/gold/red color scheme
- Cards for the two-column layout
- Responsive — works on mobile (single column on small screens, two columns on desktop)
- Chip amounts formatted with commas (e.g. "+4,965")

### 5. Architecture
- Single HTML file with embedded CSS/JS (Kimi Page static site)
- React + Tailwind (same stack as current page)
- Data embedded as a JSON constant
- No external API calls needed
- Build output to `/tmp/poker-decision-chart/`

### 6. File Structure
```
/tmp/poker-decision-chart/
  index.html          # Single file SPA
```

## Implementation Steps

1. Read the JSON data file at `/Users/fudongli/.hermes/profiles/hermes4/poker/poker_flow_data.json`
2. Build a single HTML file that implements the above design
3. The page must work without any build step (pure React via CDN or pre-compiled)
4. Test locally then prepare for Kimi Page deployment

## Key Flows Highlight Examples

### Best flows (data-driven):
| Flow | Best Action | Avg Net | Sample |
|------|:---------:|:-------:|:-----:|
| Blinds + Medium + 1W+2A | All-In | +1,418/hand | 11h |
| MP + Good + 1W+2A | All-In | +165,877/hand | 6h |
| EP + Junk + 1W+2A | Raise | +135,884/hand | 18h |
| CO + Medium + 2W+1A | Raise | +65,251/hand | 22h |
| CO + Medium + 3 Weak | Call | +12,313/hand | 36h |

### Worst flows (leaks):
| Flow | Worst Pattern | Avg Net | Sample |
|------|:-----------:|:-------:|:-----:|
| Blinds + Junk + 3 Weak | Call | -11,976/hand | 253h |
| EP + Junk + 3 Weak | Call | -11,551/hand | 160h |
| CO + Good + 2W+1A | Raise | -16,588/hand | 42h |
| BTN + Good + 3 Weak | Call | -7,034/hand | 16h |
| EP + Junk + 2W+1A | Call | -11,551/hand | 160h |
