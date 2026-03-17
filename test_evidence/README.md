# Test Evidence Folder

This folder contains sample evidence files for testing the Evidentia application.

## Case Scenario
**Case Number:** 2026-INV-001  
**Type:** Internal Data Breach Investigation  
**Suspect:** John Doe (Employee ID: EMP-2045)  
**Date:** March 15-17, 2026

## Folder Structure

```
test_evidence/
├── browser_data/          # Browser history and download records
│   ├── chrome_history.txt
│   └── download_history.txt
├── documents/             # Case documents and reports
│   ├── financial_report_Q1_2026.txt
│   ├── incident_meeting_notes.txt
│   └── termination_notice.txt
├── emails/                # Email evidence
│   ├── email_001.txt
│   └── security_alert.txt
├── images/                # Screenshots and photos
│   ├── screenshot_001.txt
│   └── workstation_photo.txt
├── logs/                  # System and security logs
│   ├── server_access.log
│   └── windows_security.log
├── case_report.txt        # Initial case report
├── case_timeline.txt      # Investigation timeline
├── document1.txt          # Sample document
└── user_activity.csv      # User activity data

Total: 16 files across 5 subdirectories
```

## Evidence Summary

### Key Evidence Items:
1. **Unauthorized Access Logs** - Server logs showing suspicious file access
2. **Email Communications** - Suspicious email to external contact
3. **Browser History** - Searches for log deletion tools
4. **Download Records** - Confidential files downloaded
5. **Timeline** - Complete sequence of events

## Testing Instructions

1. Launch Evidentia application
2. Create a new case (e.g., "Data Breach Investigation")
3. Select case type (e.g., "Internal Breach")
4. Upload this entire `test_evidence` folder
5. The scanner will recursively find all 16 files in subdirectories
6. Files will be analyzed and displayed in real-time
7. All files will be added to the case database

## Expected Results

- All 16 files should be detected and processed
- Files from subdirectories should be included
- Each file should show:
  - File name
  - File type
  - File size
  - Hash value
  - Created/modified dates
  - Full path

## File Scanner Configuration

The file scanner is configured to:
- ✅ Scan recursively through all subdirectories
- ✅ Process ALL file types (not just specific extensions)
- ✅ Extract metadata (size, dates, hash)
- ✅ Handle various file formats (.txt, .log, .csv, etc.)
