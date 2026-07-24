"""
Lesson Activation Tracker
=========================
Operationalizes the memory lifecycle ACTIVATE + REVIEW phases.

Tracks which lessons fire, calculates effective λ (edge-of-chaos parameter),
and generates structured activation log entries.

Usage:
    python tools/lesson_activation_tracker.py log "R02" "构建/改文件" Y Y Y
    python tools/lesson_activation_tracker.py status   → show recent stats
    python tools/lesson_activation_tracker.py lambda    → effective λ calc
"""

import sys
import json
import os
from datetime import datetime
from collections import defaultdict

LESSONS_LOG = os.path.join(os.path.dirname(__file__), "..", "memory", "lesson-activation-log.md")
LESSONS_MD = os.path.join(os.path.dirname(__file__), "..", "memory", "lessons.md")

# ── Helpers ──────────────────────────────────────────────────────────

SEVERITY_WEIGHTS = {"RED": 3.0, "YELLOW": 2.0, "GREEN": 1.0}

def now_str():
    return datetime.now().strftime("%H:%M")

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def parse_log():
    """Parse activation log into structured records."""
    if not os.path.exists(LESSONS_LOG):
        return []
    
    with open(LESSONS_LOG, "r", encoding="utf-8") as f:
        text = f.read()
    
    records = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        # Detect table separator line (e.g., |---|---|---|...)
        if stripped.replace("|", "").replace("-", "").strip() == "":
            in_table = True
            continue
        if not in_table:
            continue
        
        parts = [p.strip() for p in stripped.split("|")]
        # Skip header row (column names)
        if len(parts) < 7:
            continue
        # Skip header row if it contains Chinese headers like '时间'
        if any(kw in stripped for kw in ['教训ID', '行动类型', '时间']):
            continue
        
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue

        try:
            time_str = parts[1]
            lesson_id = parts[2]
            action = parts[3]
            activated = parts[4].strip().upper() == "Y"
            executed = parts[5].strip().upper() == "Y"
            verified = parts[6].strip().upper() == "Y"
            note = parts[7] if len(parts) > 7 else ""
        except (IndexError, ValueError):
            continue

        records.append({
            "time": time_str,
            "lesson_id": lesson_id,
            "action": action,
            "activated": activated,
            "executed": executed,
            "verified": verified,
            "note": note,
        })
    
    return records


def parse_lesson_severity():
    """Extract lesson ID → severity mappings from lessons.md."""
    if not os.path.exists(LESSONS_MD):
        return {}
    
    with open(LESSONS_MD, "r", encoding="utf-8") as f:
        text = f.read()
    
    import re
    result = {}
    for line in text.splitlines():
        line = line.strip()
        # Match "#### R##" or "#### Y##" or "#### G##" (4 hashes in lessons.md)
        m = re.match(r'^#{3,4}\s+([RGY]\d+)', line)
        if m:
            lid = m.group(1)
            if lid.startswith('R'):
                result[lid] = 'RED'
            elif lid.startswith('Y'):
                result[lid] = 'YELLOW'
            elif lid.startswith('G'):
                result[lid] = 'GREEN'

    return result


# ── Commands ─────────────────────────────────────────────────────────

def cmd_log(args):
    """Log a lesson activation entry."""
    if len(args) < 4:
        print("Usage: log <lesson_id> <action_type> <activated(Y/N)> <executed(Y/N)> [verified(Y/N)] [note]")
        return 1
    
    lesson_id = args[0]
    action = args[1]
    activated = args[2].upper() == "Y"
    executed = args[3].upper() == "Y"
    verified = args[4].upper() == "Y" if len(args) > 4 else False
    note = " ".join(args[5:]) if len(args) > 5 else ""

    entry = f"| {now_str()} | {lesson_id} | {action} | {'Y' if activated else 'N'} | {'Y' if executed else 'N'} | {'Y' if verified else 'N'} | {note} |"
    
    # Find the right date section
    date_header = f"## {today_str()}"
    
    with open(LESSONS_LOG, "r", encoding="utf-8") as f:
        text = f.read()
    
    if date_header not in text:
        # Need to create section
        # Find the last ## header or append
        if text.strip().endswith("|"):
            text += "\n"
        text += f"\n## {today_str()}\n\n| 时间 | 教训ID | 行动类型 | 激活 | 执行 | 验证 | 备注 |\n|------|--------|---------|------|------|------|------|\n"
        text += entry + "\n"
    else:
        # Insert after the table header line for today
        lines = text.splitlines()
        new_lines = []
        found_date = False
        in_table_header = False
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == date_header:
                found_date = True
            if not found_date:
                continue
            # After date header, look for existing table separator
            if line.strip() == "|---|---|---|---|---|---|---|" or "------" in line:
                in_table_header = True
                continue
            if in_table_header and line.strip().startswith("| "):
                new_lines.append(entry)
                in_table_header = False
                inserted = True
        
        if not inserted:
            new_lines.append("\n" + entry)
        
        text = "\n".join(new_lines)
    
    with open(LESSONS_LOG, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"[OK] Logged {lesson_id} ({action}) | A:{activated} E:{executed} V:{verified}")
    return 0


