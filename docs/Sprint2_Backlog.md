# Sprint 2 Backlog - Evidentia

## Module Name: Timeline & Analytics

**Sprint Duration:** Weeks 3-4  
**Sprint Goal:** Build interactive timeline visualization, evidence status tracking, risk level analytics, and global search functionality to enable comprehensive case analysis and evidence prioritization.

---

## User Stories for Sprint 2

### STORY ID: US-04 | Story Title: Timeline Grid
**Priority:** High  
**Estimated Hours:** 14 hours

**User Story:**  
As a user, I want to see my case milestones on a bar so I can see the order of events.

**Description:**  
This story involves developing an interactive timeline visualization that displays case milestones and evidence chronologically, allowing investigators to understand the sequence of events at a glance.

**Sub User Stories:**

1. **As a user, I want to see a horizontal timeline bar showing case progression stages** so that I can visualize the investigation workflow.
   - Acceptance Criteria:
     - Timeline bar displays 5 key stages: "Case Created" → "Evidence Collected" → "Analysis In Progress" → "Review" → "Closed"
     - Each stage represented as a node on the timeline
     - Current stage highlighted with accent color (#00d4aa)
     - Completed stages shown in green with checkmark icon
     - Future stages shown in gray
     - Timeline spans full width of screen
     - Professional styling matching app theme
     - Responsive layout for different window sizes

2. **As a user, I want to see all evidence files plotted on a chronological timeline** so that I can understand when each piece of evidence was created or modified.
   - Acceptance Criteria:
     - Timeline displays all evidence files from current case
     - Files plotted based on created_date or modified_date (user selectable)
     - Timeline shows date range from earliest to latest file
     - Each file represented as a point/marker on timeline
     - File markers color-coded by type (Document=blue, Image=green, Log=orange, etc.)
     - Hover over marker shows tooltip with: filename, date, type, size
     - Timeline scrollable horizontally for large date ranges
     - Zoom controls to adjust timeline granularity (day/week/month view)
     - Timeline auto-scales based on date range of evidence

3. **As a user, I want to click on timeline markers to view file details** so that I can quickly access information about specific evidence.
   - Acceptance Criteria:
     - Click on timeline marker opens detail panel
     - Detail panel shows: filename, full path, type, size, all dates, hash, metadata
     - "Open File Location" button to navigate to file in system
     - "View in Table" button to jump to file in metadata table
     - Close button (X) to dismiss detail panel
     - Panel slides in from right side of screen
     - Multiple clicks update panel content (no multiple panels)
     - Professional styling with proper spacing

4. **As a user, I want to filter the timeline by date range** so that I can focus on specific time periods.
   - Acceptance Criteria:
     - Date range selector at top of timeline
     - "From" date picker (calendar widget)
     - "To" date picker (calendar widget)
     - "Apply Filter" button to update timeline
     - "Reset" button to show all dates
     - Timeline updates to show only files within selected range
     - File count indicator: "Showing X files from [date] to [date]"
     - Date pickers default to min/max dates in evidence
     - Validation: "From" date cannot be after "To" date

5. **As a user, I want to see case milestones marked on the timeline** so that I can correlate evidence with investigation events.
   - Acceptance Criteria:
     - Milestones displayed as vertical lines on timeline
     - Default milestones: Case Created, First Evidence Upload, Analysis Started
     - Milestone label shown above timeline
     - Milestone date shown below timeline
     - Different visual style from evidence markers (dashed line)
     - Hover shows milestone details
     - Milestones persist when filtering timeline
     - Professional color scheme (milestones in accent color)

---

### STORY ID: US-05 | Story Title: Evidence Status Tracking
**Priority:** High  
**Estimated Hours:** 12 hours

**User Story:**  
As a user, I want to check boxes (Analyzed/Pending) to keep track of my progress.

**Description:**  
This story involves implementing a comprehensive status tracking system that allows investigators to mark evidence as analyzed, pending, or flagged, and filter the evidence view based on these statuses.

**Sub User Stories:**

1. **As a user, I want to assign status labels to evidence files** so that I can track which files have been reviewed.
   - Acceptance Criteria:
     - Status column added to metadata table
     - Three status options: "Pending" (default), "Analyzed", "Flagged"
     - Status displayed as colored badge in table
     - Pending = yellow badge, Analyzed = green badge, Flagged = red badge
     - Click on status badge opens dropdown to change status
     - Status change saves immediately to database
     - Visual confirmation (brief highlight) when status updated
     - Status persists across app sessions

2. **As a user, I want to filter evidence by status using checkboxes** so that I can focus on specific categories of files.
   - Acceptance Criteria:
     - Status filter panel in sidebar or above table
     - Three checkboxes: "Show Pending", "Show Analyzed", "Show Flagged"
     - All checkboxes checked by default (show all)
     - Uncheck box to hide that status category
     - Table updates in real-time as checkboxes toggled
     - Filter works simultaneously with search and type filters
     - "Clear All Filters" button resets all checkboxes
     - Filter state persists during session
     - File count updates: "Showing X of Y files"

3. **As a user, I want to bulk update status for multiple files** so that I can efficiently process large batches of evidence.
   - Acceptance Criteria:
     - Checkbox column added to left of metadata table
     - "Select All" checkbox in table header
     - Individual checkboxes for each file row
     - "Bulk Actions" dropdown appears when files selected
     - Bulk actions: "Mark as Analyzed", "Mark as Pending", "Mark as Flagged"
     - Confirmation dialog before bulk update: "Update status for X files?"
     - Status updated for all selected files simultaneously
     - Success message: "Updated X files"
     - Selection cleared after bulk action
     - Undo option (optional enhancement)

4. **As a user, I want to see status statistics** so that I can understand my investigation progress at a glance.
   - Acceptance Criteria:
     - Status summary widget displayed prominently
     - Shows counts: "Pending: X | Analyzed: Y | Flagged: Z"
     - Percentage bar showing completion: "X% Analyzed"
     - Color-coded segments in progress bar (yellow/green/red)
     - Statistics update in real-time when status changed
     - Statistics respect active filters (show filtered counts)
     - Click on status count to filter table by that status
     - Professional styling matching app theme

5. **As a user, I want to add notes to flagged evidence** so that I can document why certain files need attention.
   - Acceptance Criteria:
     - "Notes" icon appears next to flagged files
     - Click notes icon opens text input dialog
     - Multi-line text area for notes (max 500 characters)
     - "Save" and "Cancel" buttons
     - Notes saved to database (new column: evidence.notes)
     - Notes icon changes color when notes exist (blue = has notes)
     - Hover over notes icon shows preview of notes (first 50 chars)
     - Click icon again to edit existing notes
     - Notes searchable in global search (optional)

---

### STORY ID: US-06 | Story Title: Risk Level Charts
**Priority:** High  
**Estimated Hours:** 12 hours

**User Story:**  
As a user, I want to see a bar chart of High/Low risk files to know what to check first.

**Description:**  
This story involves implementing risk assessment functionality that automatically categorizes evidence by risk level and displays visual analytics to help investigators prioritize their work.

**Sub User Stories:**

1. **As a user, I want the system to automatically assign risk levels to evidence files** so that I can identify high-priority items.
   - Acceptance Criteria:
     - Risk level calculated based on file characteristics
     - Three risk levels: "Low", "Medium", "High"
     - Risk factors considered:
       - File type (Executable/Script = High, Document = Medium, Image = Low)
       - File size (>100MB = Medium risk, >500MB = High risk)
       - File extension (.exe, .bat, .sh = High, .dll = Medium)
       - Modified date (recently modified = higher risk)
     - Risk level stored in database (evidence.risk_level column)
     - Risk calculated automatically during file upload
     - Risk level displayed in metadata table as colored badge
     - Low = green, Medium = yellow, High = red
     - Risk level recalculated if file metadata changes

2. **As a user, I want to see a bar chart showing risk level distribution** so that I can understand the overall risk profile of my case.
   - Acceptance Criteria:
     - Bar chart displayed in analytics dashboard
     - Three bars: Low Risk, Medium Risk, High Risk
     - Y-axis shows file count (0 to max)
     - X-axis shows risk categories
     - Bars color-coded: green, yellow, red
     - Hover over bar shows exact count
     - Chart title: "Evidence Risk Distribution"
     - Chart updates when evidence added/removed
     - Professional styling using charting library (matplotlib or plotly)
     - Chart responsive to window resizing

3. **As a user, I want to filter evidence by risk level** so that I can focus on high-priority files first.
   - Acceptance Criteria:
     - Risk filter checkboxes in sidebar
     - Three checkboxes: "Show Low Risk", "Show Medium Risk", "Show High Risk"
     - All checked by default
     - Uncheck to hide that risk category
     - Table updates in real-time
     - Filter works with status and type filters simultaneously
     - Click on bar chart bar to filter by that risk level
     - "Clear Filters" button resets risk filters
     - Filtered count displayed: "Showing X high-risk files"

4. **As a user, I want to see a pie chart showing file type distribution** so that I can understand the composition of my evidence.
   - Acceptance Criteria:
     - Pie chart displayed in analytics dashboard
     - Each slice represents a file type category
     - Slice size proportional to file count
     - Color-coded slices (consistent with app theme)
     - Legend showing type names and counts
     - Hover over slice shows percentage
     - Chart title: "Evidence Type Distribution"
     - Chart updates when evidence added/removed
     - Professional styling using charting library
     - Chart responsive to window resizing

5. **As a user, I want to manually override risk levels** so that I can adjust risk based on case-specific knowledge.
   - Acceptance Criteria:
     - Click on risk badge in table opens dropdown
     - Dropdown shows three options: Low, Medium, High
     - Select new risk level to update
     - Confirmation dialog: "Change risk level to [X]?"
     - Risk level updated in database
     - Charts update automatically
     - Visual confirmation (brief highlight)
     - Override persists across sessions
     - "Reset to Auto" option to revert to calculated risk

---

### STORY ID: US-07 | Story Title: Global Search
**Priority:** High  
**Estimated Hours:** 10 hours

**User Story:**  
As a user, I want to search by filename to find evidence quickly.

**Description:**  
This story involves implementing a comprehensive global search system that allows investigators to quickly find evidence across multiple fields with advanced filtering and search history.

**Sub User Stories:**

1. **As a user, I want to search evidence by filename** so that I can quickly locate specific files.
   - Acceptance Criteria:
     - Global search bar prominently displayed at top of screen
     - Placeholder text: "Search evidence by filename, type, or hash..."
     - Real-time search as user types (debounced, 300ms delay)
     - Case-insensitive search
     - Partial match support (search "report" finds "financial_report.pdf")
     - Search highlights matching text in results
     - Clear search button (X icon) when text entered
     - Search works across all evidence in current case
     - Results update instantly
     - "No results found" message if no matches

2. **As a user, I want to search across multiple fields** so that I can find evidence using different criteria.
   - Acceptance Criteria:
     - Search looks in: filename, file type, file extension, hash (first 8 chars)
     - Search also looks in metadata (document author, title, subject)
     - Search looks in notes (if notes exist)
     - All matching files displayed in results
     - Search field dropdown to select specific field (optional)
     - Default: search all fields
     - Results show which field matched (highlight or badge)
     - Fast search performance (<500ms for 1000+ files)

3. **As a user, I want to use advanced search operators** so that I can perform precise searches.
   - Acceptance Criteria:
     - Support for exact match: "financial report" (with quotes)
     - Support for OR operator: report OR document
     - Support for NOT operator: report NOT draft
     - Support for wildcard: report*.pdf
     - Support for date range: created:2026-01-01..2026-03-01
     - Support for size range: size:>10MB
     - Support for type filter: type:pdf
     - Help icon (?) shows operator guide
     - Invalid syntax shows error message
     - Examples provided in help tooltip

4. **As a user, I want to see search history** so that I can quickly repeat previous searches.
   - Acceptance Criteria:
     - Click on search bar shows dropdown with recent searches
     - Last 10 searches displayed
     - Most recent at top
     - Click on history item to repeat search
     - "Clear History" button at bottom of dropdown
     - Search history persists across sessions (saved to database)
     - History includes timestamp: "report.pdf - 2 hours ago"
     - Delete individual history items (X icon)
     - History dropdown dismisses when clicking outside

5. **As a user, I want to save search filters as presets** so that I can quickly apply common search criteria.
   - Acceptance Criteria:
     - "Save Current Filters" button when filters active
     - Dialog prompts for preset name
     - Preset saves: search query, type filter, status filter, risk filter, date range
     - Presets displayed in dropdown: "My Saved Searches"
     - Click preset to apply all saved filters
     - Edit preset name (rename option)
     - Delete preset option
     - Presets persist across sessions (saved to database)
     - Maximum 20 saved presets
     - Export/import presets (optional enhancement)

---

## Sprint 2 Technical Tasks

### Database Development
- [ ] Add status column to evidence table (TEXT: Pending/Analyzed/Flagged)
- [ ] Add risk_level column to evidence table (TEXT: Low/Medium/High)
- [ ] Add notes column to evidence table (TEXT, nullable)
- [ ] Create milestones table (id, case_id, milestone_name, milestone_date, description)
- [ ] Create search_history table (id, case_id, search_query, timestamp)
- [ ] Create search_presets table (id, case_id, preset_name, filters_json, created_date)
- [ ] Add indexes for performance (status, risk_level, search fields)
- [ ] Create migration script to update existing database
- [ ] Update CRUD operations for new columns
- [ ] Add bulk update operations for status changes

### Backend Development
- [ ] Implement RiskAssessment class for automatic risk calculation
- [ ] Add risk calculation algorithm based on file characteristics
- [ ] Implement TimelineGenerator class to prepare timeline data
- [ ] Add date range filtering logic
- [ ] Implement SearchEngine class for multi-field search
- [ ] Add search operator parsing (quotes, OR, NOT, wildcards)
- [ ] Implement search history management
- [ ] Implement search preset save/load functionality
- [ ] Add bulk status update operations
- [ ] Optimize search performance for large datasets

### Frontend Development
- [ ] Create TimelineView screen with horizontal timeline
- [ ] Implement timeline plotting with file markers
- [ ] Add zoom and scroll controls for timeline
- [ ] Implement date range picker for timeline filtering
- [ ] Add milestone markers to timeline
- [ ] Create file detail panel (slides in from right)
- [ ] Add status column to metadata table
- [ ] Implement status dropdown for individual files
- [ ] Add status filter checkboxes to sidebar
- [ ] Implement bulk selection checkboxes
- [ ] Create bulk actions dropdown
- [ ] Add status statistics widget
- [ ] Implement notes dialog for flagged evidence
- [ ] Create AnalyticsDashboard screen
- [ ] Implement risk level bar chart using matplotlib/plotly
- [ ] Implement file type pie chart
- [ ] Add risk filter checkboxes
- [ ] Implement risk level override dropdown
- [ ] Enhance global search bar with multi-field search
- [ ] Add search history dropdown
- [ ] Implement advanced search operators
- [ ] Create search preset save/load UI
- [ ] Add search help tooltip with operator guide

### UI/UX Polish
- [ ] Consistent color scheme for status badges (yellow/green/red)
- [ ] Consistent color scheme for risk badges (green/yellow/red)
- [ ] Professional chart styling (colors, fonts, spacing)
- [ ] Smooth animations for timeline interactions
- [ ] Hover effects for timeline markers
- [ ] Loading indicators for chart generation
- [ ] Responsive layout for timeline (different window sizes)
- [ ] Tooltips for all interactive elements
- [ ] Visual feedback for bulk actions
- [ ] Error messages for invalid search syntax
- [ ] Success messages for status updates
- [ ] Professional icons for status, risk, notes

### Testing
- [ ] Test timeline display with test_evidence files (16 files)
- [ ] Test timeline zoom and scroll functionality
- [ ] Test date range filtering (various ranges)
- [ ] Test milestone display on timeline
- [ ] Test file detail panel (click markers)
- [ ] Test status assignment (all three statuses)
- [ ] Test status filtering (all combinations)
- [ ] Test bulk status updates (select multiple files)
- [ ] Test status statistics accuracy
- [ ] Test notes functionality (add, edit, delete)
- [ ] Test risk level calculation (various file types)
- [ ] Test risk level bar chart accuracy
- [ ] Test file type pie chart accuracy
- [ ] Test risk level filtering
- [ ] Test manual risk override
- [ ] Test global search (filename, type, hash)
- [ ] Test multi-field search
- [ ] Test advanced search operators (quotes, OR, NOT, wildcards)
- [ ] Test search history (save, recall, clear)
- [ ] Test search presets (save, load, delete)
- [ ] Test performance with large dataset (100+ files)
- [ ] Test all filters working simultaneously
- [ ] Test navigation between timeline and table views

---

## Definition of Done

A user story is considered "Done" when:
- [ ] All sub-user stories completed
- [ ] All acceptance criteria met and verified
- [ ] Code written and committed to repository
- [ ] Manual testing completed successfully
- [ ] No critical bugs present
- [ ] Code follows project structure (backend/, frontend/, database/)
- [ ] Database migrations applied successfully
- [ ] Charts render correctly and update in real-time
- [ ] All filters work independently and together
- [ ] Performance acceptable with large datasets
- [ ] Screenshots captured for iteration document
- [ ] User flow documented
- [ ] Code reviewed by team member

---

## Sprint 2 Deliverables

### Planned Features
1. **Timeline Grid (US-04)**
   - Horizontal timeline with case stages
   - Evidence plotted chronologically
   - Interactive markers with detail panel
   - Date range filtering
   - Milestone markers

2. **Evidence Status Tracking (US-05)**
   - Status assignment (Pending/Analyzed/Flagged)
   - Status filtering with checkboxes
   - Bulk status updates
   - Status statistics widget
   - Notes for flagged evidence

3. **Risk Level Charts (US-06)**
   - Automatic risk calculation
   - Risk level bar chart
   - File type pie chart
   - Risk filtering
   - Manual risk override

4. **Global Search (US-07)**
   - Multi-field search
   - Advanced search operators
   - Search history
   - Search presets
   - Real-time results

---

## Sprint 2 Metrics

**Planned User Stories:** 4  
**Completed User Stories:** TBD  
**Planned Sub-Stories:** 20  
**Completed Sub-Stories:** TBD  
**Completion Rate:** TBD

**Planned Hours:** 48 hours  
**Actual Hours:** TBD

---

## Team Work Division

### Gul-e-Zara (Group Lead, Developer & Tester)
**Backend Development:**
- Implement RiskAssessment class with risk calculation algorithm
- Create TimelineGenerator for timeline data preparation
- Build SearchEngine with multi-field search and operators
- Design and implement database schema updates (4 new columns, 3 new tables)
- Create migration scripts for database updates
- Implement bulk update operations
- Optimize search performance
- Add search history and preset management

**Testing:**
- Backend unit testing for risk calculation
- Integration testing (timeline + search + filters)
- Performance testing with large datasets
- Bug fixes and error handling

### Rumesha Naveed (Requirement Engineer, Developer & Tester)
**Frontend Development:**
- Implement TimelineView screen with interactive timeline
- Create AnalyticsDashboard with bar and pie charts
- Build status tracking UI (badges, filters, bulk actions)
- Implement global search bar with history and presets
- Add date range picker and zoom controls
- Create file detail panel
- Implement notes dialog
- Connect all new screens with navigation

**Documentation:**
- User stories and acceptance criteria for Sprint 2
- User flow documentation for new features
- Sprint 2 backlog creation
- Screenshots for iteration document
- Update API documentation

**Testing:**
- Frontend UI testing for all new screens
- User flow testing (timeline → analytics → search)
- Chart rendering and interaction testing
- Filter combination testing

### Shared Responsibilities
- Sprint planning and backlog refinement
- Daily standups and progress tracking
- Code reviews and pair programming
- Bug identification and fixes
- Trello board management (3 snapshots)
- Sprint retrospective
- Iteration 2 document preparation

---

## Notes

- Sprint 2 builds on Sprint 1 foundation (Evidence Engine)
- All 4 user stories from Iteration 2 of project proposal included
- 20 detailed sub-user stories with full acceptance criteria
- Database schema extensions required (4 columns, 3 tables)
- Charting library needed (matplotlib or plotly for Python)
- Performance optimization critical for large datasets
- Timeline and analytics provide visual investigation tools
- Search functionality enables quick evidence location
- Ready for Sprint 3: Reporting & History module

---

## Trello Board Snapshots

**Snapshot 1 (Sprint Start):**
- All user stories in "To Do" column
- Sprint backlog uploaded
- Tasks estimated and assigned
- Any leftovers from Sprint 1 moved to "In Progress"

**Snapshot 2 (Mid-Sprint):**
- US-04 and US-05 in "Done" or "In Progress"
- US-06 and US-07 in "In Progress" or "To Do"
- ~50% completion

**Snapshot 3 (Sprint End):**
- All user stories in "Done"
- Leftovers for Sprint 3 documented (if any)
- Completion rate calculated

---

## Product Burndown Chart Data

| Day | Planned Tasks Remaining | Actual Tasks Remaining |
|-----|------------------------|------------------------|
| 1   | 20                     |                        |
| 2   | 19                     |                        |
| 3   | 17                     |                        |
| 4   | 16                     |                        |
| 5   | 14                     |                        |
| 6   | 12                     |                        |
| 7   | 11                     |                        |
| 8   | 9                      |                        |
| 9   | 7                      |                        |
| 10  | 6                      |                        |
| 11  | 4                      |                        |
| 12  | 2                      |                        |
| 13  | 1                      |                        |
| 14  | 0                      |                        |

*Note: Fill in "Actual Tasks Remaining" column daily during Sprint 2. Create actual burndown chart in Excel/Google Sheets and include in Iteration_2.docx*

---

## Dependencies from Sprint 1

- Database connection and CRUD operations (completed)
- Evidence upload and metadata extraction (completed)
- Metadata table display (completed)
- Case management system (completed)
- File type categorization (completed)

## Risks and Mitigation

**Risk 1:** Timeline rendering performance with large datasets
- Mitigation: Implement virtualization, lazy loading, and pagination

**Risk 2:** Chart library integration complexity
- Mitigation: Research and select library early (matplotlib recommended for Python)

**Risk 3:** Search operator parsing complexity
- Mitigation: Start with basic operators, add advanced features incrementally

**Risk 4:** Database migration issues
- Mitigation: Test migration on copy of database first, backup before applying

---

## Sprint 2 Success Criteria

- [ ] Timeline displays all evidence chronologically
- [ ] Users can filter timeline by date range
- [ ] Status tracking fully functional with bulk updates
- [ ] Risk charts display accurate data
- [ ] Global search returns results in <500ms
- [ ] All filters work independently and together
- [ ] No critical bugs in new features
- [ ] Performance acceptable with 100+ files
- [ ] Code reviewed and documented
- [ ] Iteration 2 document completed
