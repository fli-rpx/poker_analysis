#!/usr/bin/env python3
"""
Poker Analysis — Daily Refresh Script

Runs daily to:
1. Append the latest tip to data/tips.json
2. Run poker-review.py --baseline and append snapshot to data/analysis_history.json
3. Git add, commit, and push the updated data files
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
TIPS_JSON = DATA_DIR / "tips.json"
ANALYSIS_JSON = DATA_DIR / "analysis_history.json"

LAST_TIP_DATE_FILE = Path("/Users/fudongli/.hermes/profiles/hermes4/poker/last_tip_date.txt")
TIP_HISTORY_FILE = Path("/Users/fudongli/.hermes/profiles/hermes4/skills/leisure/poker-companion/references/tip-history.md")
POKER_REVIEW_SCRIPT = Path("/Users/fudongli/.hermes/profiles/hermes4/poker/poker-review.py")

# ─── Helpers ────────────────────────────────────────────────────────

def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def run_command(cmd, cwd=None, capture=True):
    kwargs = {"cwd": cwd or str(REPO_ROOT)}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    result = subprocess.run(cmd, shell=True, **kwargs)
    return result


def parse_tip_history():
    """Parse tip-history.md and return a dict of date -> {title, category}."""
    tips = {}
    if not TIP_HISTORY_FILE.exists():
        return tips

    text = TIP_HISTORY_FILE.read_text(encoding="utf-8")
    # Match table rows like: | Jun 10 | Blind Stealing — Profit From Position | positional play | ✅ |
    pattern = re.compile(
        r"\|\s*([A-Za-z]+\s+\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*[^|]+\|"
    )
    for match in pattern.finditer(text):
        raw_date = match.group(1).strip()
        title = match.group(2).strip()
        category = match.group(3).strip()
        # Normalize date to YYYY-MM-DD (assume current year 2026)
        try:
            dt = datetime.strptime(f"2026 {raw_date}", "%Y %b %d")
            date_key = dt.strftime("%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(f"2026 {raw_date}", "%Y %B %d")
                date_key = dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        tips[date_key] = {"title": title, "category": category}

    return tips


def generate_tip_content(title, category):
    """Generate placeholder content for a tip."""
    return (
        f"Today's focus: {title}. "
        f"This falls under the {category} category. "
        f"Review the principle of First God > Second Odds > Last Cards before your session. "
        f"Attack like a leopard — unexpected, careful, watchful."
    )


def parse_review_output(output):
    """Parse poker-review.py --baseline output and return metrics dict."""
    metrics = {
        "junk_pct": None,
        "junk_showdown_win_rate": None,
        "high_pp_win_rate": None,
        "high_pp_volume": None,
        "overall_showdown_win_rate": None,
        "total_hands": None,
    }

    # Total hands
    m = re.search(r"Total hands seen:\s*(\d+)", output)
    if m:
        metrics["total_hands"] = int(m.group(1))

    # JUNK%: "4549 of 7953 hands ( 57%)"
    m = re.search(r"(\d+)\s+of\s+(\d+)\s+hands\s*\(\s*(\d+)%?\s*\)", output)
    if m:
        metrics["junk_pct"] = int(m.group(3))

    # High PP volume from breakdown line: "High PP (TT+) 170 2%"
    m = re.search(r"High PP \(TT\+\)\s+(\d+)\s+(\d+)%", output)
    if m:
        metrics["high_pp_volume"] = int(m.group(2))

    # Note: poker-review.py does not output showdown win rates.
    # Those remain None and will not overwrite existing values in the snapshot.
    return metrics


def configure_git_auth():
    """Configure git auth using GH_TOKEN if available."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return

    # Get the current remote URL
    result = run_command("git remote get-url origin", capture=True)
    if result.returncode != 0:
        return

    url = result.stdout.strip()
    # If it's an HTTPS URL, inject the token
    if url.startswith("https://github.com/"):
        new_url = f"https://{token}@github.com/{url.split('github.com/')[1]}"
        run_command(f"git remote set-url origin {new_url}", capture=False)
        print("Configured GitHub token for push.")


