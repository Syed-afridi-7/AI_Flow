#!/usr/bin/env python3
"""
beats.py - turn a Reel script into a timed beat sheet before you record it.

Calculates 5-beat spoken timing (30-45s, 75-100 words) and flags:
- A hook running past 3.0s
- Any beat running over 4.0s without a visual shift
- Abstract runs with no numbers/concrete markers
- Total length vs target duration (30-45s)
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Union

WORD_RE = re.compile(r"[A-Za-z0-9$%'’-]+")
SENT_RE = re.compile(r"[^.!?]+[.!?]*")
CONCRETE_RE = re.compile(r"\$\s?\d|\b\d[\d,.]*\b|(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE)
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "for",
    "with", "that", "this", "it", "is", "are", "was", "were", "be", "been",
    "you", "your", "i", "my", "me", "we", "our", "they", "them", "he", "she",
    "so", "just", "not", "no", "do", "did", "does", "have", "has", "had",
    "will", "can", "at", "as", "by", "from", "out", "up", "off", "one", "all",
}

HOOK_WINDOW = 3.0        # seconds. Past this, thumb has already decided.
MAX_BEAT = 4.0           # seconds on one idea with no change on screen.
ABSTRACT_RUN = 3         # beats in a row with nothing checkable in them.

# Standard 5-beat structure conventions:
DEFAULT_5_BEAT_LABELS = [
    "HOOK",
    "PROBLEM",
    "CORE_VALUE",
    "PAYOFF",
    "CTA_LOOP"
]


def words(text: str) -> list:
    # "$18,000" is one word when it is spoken, so it is one word here too.
    return WORD_RE.findall(re.sub(r"(?<=\d),(?=\d)", "", text))


def pretty(token: str) -> str:
    """Put the thousands separator back for display."""
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1,", token)


def tc(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def split_beats(raw: str, wps: float) -> list:
    """One line is one beat, unless a line is too long to be one."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if len(words(line)) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        # Long paragraph: break at sentence ends so timings mean something
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and len(words(candidate)) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def analyse(raw: str, wpm: float = 165.0, target: Optional[float] = None) -> Optional[dict]:
    wps = wpm / 60.0
    beats = split_beats(raw, wps)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = len(words(text))
        dur = n / wps
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": n,
            "text": text,
            "concrete": len(CONCRETE_RE.findall(text)),
            "label": "",
            "flags": [],
        })
        clock += dur
    total = clock

    # Label structural positions
    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "HOOK"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "HOOK" else "HOOK/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MID"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(f"hook runs {rows[0]['dur']:.1f}s, past the {HOOK_WINDOW:.0f}s mark")
        notes.append(f"Beat 1 takes {rows[0]['dur']:.1f}s to say. Cut it to "
                     f"{int(HOOK_WINDOW * wps)} words or fewer, or the hook lands after "
                     "the decision has been made.")
    if rows[0]["concrete"] == 0:
        notes.append("Beat 1 has no number and no name in it. Hooks without something "
                     "checkable are the ones that get scrolled.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{r['dur']:.1f}s on one beat")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Beat(s) {', '.join(map(str, long_beats))} run past {MAX_BEAT:.0f}s. "
                     "Either split the line or change what is on screen inside it. "
                     "A static frame is where people leave.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"Beats {start}-{r['n']} have nothing concrete in them. "
                             "Put a number, a name or a price in one of them.")
        else:
            run, start = 0, None

    # Loop check
    first = {w.lower() for w in words(rows[0]["text"]) if w.lower() not in STOPWORDS}
    last = {w.lower() for w in words(rows[-1]["text"]) if w.lower() not in STOPWORDS}
    loop = sorted(pretty(w) for w in first & last)
    if loop:
        notes.append(f"Loops: the last beat repeats \"{', '.join(loop[:3])}\" from the hook. "
                     "Second watches are free reach.")
    else:
        notes.append("No loop. The last beat shares no word with the hook, so the video "
                     "ends flat. Echoing one word from beat 1 is the cheapest replay you get.")

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(f"Length is on target ({total:.1f}s against {target}s).")
        elif delta > 0:
            notes.append(f"{delta:.1f}s over target. Cut about {int(delta * wps)} words.")
        else:
            notes.append(f"{-delta:.1f}s under target. Either add {int(-delta * wps)} words "
                          "or shoot it short. Short is usually right.")

    return {
        "wpm": wpm,
        "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a: dict, out=sys.stdout):
    head = (f"BEAT SHEET  ·  {a['total_words']} words  ·  ~{a['total_seconds']:.1f}s "
            f"at {a['wpm']} wpm" + (f"  ·  target {a['target']}s" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<8}" if r["label"] else " " * 8
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<8}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def calculate_5_beat_timing(
    content: Union[str, List[str], List[dict]],
    target_seconds: int = 35,
    wpm: float = 165.0,
) -> dict:
    """
    Calculate spoken timing for a 5-beat Reel script.
    Optimized for short-form video standards:
    - Target spoken timing: 30-45s
    - Target total word count: 75-100 words (at ~165 wpm)
    - Beat 1 (Hook): <= 3.0s (5-10 words)
    - Beat 2 (Problem/Setup): 4-8s (12-20 words)
    - Beat 3 (Core Value/Solution): 12-20s (30-45 words)
    - Beat 4 (Payoff/Proof): 6-10s (15-25 words)
    - Beat 5 (CTA/Loop): 4-6s (10-15 words)
    """
    wps = wpm / 60.0

    if isinstance(content, list):
        if content and isinstance(content[0], dict):
            raw_lines = [item.get("text", "") for item in content]
        else:
            raw_lines = [str(item) for item in content]
        script_text = "\n".join(line.strip() for line in raw_lines if line.strip())
    else:
        script_text = content.strip()
        if "\n" not in script_text:
            # Split by punctuation
            script_text = re.sub(r"(?<=[.!?])\s+", "\n", script_text)

    analysis = analyse(script_text, wpm=wpm, target=target_seconds)
    if not analysis or not analysis["beats"]:
        return {
            "valid": False,
            "total_words": 0,
            "total_seconds": 0.0,
            "beat_count": 0,
            "words_in_range": False,
            "duration_in_range": False,
            "beats": [],
            "warnings": ["Script is empty"],
        }

    detected_beats = analysis["beats"]
    total_words = analysis["total_words"]
    total_seconds = analysis["total_seconds"]

    # Align labels with 5-beat schema if 5 beats present
    beats_output = []
    default_cues = [
        "Hook overlay / eye-level direct address",
        "Problem demonstration / screen record zoom",
        "Step-by-step resolution / code or product highlight",
        "Before/After comparison or concrete metric proof",
        "Loop back to hook opener / save CTA",
    ]

    for idx, r in enumerate(detected_beats):
        if idx < len(DEFAULT_5_BEAT_LABELS):
            label = DEFAULT_5_BEAT_LABELS[idx]
        else:
            label = r.get("label") or f"BEAT_{idx + 1}"

        cue = default_cues[idx] if idx < len(default_cues) else "Screen motion / visual cut"

        beats_output.append({
            "beat": idx + 1,
            "section": label,
            "start": tc(r["start"]),
            "end": tc(r["start"] + r["dur"]),
            "duration": r["dur"],
            "words": r["words"],
            "text": r["text"],
            "cue": cue,
            "flags": r["flags"],
        })

    words_ok = 75 <= total_words <= 100
    duration_ok = 30.0 <= total_seconds <= 45.0
    hook_ok = detected_beats[0]["dur"] <= HOOK_WINDOW

    warnings = []
    if not (75 <= total_words <= 100):
        warnings.append(
            f"Word count {total_words} outside recommended 75-100 range "
            f"({'under by ' + str(75 - total_words) if total_words < 75 else 'over by ' + str(total_words - 100)})"
        )
    if not (30.0 <= total_seconds <= 45.0):
        warnings.append(
            f"Total duration {total_seconds:.1f}s outside recommended 30-45s window"
        )
    if not hook_ok:
        warnings.append(
            f"Hook duration {detected_beats[0]['dur']:.1f}s exceeds 3.0s limit"
        )
    if len(detected_beats) != 5:
        warnings.append(
            f"Beat count is {len(detected_beats)} (standard structure expects 5 beats)"
        )

    return {
        "valid": words_ok and duration_ok and hook_ok,
        "total_words": total_words,
        "total_seconds": round(total_seconds, 2),
        "beat_count": len(detected_beats),
        "words_in_range": words_ok,
        "duration_in_range": duration_ok,
        "hook_valid": hook_ok,
        "wpm": wpm,
        "beats": beats_output,
        "warnings": warnings,
        "notes": analysis["notes"],
    }


def generate_beat_sheet(script: str, target_seconds: int = 30) -> list:
    """Convenience helper for generating structured beat sheets."""
    if "\n" not in script:
        script = re.sub(r"(?<=[.!?])\s+", "\n", script)
    analysis = analyse(script, target=target_seconds)
    beats_data = (analysis.get("beats") or analysis.get("rows")) if analysis else None
    if not beats_data:
        return [
            {"section": "HOOK", "start": "0:00", "end": "0:03", "text": script, "cue": "Look at camera / code overlay"}
        ]
    beats = []
    for r in beats_data:
        label = r.get("label") or "CONTENT"
        beats.append({
            "section": label,
            "start": tc(r["start"]),
            "end": tc(r["start"] + r["dur"]),
            "duration": r["dur"],
            "text": r["text"],
            "cue": "Camera shot / screen zoom" if label != "CTA" else "Call to action on screen"
        })
    return beats


def main():
    ap = argparse.ArgumentParser(description="Time a Reel script into a beat sheet.")
    ap.add_argument("input", nargs="?", default="-", help="script file, or - for stdin")
    ap.add_argument("--wpm", type=float, default=165, help="speaking rate (default 165)")
    ap.add_argument("--target", type=float, help="target length in seconds")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timing-5beat", action="store_true", help="verify 5-beat timing rules (30-45s, 75-100w)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()

    if args.timing_5beat:
        res = calculate_5_beat_timing(raw, target_seconds=int(args.target or 35), wpm=args.wpm)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res["valid"] else 1)

    a = analyse(raw, wpm=args.wpm, target=args.target)
    if not a:
        print("empty script", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
