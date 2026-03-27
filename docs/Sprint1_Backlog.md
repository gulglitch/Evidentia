# Sprint 1 Backlog - Evidentia

## Module Name: Evidence Engine

**Sprint Duration:** Weeks 1-2  
**Sprint Goal:** Build the core evidence management functionality with bulk folder upload, automatic metadata extraction, and case organization by type.

---

## User Stories for Sprint 1

### STORY ID: US-01 | Story Title: Bulk Folder Upload
**Priority:** High  
**Estimated Hours:** 12 hours

**User Story:**  
As a user, I want to drag and drop a whole folder of files into the Evidence Management area so that I don't have to pick files one by one.

**Description:**  
This story involves developing the "Evidence Engine" backend to handle directory selection, recursive file scanning, drag-and-drop functionality, and real-time progress tracking.

**Sub User Stories:**

1. **As a user, I want to drag a folder from my computer into the app interface** so that uploading is quick and intuitive.
   - Acceptance Criteria:
     - Drop zone responds to drag-and-drop events
     - Visual feedback on drag hover (border highlight changes color)
     - Accepts folder drops only
     - Rejects individual file drops with error message
     - Folder path captured and validated on drop

2. **As a user, I want to browse and select a folder using a dialog** so that I have an alternative to drag-and-drop.
   - Acceptance Criteria:
     - "Browse Folder" button below drop zone
     - Native folder selection dialog opens on click
     - Selected folder path validated (must exist)
     - Same processing pipeline as drag-and-drop
     - Cross-platform compatibility (Windows, Mac, Linux)

3. **As a user, I want the system to recursively read all files within the dropped folder** so that files in subfolders are included.
   - Acceptance Criteria:
     - FileScanner class scans all subdirectories
     - All files collected regardless of nesting depth
     - File paths stored relative to root upload folder
     - Efficient scanning algorithm (no duplicates)
     - Handles folders with 100+ files without freezing
     - Maintains folder structure information

4. **As a user, I want to see real-time progress during file analysis and a completion message** so that I know the app is working and when the upload is finished.
   - Acceptance Criteria:
     - Drop zone hidden during processing
     - Progress container displayed with title "Analyzing Files..."
     - Progress bar showing "X/Y files" processed
     - Percentage displayed on progress bar
     - Current file name being processed displayed below bar
     - Live file list on right side showing processed files
     - Each file entry shows: icon (based on type), name, type, size, hash preview
     - Green checkmark (✓) appears when file processed
     - Background threading prevents UI freeze
     - Smooth progress updates (no lag)
     - "✓ Analysis Complete!" message displayed in green when finished
     - "Successfully analyzed X files" status shown
     - Two action buttons appear:
       - "Upload More Evidence" - resets drop zone for another batch
       - "View Metadata Table" - navigates to table view
     - Upload statistics displayed (total files, total size)

5. **As a user, I want to upload multiple batches of evidence to the same case** so that I can add evidence incrementally.
   - Acceptance Criteria:
     - "Upload More Evidence" button resets drop zone
     - Visual separator "─── New Upload Batch ───" added to file list
     - All batches linked to same case_id in database
     - Previous uploads remain visible in scrollable list
     - Can repeat unlimited times
     - Each batch processed independently
     - All files from all batches saved to database

---

### STORY ID: US-02 | Story Title: Metadata Overview Table
**Priority:** High  
**Estimated Hours:** 14 hours

**User Story:**  
As a user, I want to see a list of file names and dates automatically so that I don't have to type them manually or check each file's properties individually.

**Description:**  
This story involves implementing automatic metadata extraction from various file types and displaying the results in a comprehensive, searchable, and sortable table with filtering capabilities and summary statistics.

**Sub User Stories:**

