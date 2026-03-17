# Evidentia - User Flow Documentation

## Application Overview

Evidentia is a digital forensics timeline tool that helps investigators manage cases, upload evidence, and analyze file metadata automatically.

---

## Screen Flow Diagram

```
┌─────────────────┐
│ Splash Screen   │ (2-3 seconds loading animation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Login Screen    │ ◄─── Logout returns here
└────────┬────────┘
         │
         ├─── New User ────────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐          ┌─────────────────┐
│ Profile Setup   │          │ Sign Up Form    │
│ (First Time)    │          │                 │
└────────┬────────┘          └────────┬────────┘
         │                             │
         │                             │ (After signup, redirects to login)
         │                             │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────┐
         │ Case Management │
         │   (Step 1-2)    │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Evidence Upload │ ◄─── Can return here to upload more
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Metadata Table  │
         └─────────────────┘
```

---

## Detailed User Flows

### 🆕 New User Flow (First Time)

#### 1. Splash Screen
- **Duration:** 2-3 seconds
- **Purpose:** Loading animation with Evidentia branding
- **Elements:**
  - Evidentia logo
  - "Digital Forensics Made Simple" tagline
  - Progress bar
  - Loading status messages

#### 2. Login Screen
- **Action:** User clicks "Sign Up"
- **Form Fields:**
  - Full Name * (required)
  - Email (optional)
  - Username * (min 4 characters)
  - Password * (min 6 characters)
  - Confirm Password *
- **Validation:**
  - All required fields must be filled
  - Username must be unique
  - Passwords must match
  - Minimum length requirements enforced
- **After Success:** Redirects to login form with username pre-filled

#### 3. Login Screen (After Signup)
- **Action:** User enters credentials and logs in
- **Options:**
  - ☐ Remember Me checkbox (saves credentials for auto-login)
- **After Success:** Proceeds to Profile Setup

#### 4. Profile Setup Screen (First Time Only)
- **Purpose:** Personalize user experience
- **Section 1 - Role Selection:**
  - 🔍 Forensic Investigator
  - ⚖️ Legal Professional
  - 🛡️ Cybersecurity Analyst
  - 🎓 Student / Learner
- **Section 2 - Primary Use:**
  - 📁 Manage Cases
  - 🔬 Analyze Evidence
  - 📊 Generate Reports
  - 📚 Learn & Train
- **Section 3 - Organization (Optional):**
  - Text input for university, company, lab, etc.
- **Buttons:**
  - "Skip for Now" - Saves minimal profile and continues
  - "Continue ›" - Saves preferences and continues
- **After Completion:** Proceeds to Case Management

#### 5. Case Management Screen
**Step 1: Create New Case**
- **Form Fields:**
  - Case Name * (required)
  - Description (optional)
- **Button:** "Choose Case Type"

**Step 2: Choose Case Type**
- **Options (select one):**
  - 🔒 Cybercrime
  - 💰 Financial Fraud
  - 📊 Data Theft
  - 🛡️ Internal Breach
- **Buttons:**
  - "‹ Back" - Return to Step 1
  - "Upload Evidence" - Proceed to evidence upload
- **After Selection:** Case is created in database, proceeds to Evidence Upload

#### 6. Evidence Upload Screen
- **Initial State:**
  - Large drag-and-drop zone (800x350px)
  - 📁 Folder icon
  - "Bulk Evidence Upload" title
  - "Drag and drop a folder here or click to browse"
  - "Browse Folder" button

- **During Upload:**
  - Drop zone hidden
  - Progress container shown with:
    - "Analyzing Files..." title
    - Progress bar (X/Y files)
    - Current file being processed
    - Live file list on the right showing:
      - File icon (based on type)
      - File name
      - File type, size, hash preview
      - Green checkmark when processed