def git_commit_and_push(files_to_add, commit_msg):
    """Stage files, commit, and push."""
    for f in files_to_add:
        run_command(f"git add {f}")

    # Check if there are changes to commit
    result = run_command("git diff --cached --quiet")
    if result.returncode == 0:
        print("No changes to commit.")
        return

    run_command(f'git commit -m "{commit_msg}"')
    push_result = run_command("git push origin main")
    if push_result.returncode != 0:
        print(f"Git push failed:\n{push_result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("Pushed to origin/main.")


# ─── Main ───────────────────────────────────────────────────────────

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Optionally read last_tip_date.txt to cross-check
    if LAST_TIP_DATE_FILE.exists():
        last_date = LAST_TIP_DATE_FILE.read_text(encoding="utf-8").strip()
        print(f"Last tip date from file: {last_date}")
        today_str = last_date  # Use the system's recorded date

    print(f"Processing for date: {today_str}")

    updated_files = []

    # ── 1. Update tips.json ────────────────────────────────────────
    tips_data = load_json(TIPS_JSON)
    if "tips" not in tips_data:
        tips_data["tips"] = []

    existing_dates = {t["date"] for t in tips_data["tips"]}

    if today_str not in existing_dates:
        history = parse_tip_history()
        tip_info = history.get(today_str)

        if tip_info:
            title = tip_info["title"]
            category = tip_info["category"]
        else:
            title = f"Daily Tip — {today_str}"
            category = "general"

        # Try to find richer content from any export mechanism
        content = generate_tip_content(title, category)
        export_file = Path(f"/Users/fudongli/.hermes/profiles/hermes4/poker/tips/{today_str}.txt")
        if export_file.exists():
            content = export_file.read_text(encoding="utf-8").strip()

        new_tip = {
            "date": today_str,
            "title": title,
            "content": content,
            "category": category,
        }
        tips_data["tips"].append(new_tip)
        save_json(TIPS_JSON, tips_data)
        updated_files.append("data/tips.json")
        print(f"Appended new tip for {today_str}: {title}")
    else:
        print(f"Tip for {today_str} already exists. Skipping.")

    # ── 2. Update analysis_history.json ────────────────────────────
    analysis_data = load_json(ANALYSIS_JSON)
    if "snapshots" not in analysis_data:
        analysis_data["snapshots"] = []

    existing_snap_dates = {s["date"] for s in analysis_data["snapshots"]}

    if today_str not in existing_snap_dates:
        if POKER_REVIEW_SCRIPT.exists():
            print("Running poker-review.py --baseline ...")
            result = subprocess.run(
                ["python3", str(POKER_REVIEW_SCRIPT), "--baseline"],
                capture_output=True,
                text=True,
            )
            review_output = result.stdout + result.stderr
            metrics = parse_review_output(review_output)
            print(f"Parsed metrics: {metrics}")
        else:
            print(f"Warning: {POKER_REVIEW_SCRIPT} not found. Using zeros.")
            metrics = {
                "junk_pct": 0,
                "junk_showdown_win_rate": None,
                "high_pp_win_rate": None,
                "high_pp_volume": 0,
                "overall_showdown_win_rate": None,
                "total_hands": 0,
            }

        snapshot = {
            "date": today_str,
            "junk_pct": metrics["junk_pct"] if metrics["junk_pct"] is not None else 0,
            "junk_showdown_win_rate": metrics["junk_showdown_win_rate"] if metrics["junk_showdown_win_rate"] is not None else 0,
            "high_pp_win_rate": metrics["high_pp_win_rate"] if metrics["high_pp_win_rate"] is not None else 0,
            "high_pp_volume": metrics["high_pp_volume"] if metrics["high_pp_volume"] is not None else 0,
            "overall_showdown_win_rate": metrics["overall_showdown_win_rate"] if metrics["overall_showdown_win_rate"] is not None else 0,
            "total_hands": metrics["total_hands"] if metrics["total_hands"] is not None else 0,
        }

        analysis_data["snapshots"].append(snapshot)
        save_json(ANALYSIS_JSON, analysis_data)
        updated_files.append("data/analysis_history.json")
        print(f"Appended analysis snapshot for {today_str}.")
    else:
        print(f"Analysis snapshot for {today_str} already exists. Skipping.")

    # ── 3. Git commit and push ─────────────────────────────────────
    if updated_files:
        configure_git_auth()
        commit_msg = f"Daily refresh: {today_str}"
        git_commit_and_push(updated_files, commit_msg)
    else:
        print("Nothing new to commit.")

    print("Done.")


if __name__ == "__main__":
    main()