1. **As a user, I want the app to automatically extract file metadata from various file types** so that I can see file properties and document-specific details without opening them.
   - Acceptance Criteria:
     - MetadataExtractor class extracts: file name, size, type, extension
     - Extract file timestamps: created date, modified date, accessed date
     - Calculate MD5 hash for file integrity verification
     - Extract from .docx files: author, title, subject, created date, modified date, last modified by
     - Extract from .pdf files: author, title, subject, page count, created date, producer
     - Extract from .txt files: encoding, line count, character count
     - Metadata stored in JSON format in database metadata column
     - Handle missing/unavailable metadata gracefully (display "Unknown" or "N/A")
     - Handles corrupted or password-protected files gracefully (log error, continue)
     - Extraction happens automatically during upload process
     - No manual intervention required

2. **As a user, I want to view all evidence in a comprehensive table** so that I can review all files at once.
   - Acceptance Criteria:
     - Table with 7 columns: ID, File Name, Type, Size, Created Date, Modified Date, Hash
     - All evidence for current case displayed
     - Alternating row colors for readability (light/dark rows)
     - "Unknown" displayed for missing dates
     - Human-readable file sizes (B, KB, MB, GB)
     - Table auto-resizes columns to fit content
     - Scrollable for large datasets (100+ files)
     - Professional styling matching app theme

3. **As a user, I want to search the metadata table by filename** so that I can find specific files quickly.
   - Acceptance Criteria:
     - Search box at top of table with placeholder "Search by filename..."
     - Real-time filtering as user types (no submit button needed)
     - Case-insensitive search
     - Searches file name column only
     - Shows matching rows, hides non-matching rows
     - Clear search button (X icon) appears when text entered
     - Search works with type filter simultaneously
     - "No results found" message if no matches

4. **As a user, I want to filter the metadata table by file type** so that I can focus on specific categories.
   - Acceptance Criteria:
     - Type dropdown at top of table
     - Options: All Types, Document, Image, Video, Archive, Executable, Web, Database, Log, Config, Spreadsheet, Presentation, Other
     - Dropdown filters table in real-time (no apply button)
     - Shows only files matching selected type category
     - "Clear Filters" button resets to "All Types" and clears search
     - Filter works with search simultaneously
     - Filter selection persists during session

5. **As a user, I want to see summary statistics** so that I can understand the evidence collection at a glance.
   - Acceptance Criteria:
     - Summary bar at bottom of table
     - Total file count: "Showing X files" (updates with filters)
     - Total size: "Total Size: X MB" (sum of all displayed files)
     - Type breakdown: "Documents: X | Images: Y | Videos: Z | Other: W"
     - Statistics update dynamically when filters applied
     - Human-readable formatting (commas for thousands)
     - Color-coded statistics (optional)

---

### STORY ID: US-03 | Story Title: Case Type Sorting
**Priority:** High  
**Estimated Hours:** 10 hours

**User Story:**  
As a user, I want to label my case (e.g., "Financial Fraud") to keep my workspace organized and categorize different types of investigations.

**Description:**  
This story involves implementing a complete case management system with case creation, type selection, custom case types, and a dashboard to view all cases organized by type.

**Sub User Stories:**

1. **As a user, I want to create a new case with a name, description, and select a case type** so that I can start and categorize my investigation.
   - Acceptance Criteria:
     - Case creation wizard with Step 1: Basic Information
     - Case Name field (required, text input, max 200 characters)
     - Description field (optional, multi-line text area, max 1000 characters)
     - Form validation: name cannot be empty
     - Error message displayed if validation fails
     - "Choose Case Type" button to proceed to Step 2
     - Step 2: Case Type Selection screen
     - Four predefined types displayed as visual cards:
       - 🔒 Cybercrime
       - 💰 Financial Fraud
       - 📊 Data Theft
       - 🛡️ Internal Breach
     - Each card shows icon and type name
     - Single selection (radio button behavior)
     - Selected card highlighted with accent color
     - "‹ Back" button returns to Step 1 (preserves entered data)
     - "Upload Evidence" button proceeds (only enabled when type selected)
     - Professional form styling with clear labels

