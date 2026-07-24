#!/usr/bin/env python3
"""
Lesson λ (Lambda) Analyzer

Measures the agent's "effective λ" from lesson activation patterns,
connecting Edge of Chaos theory (#003) to the Lesson Activation System.

λ = (activated_lessons) / (available_lessons_this_session)

Interpretation:
  λ ≈ 0.00-0.25 → Too ordered, rigid, lessons fire too rarely
  λ ≈ 0.25-0.50 → Edge of chaos, adaptive sweet spot
  λ ≈ 0.50-0.75 → Slightly chaotic, lessons are too reactive
  λ ≈ 1.00      → Too chaotic, every lesson fires = none sticks

Usage:
  python tools/lesson_lambda_analyzer.py
"""

import re
import json
from datetime import datetime, date
from pathlib import Path

MEMORY_DIR = Path("memory")
ACTIVATION_LOG = MEMORY_DIR / "lesson-activation-log.md"
LESSONS_FILE = MEMORY_DIR / "lessons.md"
OUTPUT_FILE = MEMORY_DIR / "lambda-metrics.json"

def parse_activation_log():
    """Parse the activation log markdown table."""
    if not ACTIVATION_LOG.exists():
        print(f"[!] Activation log not found: {ACTIVATION_LOG}")
        return {}

    text = ACTIVATION_LOG.read_text(encoding="utf-8", errors="replace")
    
    # Find sections by date headers
    daily_entries = {}
    current_date = None
    
    for line in text.split("\n"):
        # Date header: ## YYYY-MM-DD
        date_match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            daily_entries[current_date] = []
            continue
        
        # Table row: | time | ID | type | activated | executed | verified | notes |
        if current_date and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            # Filter header/footer and empty rows
            if len(parts) >= 7:
                time_id = parts[1] if len(parts) > 1 else ""
                lesson_id = parts[2] if len(parts) > 2 else ""
                action_type = parts[3] if len(parts) > 3 else ""
                activated = parts[4] if len(parts) > 4 else ""
                executed = parts[5] if len(parts) > 5 else ""
                verified = parts[6] if len(parts) > 6 else ""
                
                # Skip column headers or empty rows
                if time_id and lesson_id and lesson_id not in ("教训ID", "", " "):
                    daily_entries[current_date].append({
                        "time": time_id,
                        "lesson_id": lesson_id,
                        "action_type": action_type,
                        "activated": activated == "Y",
                        "executed": executed == "Y",
                        "verified": verified == "Y",
                        "notes": parts[7] if len(parts) > 7 else "",
                    })
    
    return daily_entries

def count_available_lessons():
    """Count available lessons by severity from lessons.md."""
    if not LESSONS_FILE.exists():
        return {"RED": 0, "YELLOW": 0, "GREEN": 0}
    
    text = LESSONS_FILE.read_text(encoding="utf-8", errors="replace")
    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    
    # Count lesson IDs in each severity section
    current_sev = None
    for line in text.split("\n"):
        sev_match = re.match(r"^### (RED|YELLOW|GREEN)", line)
        if sev_match:
            current_sev = sev_match.group(1)
            continue
        # Count lesson entries: R01, Y01, G01 etc.
        if current_sev and re.match(r"^#### [RYG]\d+", line):
            counts[current_sev] += 1
    
    return counts


def compute_metrics(daily_entries):
    """Compute λ and other statistics per day."""
    available = count_available_lessons()
    total_available = sum(available.values())
    
    results = {
        "_available_lessons": {
            "RED": available["RED"],
            "YELLOW": available["YELLOW"],
            "GREEN": available["GREEN"],
            "total": total_available,
        }
    }
    
    for day, entries in sorted(daily_entries.items()):
        total = len(entries)
        if total == 0:
            continue
        
        activated = sum(1 for e in entries if e["activated"])
        executed = sum(1 for e in entries if e["executed"])
        verified = sum(1 for e in entries if e["verified"])
        
        # λ = unique lessons activated / total available lessons
        unique_activated = len(set(e["lesson_id"] for e in entries if e["activated"]))
        lam = unique_activated / total_available if total_available > 0 else 0
        
        # By severity
        red_entries = [e for e in entries if e["lesson_id"].startswith("R")]
        yellow_entries = [e for e in entries if e["lesson_id"].startswith("Y")]
        green_entries = [e for e in entries if e["lesson_id"].startswith("G")]
        
        red_activated = sum(1 for e in red_entries if e["activated"])
        yellow_activated = sum(1 for e in yellow_entries if e["activated"])
        green_activated = sum(1 for e in green_entries if e["activated"])
        
        # Activation frequency: how often the same lessons fire per session
        activation_intensity = total / unique_activated if unique_activated > 0 else 0
        
        # Execution fidelity: how many activated lessons actually executed?
        exec_fidelity = executed / activated if activated > 0 else 0
        verify_fidelity = verified / executed if executed > 0 else 0
        
        results[day] = {
            "total_log_entries": total,
            "unique_activated": unique_activated,
            "available_lessons": total_available,
            "activated": activated,
            "executed": executed,
            "verified": verified,
            "lambda": round(lam, 4),
            "activation_intensity": round(activation_intensity, 2),
            "edge_of_chaos": 0.25 <= lam <= 0.50,
            "by_severity": {
                "RED": {"entries": len(red_entries), "activated": red_activated, "available": available["RED"], "rate": round(red_activated / available["RED"], 4) if available["RED"] > 0 else 0},
                "YELLOW": {"entries": len(yellow_entries), "activated": yellow_activated, "available": available["YELLOW"], "rate": round(yellow_activated / available["YELLOW"], 4) if available["YELLOW"] > 0 else 0},
                "GREEN": {"entries": len(green_entries), "activated": green_activated, "available": available["GREEN"], "rate": round(green_activated / available["GREEN"], 4) if available["GREEN"] > 0 else 0},
            },
            "execution_fidelity": round(exec_fidelity, 4),
            "verification_fidelity": round(verify_fidelity, 4),
            "interpretation": interpret_lambda(lam),
        }
    
    return results

