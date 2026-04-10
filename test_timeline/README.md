# Test Timeline Evidence Collection

This folder contains test evidence files specifically designed to rigorously test the timeline visualization system.

## Test Scenarios Covered

### 1. Date Range Testing
- Files span from January 2026 to March 2026 (3-month range)
- Tests timeline scaling and date label positioning
- Tests date range filtering functionality

### 2. Date Clustering
- Multiple files on same dates (Jan 15, Feb 10, Mar 01)
- Tests marker overlap handling
- Tests vertical offset algorithm

### 3. File Type Diversity
- Documents (.txt, .pdf, .docx)
- Images (.jpg, .png)
- Logs (.log)
- Spreadsheets (.csv, .xlsx)
- Archives (.zip)
- Tests color-coding system

### 4. Temporal Patterns
- **Early Activity Burst:** Jan 10-15 (6 files in 5 days)
- **Gap Period:** Jan 16 - Feb 09 (24 days with no activity)
- **Mid Investigation:** Feb 10-20 (5 files in 10 days)
- **Another Gap:** Feb 21 - Feb 28 (7 days)
- **Final Activity:** Mar 01-15 (4 files in 14 days)

### 5. Edge Cases
- Files on same day at different times
- Files at start of month
- Files at end of month
- Files on consecutive days
- Files with large gaps between them

## File Distribution by Date

### January 2026
- **Jan 10:** initial_case_notes.txt (09:00)
- **Jan 10:** suspect_photo.jpg (14:30)
- **Jan 12:** email_thread.txt (10:15)
- **Jan 13:** financial_records.xlsx (16:45)
- **Jan 15:** server_access.log (08:00)
- **Jan 15:** security_footage.jpg (08:30)

### February 2026
- **Feb 10:** interview_transcript.txt (11:00)
- **Feb 10:** evidence_photos.zip (11:15)
- **Feb 12:** forensic_report.pdf (15:30)
- **Feb 15:** network_logs.log (09:45)
- **Feb 20:** witness_statement.docx (14:00)

### March 2026
- **Mar 01:** final_analysis.txt (10:00)
- **Mar 01:** case_summary.pdf (10:30)
- **Mar 05:** supplemental_evidence.csv (13:20)
- **Mar 15:** closing_report.docx (16:00)

## File Type Distribution
- Documents (TXT, PDF, DOCX): 8 files (53%)
- Images (JPG, PNG): 2 files (13%)
- Logs (LOG): 2 files (13%)
- Spreadsheets (CSV, XLSX): 2 files (13%)
- Archives (ZIP): 1 file (7%)

## Timeline Testing Checklist

### Visual Rendering
- [ ] All 15 files appear on timeline
- [ ] Files correctly positioned by date
- [ ] Color coding matches file types
- [ ] Markers don't completely overlap (vertical offset works)
- [ ] Timeline scales appropriately for 3-month range

### Date Range Filtering
- [ ] Filter to January only (6 files)
- [ ] Filter to February only (5 files)
- [ ] Filter to March only (4 files)
- [ ] Filter to Jan 10-15 (6 files - early burst)
- [ ] Filter to Feb 10-20 (5 files - mid investigation)
- [ ] Filter to single day with multiple files (Jan 10, Jan 15, Feb 10, Mar 01)

### Gap Detection
- [ ] Visual gap between Jan 15 and Feb 10 (24 days)
- [ ] Visual gap between Feb 20 and Mar 01 (9 days)
- [ ] Timeline shows sparse vs dense periods

### Interaction Testing
- [ ] Hover tooltips show correct information
- [ ] Click markers opens detail dialog
- [ ] Zoom in/out works smoothly
- [ ] Scroll/pan works across full timeline
- [ ] Fit to view shows all files

### Milestone Testing
- [ ] Add milestone on Jan 10 (Case Opened)
- [ ] Add milestone on Feb 10 (Key Evidence Found)
- [ ] Add milestone on Mar 15 (Case Closed)
- [ ] Milestones appear correctly on timeline
- [ ] Milestones persist when filtering

### Date Field Testing
- [ ] Switch between modified_time and created_time
- [ ] Timeline updates correctly
- [ ] File positions change appropriately

### Performance Testing
- [ ] Timeline renders quickly (<1 second)
- [ ] Zoom operations are smooth
- [ ] Filter updates are instant
- [ ] No lag when clicking markers

## Expected Timeline Appearance

```
Jan 10  Jan 15      [24-day gap]      Feb 10  Feb 20  [9-day gap]  Mar 01    Mar 15
  ●●      ●●                             ●●      ●                    ●●         ●
  ↓       ↓                              ↓       ↓                    ↓          ↓
Dense   Dense                          Dense  Single               Dense     Single
```

## File Contents Summary

Each file contains realistic forensic investigation content related to a fictional corporate data breach case. The content helps verify that metadata extraction is working correctly.

## Usage Instructions

1. Create a new case in Evidentia
2. Upload the entire `test_timeline` folder
3. Navigate to Timeline View
4. Verify all test scenarios above
5. Test milestone creation and management
6. Test all filter combinations
7. Test zoom and navigation controls

## Notes

- All files have realistic timestamps for a 3-month investigation
- File sizes vary from 1KB to 50KB
- Content is relevant to a corporate investigation scenario
- Files are named descriptively for easy identification
- Dates are strategically chosen to test edge cases