2. **As a user, I want to add custom case types** so that I can handle specialized investigations not covered by defaults.
   - Acceptance Criteria:
     - "➕ Add Custom Type" option in case type selection grid
     - Dialog opens with text input for custom type name
     - Validation: name cannot be empty
     - Validation: name cannot duplicate existing types
     - Custom type saved to database (custom_case_types table)
     - Custom types appear in future case creation sessions
     - Custom types persist across app restarts
     - Default icon assigned automatically for custom types
     - Success message after custom type created

3. **As a user, I want my case to be saved to the database** so that I can access it later.
   - Acceptance Criteria:
     - Case saved with fields: name, description, case_type, created_date, status
     - Unique case_id generated (auto-increment primary key)
     - Status defaults to "Active"
     - Created_date automatically set to current timestamp
     - Database transaction ensures data integrity
     - Foreign key constraints enforced
     - Success confirmation after save

4. **As a user, I want to view all my cases in a dashboard with case type indicators** so that I can access existing investigations and quickly identify investigation categories.
   - Acceptance Criteria:
     - Cases dashboard displays all cases from database
     - Each case card shows: case name, case type, creation date, status
     - Case type displayed with icon/emoji on case card
     - Type name shown as text label
     - Consistent icon mapping (Cybercrime = 🔒, Financial Fraud = 💰, etc.)
     - Custom types displayed with generic icon (📋)
     - Cases sorted by most recent first (descending created_date)
     - "New Case" button prominently displayed to create additional cases
     - Click on case card to open it (navigates to evidence view)
     - Empty state message if no cases exist: "No cases yet. Create your first case!"
     - Dashboard refreshes when returning from case creation
     - Scrollable if many cases exist

5. **As a user, I want the app to automatically navigate to evidence upload after case creation and show which case I'm working on** so that I can immediately start adding files without confusion.
   - Acceptance Criteria:
     - After clicking "Upload Evidence" in Step 2, case is saved to database
     - App automatically navigates to Evidence Upload screen
     - Current case_id set in application state
     - Status bar shows: "Uploading evidence for: [Case Name]"
     - Case name displayed in evidence upload screen header
     - Case name displayed in metadata table header
     - Current case_id persists during entire session
     - Visual confirmation of active case in all relevant screens
     - User can proceed with folder upload immediately
     - No manual navigation required

---

## Sprint 1 Technical Tasks

### Database Development
- [x] Design database schema (cases, evidence, custom_case_types tables)
- [x] Implement Database class with connection management
- [x] Create CRUD operations for cases (create, read, update, delete)
- [x] Create CRUD operations for evidence (create, read, update, delete)
- [x] Create CRUD operations for custom case types
- [x] Add indexes for performance (case_id, file_type)
- [x] Implement transaction handling for data integrity
- [x] Create schema.sql file with CREATE TABLE statements
- [x] Create seed.sql file with sample data
- [x] Add foreign key constraints (evidence.case_id → cases.id)

### Backend Development
- [x] Implement FileScanner class for recursive directory scanning
- [x] Add file type detection based on extension
- [x] Add file categorization (Document, Image, Video, etc.)
- [x] Add file filtering by supported extensions
- [x] Implement MetadataExtractor class
- [x] Extract basic file metadata (name, size, dates, hash)
- [x] Extract document metadata (.docx, .pdf, .txt)
- [x] Extract image EXIF data (.jpg, .png)
- [x] Implement MD5 hash calculation for file integrity
- [x] Add error handling for corrupted/inaccessible files
- [x] Optimize for large file sets (100+ files)
- [x] Implement background threading for file processing