def interpret_lambda(lam):
    """Map λ value to a behavioral interpretation."""
    if lam <= 0.10:
        return "CRITICAL: Too ordered — lessons are rarely checked, likely ignored in practice"
    elif lam <= 0.25:
        return "RIGID: Below edge of chaos — reliable but lacks flexibility for novel situations"
    elif lam <= 0.40:
        return "EDGE+: Adaptive zone — structured with room for exploration"
    elif lam <= 0.50:
        return "EDGE: Optimal — balanced between order and chaos"
    elif lam <= 0.70:
        return "CHAOTIC-: Slightly reactive — too many lessons firing, may dilute focus"
    elif lam <= 0.90:
        return "CHAOTIC: Unstable — nearly every trigger fires, lessons lose weight"
    else:
        return "OVERLOADED: Every lesson is 'activated' — none is truly prioritized"

def print_report(results):
    """Print a human-readable report."""
    print("=" * 65)
    print("  LESSON λ (LAMBDA) ANALYZER — Edge of Chaos in Agent Memory")
    print("=" * 65)
    
    days = sorted(results.keys())
    if not days:
        print("\n  No activation data found yet.")
        print("  Start tracking activations in memory/lesson-activation-log.md")
        return
    
    print(f"\n  Days tracked: {len(days)}")
    print(f"  Date range: {days[0]} → {days[-1]}")
    print()
    
    avail = results.get("_available_lessons", {})
    if avail:
        print(f"  Available lessons: RED={avail['RED']}, YELLOW={avail['YELLOW']}, GREEN={avail['GREEN']} (total={avail['total']})")
    print()
    
    for day in days:
        if day.startswith("_"):
            continue
        d = results[day]
        eco = "[OK]" if d["edge_of_chaos"] else "[--]"
        print(f"  {day} | lambda={d['lambda']:.3f} | {eco} Edge? | "
              f"unique={d['unique_activated']}/{d['available_lessons']} | "
              f"entries={d['total_log_entries']} | "
              f"intensity={d['activation_intensity']}x | "
              f"exec={d['execution_fidelity']:.2f} ver={d['verification_fidelity']:.2f}")
        print(f"    => {d['interpretation']}")
        for sev, sdata in d["by_severity"].items():
            if sdata["available"] > 0:
                print(f"       [{sev}]: {sdata['activated']}/{sdata['available']} avail ({sdata['rate']:.2%})")
    
    # Trend
    if len(days) >= 3:
        lams = [results[d]["lambda"] for d in days[-3:]]
        trend = "↑" if lams[-1] > lams[0] else ("↓" if lams[-1] < lams[0] else "→")
        print(f"\n  Trend (last 3): {lams[0]:.3f} → {lams[1]:.3f} → {lams[2]:.3f} {trend}")
    
    print("\n" + "=" * 65)

def save_results(results):
    """Save metrics to JSON for trend tracking."""
    existing = {}
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    
    existing["last_updated"] = datetime.now().isoformat()
    existing["total_days_tracked"] = len(results)
    existing["days"] = results
    
    OUTPUT_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [Saved to {OUTPUT_FILE}]")

if __name__ == "__main__":
    entries = parse_activation_log()
    if not entries:
        print("[!] No activation entries found.")
        print(f"    Make sure {ACTIVATION_LOG} exists with entries in format:")
        print("    ## YYYY-MM-DD")
        print("    | time | lesson_id | action_type | activated(Y/N) | executed(Y/N) | verified(Y/N) | notes |")
        exit(0)
    
    metrics = compute_metrics(entries)
    print_report(metrics)
    save_results(metrics)