def cmd_status(args):
    """Show recent activation statistics."""
    records = parse_log()
    if not records:
        print("No activation records found.")
        return 0

    severities = parse_lesson_severity()

    # Stats
    total = len(records)
    activated = sum(1 for r in records if r["activated"])
    executed = sum(1 for r in records if r["executed"])
    verified = sum(1 for r in records if r["verified"])

    print(f"Lesson Activation Status (total: {total})")
    print(f"{'='*50}")
    print(f"  Activated:  {activated}/{total} ({100*activated/total:.0f}%)")
    print(f"  Executed:   {executed}/{total} ({100*executed/total:.0f}%)")
    print(f"  Verified:   {verified}/{total} ({100*verified/total:.0f}%)")
    print()

    # Per-lesson breakdown
    by_lesson = defaultdict(list)
    for r in records:
        by_lesson[r["lesson_id"]].append(r)

    print(f"{'Lesson':<10} {'Severity':<10} {'Count':<6} {'Act%':<6} {'Exe%':<6}")
    print(f"{'-'*40}")
    for lid in sorted(by_lesson.keys()):
        rs = by_lesson[lid]
        n = len(rs)
        act_p = 100 * sum(1 for r in rs if r["activated"]) / n
        exe_p = 100 * sum(1 for r in rs if r["executed"]) / n
        sev = severities.get(lid, "?")
        print(f"{lid:<10} {sev:<10} {n:<6} {act_p:<6.0f}% {exe_p:<6.0f}%")

    return 0


def cmd_lambda(args):
    """
    Calculate effective λ (edge-of-chaos parameter).
    
    λ = (weighted activation rate) mapped to [0, 1]
    λ < 0.25: too ordered (selective, lessons never fire)
    λ 0.25-0.50: edge of chaos (ideal)
    λ > 0.50: too chaotic (lessons don't stick)
    """
    records = parse_log()
    if not records:
        print("No activation records. Cannot calculate λ.")
        return 0

    severities = parse_lesson_severity()

    # Weighted activation
    total_weight = 0.0
    activated_weight = 0.0

    for r in records:
        sev = severities.get(r["lesson_id"], "YELLOW")
        w = SEVERITY_WEIGHTS.get(sev, 2.0)
        total_weight += w
        if r["activated"]:
            activated_weight += w

    if total_weight == 0:
        print("No weight data. λ = N/A")
        return 0

    raw_lambda = activated_weight / total_weight
    
    print(f"Effective λ = {raw_lambda:.3f}")
    print()

    if raw_lambda < 0.25:
        zone = "[BLUE] TOO ORDERED - lessons rarely fire, rigid behavior"
    elif raw_lambda <= 0.50:
        zone = "[GREEN] EDGE OF CHAOS - adaptive, reliable, flexible"
    else:
        zone = "[RED] TOO CHAOTIC - lessons don't stick, unpredictable"
    
    print(f"Zone: {zone}")
    print()
    
    # Per lesson group
    print(f"  Group breakdown:")
    for group in ["RED", "YELLOW", "GREEN"]:
        group_records = [r for r in records if severities.get(r["lesson_id"]) == group]
        if group_records:
            gw = len(group_records) * SEVERITY_WEIGHTS[group]
            ga = sum(SEVERITY_WEIGHTS[group] for r in group_records if r["activated"])
            gr = ga / gw if gw > 0 else 0
            print(f"    {group:<10}: {gr:.2f} activation rate ({len(group_records)} records)")

    return 0


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tools/lesson_activation_tracker.py log <lesson_id> <action_type> <activated(Y/N)> <executed(Y/N)> [verified(Y/N)] [note]")
        print("  python tools/lesson_activation_tracker.py status")
        print("  python tools/lesson_activation_tracker.py lambda")
        return 1
    
    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "log": cmd_log,
        "status": cmd_status,
        "lambda": cmd_lambda,
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        return 1

    return commands[cmd](args)


if __name__ == "__main__":
    sys.exit(main())
