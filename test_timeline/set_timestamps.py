"""
Stamp test_timeline files with the correct historical timestamps.
Run this once from the test_timeline directory OR from the project root.

Usage:
    python test_timeline/set_timestamps.py
"""

import os
import time
from datetime import datetime

# Map filename -> (modified_time as "YYYY-MM-DD HH:MM:SS")
# Matches the schedule in README.md
TIMESTAMPS = {
    "initial_case_notes.txt":   "2026-01-10 09:00:00",
    "suspect_photo.jpg":         "2026-01-10 14:30:00",
    "email_thread.txt":          "2026-01-12 10:15:00",
    "financial_records.xlsx":    "2026-01-13 16:45:00",
    "server_access.log":         "2026-01-15 08:00:00",
    "security_footage.jpg":      "2026-01-15 08:30:00",
    "interview_transcript.txt":  "2026-02-10 11:00:00",
    "evidence_photos.zip":       "2026-02-10 11:15:00",
    "forensic_report.pdf":       "2026-02-12 15:30:00",
    "network_logs.log":          "2026-02-15 09:45:00",
    "witness_statement.docx":    "2026-02-20 14:00:00",
    "final_analysis.txt":        "2026-03-01 10:00:00",
    "case_summary.pdf":          "2026-03-01 10:30:00",
    "supplemental_evidence.csv": "2026-03-05 13:20:00",
    "closing_report.docx":       "2026-03-15 16:00:00",
}

# Find the test_timeline directory relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))

ok  = 0
err = 0

for filename, ts_str in TIMESTAMPS.items():
    filepath = os.path.join(script_dir, filename)
    if not os.path.exists(filepath):
        print(f"  MISSING : {filename}")
        err += 1
        continue

    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    epoch = dt.timestamp()

    # Set both access time and modified time
    os.utime(filepath, (epoch, epoch))
    print(f"  STAMPED : {filename}  →  {ts_str}")
    ok += 1

print(f"\nDone: {ok} stamped, {err} missing.")
print("\nYou can now upload this folder to Evidentia and the timeline")
print("will show files spread across Jan–Mar 2026 with correct activity peaks.")