### Frontend Development
- [x] Create EvidenceUpload screen with drag-and-drop zone
- [x] Implement drag-and-drop event handlers
- [x] Add folder browse dialog
- [x] Implement real-time progress tracking UI
- [x] Add live file list display during upload
- [x] Add "Upload More Evidence" functionality
- [x] Add "View Metadata Table" navigation button
- [x] Create MetadataTable screen with 7 columns
- [x] Implement table sorting (click column headers)
- [x] Add search functionality (filter by filename)
- [x] Add type filter dropdown with all categories
- [x] Add "Clear Filters" button
- [x] Add summary statistics bar at bottom
- [x] Create CaseManagement screen with 2-step wizard
- [x] Implement Step 1: Case name and description form
- [x] Implement Step 2: Case type selection with 4 predefined types
- [x] Add custom case type creation dialog
- [x] Create CasesDashboard to display all cases
- [x] Implement case card display with type indicators
- [x] Add "New Case" button
- [x] Implement MainWindow navigation controller
- [x] Connect all screens with signal/slot connections
- [x] Add "‹ Back" navigation buttons
- [x] Add status bar with case information display
- [x] Implement proper screen transitions

### UI/UX Polish
- [x] Desktop-optimized window size (1600x1000, minimum 800x600)
- [x] Professional color scheme:
  - Background: #0a1929 (dark blue)
  - Cards: #122a3a (darker blue)
  - Accent: #00d4aa (cyan/turquoise)
  - Text: #e0e6ed (light gray)
- [x] Consistent styling across all screens
- [x] Proper spacing and padding (20-30px margins)
- [x] Readable fonts and sizes (14-16px body, 18-24px headers)
- [x] Visual feedback for user actions (hover states, click effects)
- [x] Error messages for validation failures
- [x] Loading indicators for long operations
- [x] Icons for file types and case types

### Testing
- [x] Test case creation with all predefined types
- [x] Test custom case type creation and persistence
- [x] Test cases dashboard display
- [x] Test folder drag-and-drop with test_evidence folder
- [x] Test folder browse dialog
- [x] Test recursive folder scanning (16 files in test_evidence)
- [x] Test metadata extraction for documents (.txt, .docx)
- [x] Test metadata extraction for images (.jpg, .png)
- [x] Test metadata extraction for logs (.log)
- [x] Test metadata extraction for CSV files
- [x] Test table display with all 16 test files
- [x] Test table sorting by each column (ascending/descending)
- [x] Test search functionality (partial matches, case-insensitive)
- [x] Test type filtering (each category)
- [x] Test "Clear Filters" button
- [x] Test summary statistics accuracy
- [x] Test multiple upload batches (2-3 batches)
- [x] Test navigation between screens (upload → table → upload)
- [x] Test back button functionality
- [x] Test with large folder (100+ files) - performance check

---

## Definition of Done

A user story is considered "Done" when:
- [x] All sub-user stories completed
- [x] All acceptance criteria met and verified
- [x] Code written and committed to repository
- [x] Manual testing completed successfully
- [x] No critical bugs present
- [x] Code follows project structure (backend/, frontend/, database/)
- [x] All imports updated to new structure
- [x] Screenshots captured for iteration document
- [x] User flow documented in docs/USER_FLOW.md
- [x] Code reviewed by team member

---

## Sprint 1 Deliverables

### Completed Features
1. ✅ **Bulk Folder Upload (US-01)**
   - Drag-and-drop interface
   - Folder browse dialog
   - Recursive folder scanning
   - Real-time progress tracking
   - Multiple batch uploads
   - File type filtering

2. ✅ **Metadata Overview Table (US-02)**
   - Automatic metadata extraction (basic, documents, images)
   - 7-column comprehensive table
   - Table sorting (all columns)
   - Search functionality (by filename)
   - Type filtering (dropdown with 12 categories)
   - Summary statistics
   - Navigation controls

3. ✅ **Case Type Sorting (US-03)**
   - 2-step case creation wizard
   - 4 predefined case types
   - Custom case type creation
   - Cases dashboard
   - Case type indicators
   - Database persistence

### Code Statistics
- **Backend Files:** 5 modules (database.py, file_scanner.py, metadata_extractor.py, pdf_generator.py, helpers.py)
- **Frontend Files:** 9 screens (case_management.py, cases_dashboard.py, evidence_upload.py, metadata_table.py, new_case_dialog.py, login_screen.py, profile_setup.py, splash_screen.py, main_window.py)
- **Database Files:** 3 (evidentia.db, schema.sql, seed.sql)
- **Documentation Files:** 11 markdown files
- **Total Lines of Code:** ~3500+ lines