- **After Upload Complete:**
  - "✓ Analysis Complete!" message
  - "Successfully analyzed X files" status
  - Two action buttons appear:
    - **"Upload More Evidence"** - Reset to upload another folder
    - **"View Metadata Table"** - Navigate to metadata table

- **Upload More Evidence:**
  - Shows drop zone again
  - Adds separator "─── New Upload Batch ───" to file list
  - All files go to the same case
  - Can repeat multiple times

#### 7. Metadata Table Screen
- **Header:**
  - "‹ Back" button (returns to Evidence Upload)
  - "Evidence Metadata - [Case Name]" title
  - File count display

- **Filters:**
  - Search box (filter by filename)
  - Type dropdown (All Types, Document, Image, Video, Archive, Other)
  - "Clear Filters" button

- **Table Columns:**
  1. ID - Evidence ID
  2. File Name - Full filename
  3. Type - File category
  4. Size - Human-readable format
  5. Created Date - When file was created (or "Unknown")
  6. Modified Date - When file was modified (or "Unknown")
  7. Hash - MD5 hash for integrity

- **Features:**
  - Sortable columns (click header to sort)
  - Row selection
  - Alternating row colors
  - Search and filter in real-time

- **Summary Bar:**
  - Total Size: X MB
  - Type breakdown: Documents: X | Images: Y | Videos: Z | Other: W

---

### 🔄 Returning User Flow (Remember Me Enabled)

#### 1. Splash Screen
- Same as new user (2-3 seconds)

#### 2. Auto-Login
- **If "Remember Me" was checked:**
  - Automatically logs in without showing login screen
  - Skips directly to Case Management
- **If credentials invalid or not saved:**
  - Shows login screen with credentials pre-filled (if saved)

#### 3. Case Management Screen
- Same as new user
- Profile setup is skipped (already completed)
- User can create new cases or continue existing ones

#### 4-7. Evidence Upload & Metadata Table
- Same flow as new user

---

### 🔄 Returning User Flow (Remember Me Disabled)

#### 1. Splash Screen
- Same as new user (2-3 seconds)

#### 2. Login Screen
- **If previously logged in:**
  - Username may be pre-filled (browser cache)
  - User must enter password
- **Options:**
  - ☐ Remember Me checkbox (can enable for next time)
- **After Login:** Proceeds to Case Management (skips Profile Setup)

#### 3-7. Case Management, Evidence Upload & Metadata Table
- Same flow as new user

---

## Key Features by Screen

### Login Screen
- ✅ Sign up for new users
- ✅ Login for existing users
- ✅ Remember Me functionality
- ✅ Auto-login on app restart (if enabled)
- ✅ Password validation
- ✅ Username uniqueness check

### Profile Setup Screen
- ✅ Role selection (4 options)
- ✅ Primary use selection (4 options)
- ✅ Optional organization field
- ✅ Skip option available
- ✅ Only shown once (first login)

### Case Management Screen
- ✅ Two-step case creation
- ✅ Case name and description
- ✅ Case type selection (4 types)
- ✅ Back navigation between steps
- ✅ Saves to database immediately

### Evidence Upload Screen
- ✅ Drag-and-drop folder upload
- ✅ Browse folder dialog
- ✅ Recursive folder scanning (includes subfolders)
- ✅ Real-time file analysis
- ✅ Live file list display
- ✅ Progress tracking
- ✅ Multiple upload batches supported
- ✅ Upload more evidence option
- ✅ View metadata table option

### Metadata Table Screen
- ✅ Comprehensive file listing
- ✅ 7 columns of metadata
- ✅ Search by filename
- ✅ Filter by file type
- ✅ Sortable columns
- ✅ Summary statistics
- ✅ Automatic merging of multiple uploads
- ✅ "Unknown" for missing dates

---

## Navigation Summary

### Forward Navigation
```
Splash → Login → Profile Setup → Case Management → Evidence Upload → Metadata Table
         (auto)   (first time)   (2 steps)         (repeatable)
```