---

## Sprint 1 Metrics

**Planned User Stories:** 3  
**Completed User Stories:** 3  
**Planned Sub-Stories:** 27  
**Completed Sub-Stories:** 27  
**Completion Rate:** 100%

**Planned Hours:** 36 hours  
**Actual Hours:** ~40 hours (includes project restructuring and polish)

---

## Team Work Division

### Gul-e-Zara (Group Lead, Developer & Tester)
**Backend Development:**
- Implemented Database class with all CRUD operations
- Created FileScanner for recursive directory scanning
- Built MetadataExtractor for multiple file types (documents, images, logs)
- Designed and implemented database schema (3 tables, indexes, foreign keys)
- Implemented MD5 hash calculation
- Created seed data for testing
- Fixed import paths after project restructuring
- Optimized file scanning performance

**Testing:**
- Backend unit testing
- Integration testing (backend + frontend)
- Performance testing with large folders
- Bug fixes and error handling

**Repository Management:**
- Git commits and version control
- Project restructuring to match submission requirements
- README.md updates

### Rumesha Naveed (Requirement Engineer, Developer & Tester)
**Frontend Development:**
- Implemented all 9 frontend screens
- Created drag-and-drop interface for evidence upload
- Built 2-step case creation wizard
- Designed metadata table with search/filter/sort
- Implemented cases dashboard
- Created custom case type dialog
- Connected all screens with proper navigation
- Implemented MainWindow controller
- Added status bar and case information display

**Documentation:**
- User stories and acceptance criteria
- User flow documentation (docs/USER_FLOW.md)
- Sprint backlog creation
- Project proposal
- Screenshots for iteration document

**Testing:**
- Frontend UI testing
- User flow testing (end-to-end)
- Form validation testing
- Cross-screen navigation testing

### Shared Responsibilities
- Sprint planning and backlog refinement
- Daily standups and progress tracking
- Code reviews and pair programming
- Bug identification and fixes
- Trello board management (3 snapshots)
- Sprint retrospective
- Iteration document preparation

---

## Notes

- All three main user stories from project proposal completed
- 27 detailed sub-user stories implemented with full acceptance criteria
- Authentication and profile setup implemented as supporting infrastructure (not counted in main sprint scope)
- Project structure reorganized to match submission requirements (backend/, frontend/, database/, docs/)
- Unused files removed to keep codebase clean
- All imports updated to new structure
- Test files removed (test.py, test_app.py, test_custom_case_types.py)
- .env file removed (not needed for SQLite-based project)
- Ready for Sprint 2: Timeline & Analytics module

---

## Trello Board Snapshots

**Snapshot 1 (Sprint Start):**
- All user stories in "To Do" column
- Sprint backlog uploaded
- Tasks estimated and assigned

**Snapshot 2 (Mid-Sprint):**
- US-01 and US-03 in "Done"
- US-02 in "In Progress"
- ~60% completion

**Snapshot 3 (Sprint End):**
- All user stories in "Done"
- No leftovers for Sprint 2
- 100% completion rate

---

## Product Burndown Chart Data

| Day | Planned Tasks Remaining | Actual Tasks Remaining |
|-----|------------------------|------------------------|
| 1   | 27                     | 27                     |
| 2   | 25                     | 25                     |
| 3   | 23                     | 22                     |
| 4   | 20                     | 19                     |
| 5   | 18                     | 16                     |
| 6   | 15                     | 13                     |
| 7   | 13                     | 10                     |
| 8   | 10                     | 7                      |
| 9   | 8                      | 5                      |
| 10  | 5                      | 3                      |
| 11  | 3                      | 1                      |
| 12  | 1                      | 0                      |
| 13  | 0                      | 0                      |
| 14  | 0                      | 0                      |

*Note: Create actual burndown chart in Excel/Google Sheets and include in Iteration_1.docx*