### Backward Navigation
```
Metadata Table → Evidence Upload → Case Management
    (‹ Back)         (‹ Back)
```

### Logout
```
Any Screen → Login Screen
  (Logout button in header)
```

---

## Database Integration

### User Data
- Username, password (hashed), full name, email
- Profile preferences (role, organization, primary use)
- Remember Me credentials (encrypted)

### Case Data
- Case name, description, type, status
- Created/modified timestamps
- Associated user ID

### Evidence Data
- File name, path, extension, size
- Created/modified timestamps
- MD5 hash for integrity
- Associated case ID
- Metadata extracted from files

---

## File Types Supported

### Documents
`.txt`, `.doc`, `.docx`, `.pdf`, `.rtf`, `.odt`

### Images
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.ico`, `.svg`, `.webp`

### Videos
`.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.flv`, `.webm`, `.m4v`

### Archives
`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`

### Executables
`.exe`, `.dll`, `.bat`, `.sh`, `.msi`

### Web Files
`.html`, `.htm`, `.css`, `.js`, `.json`, `.xml`

### Databases
`.db`, `.sqlite`, `.mdb`, `.accdb`

### Logs
`.log`, `.txt`

### Configuration
`.ini`, `.cfg`, `.conf`, `.yaml`, `.yml`

### Spreadsheets
`.xlsx`, `.xls`, `.csv`, `.ods`

### Presentations
`.pptx`, `.ppt`, `.odp`

---

## Testing Instructions

### Test as New User
1. Launch application
2. Wait for splash screen
3. Click "Sign Up"
4. Fill in all required fields
5. Click "Create Account"
6. Login with new credentials
7. Check "Remember Me"
8. Complete profile setup
9. Create a new case
10. Select case type
11. Upload test_evidence folder
12. Wait for analysis
13. Click "View Metadata Table"
14. Verify all 16 files are shown

### Test as Returning User (Remember Me)
1. Close and relaunch application
2. Should auto-login (skip login screen)
3. Should skip profile setup
4. Should go directly to Case Management

### Test Multiple Uploads
1. Upload first batch of evidence
2. Click "Upload More Evidence"
3. Upload second batch
4. Click "View Metadata Table"
5. Verify both batches are merged in table

---

## Error Handling

### Login Errors
- Invalid username/password → Error message shown
- Empty fields → "Please enter both username and password"
- Network issues → Connection error message

### Signup Errors
- Username taken → "Username already exists"
- Passwords don't match → "Passwords do not match"
- Short password → "Password must be at least 6 characters"
- Short username → "Username must be at least 4 characters"

### Upload Errors
- No files found → "No files found in folder"
- Permission denied → "Cannot access file: [filename]"
- Invalid folder → "Directory not found"

### Database Errors
- Connection failed → Error message with retry option
- Query failed → Logged and user notified

---

## Future Enhancements

### Planned Features
- Timeline visualization of evidence
- Advanced filtering and search
- Export metadata to CSV/PDF
- Evidence tagging and categorization
- Case collaboration features
- Audit trail and activity logs
- Advanced metadata extraction (EXIF, document properties)
- File preview functionality
- Evidence comparison tools

---

## Technical Notes

### Screen Transitions
- All transitions use QStackedWidget
- Smooth switching between screens
- Previous screens remain in memory for fast navigation

### Data Persistence
- SQLite database (evidentia.db)
- Automatic schema creation on first run
- Transaction-based operations for data integrity

### Performance
- Background threading for file scanning
- Real-time UI updates during analysis
- Efficient database queries with indexing
- Lazy loading for large datasets

---

## Support & Documentation

For more information:
- See `ProjectProposal.md` for project requirements
- See `test_evidence/README.md` for test data information
- See `DEVELOPMENT_PLAN.md` for technical architecture

---

**Version:** 1.0  
**Last Updated:** March 18, 2026  
**Application:** Evidentia - Digital Forensics Timeline Tool
