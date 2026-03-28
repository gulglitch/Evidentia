# Sprint 2 Planning Document - US-04 & US-05

## Evidentia - Timeline & Analytics Module

**Document Purpose:** Detailed planning and implementation guide for User Story 4 (Timeline Grid) and User Story 5 (Evidence Status Tracking)

**Sprint:** Sprint 2 (Weeks 3-4)  
**Date Created:** March 28, 2026  
**Team Members:** Gul-e-Zara, Rumesha Naveed

---

## US-04: Timeline Grid - Implementation Plan

### Overview
Build an interactive timeline visualization that displays case milestones and evidence files chronologically, allowing investigators to see the sequence of events at a glance.

### Technical Architecture

#### Database Changes
**New Table: milestones**
```sql
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    milestone_name TEXT NOT NULL,
    milestone_date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(id)
);
```

**Sample Milestones:**
- Case Created (auto-generated when case created)
- First Evidence Upload (auto-generated on first upload)
- Analysis Started (manual or auto when first file marked analyzed)

#### Backend Components

**1. TimelineGenerator Class (backend/app/timeline_generator.py)**

Responsibilities:
- Fetch all evidence for a case with date information
- Sort evidence chronologically
- Calculate date range (min/max dates)
- Prepare data structure for timeline visualization
- Filter evidence by date range
- Fetch and integrate milestone data

Key Methods:
```python
def get_timeline_data(case_id, date_from=None, date_to=None):
    """Returns evidence and milestones for timeline display"""
    
def calculate_date_range(case_id):
    """Returns earliest and latest dates in evidence"""
    
def filter_by_date_range(evidence_list, date_from, date_to):
    """Filters evidence within specified date range"""
```

**2. Database Extensions (backend/app/database.py)**

Add methods:
```python
def create_milestone(case_id, milestone_name, milestone_date, description):
    """Creates a new milestone for a case"""
    
def get_milestones(case_id):
    """Retrieves all milestones for a case"""
    
def get_evidence_date_range(case_id):
    """Returns min and max dates from evidence"""
```

#### Frontend Components

**1. TimelineView Screen (frontend/src/timeline_view.py)**

Main Components:
- Timeline canvas (horizontal scrollable area)
- Date axis (bottom of timeline)
- Evidence markers (plotted points)
- Milestone markers (vertical lines)
- Detail panel (slides in from right)
- Date range filter controls (top bar)
- Zoom controls (buttons or slider)

Layout Structure:
```
┌─────────────────────────────────────────────────────┐
│  Timeline for: [Case Name]          [Date Filters]  │
├─────────────────────────────────────────────────────┤
│  Milestones: Case Created → Evidence → Analysis     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ●  ●    ●  ●  ●      ●    ●  ●                    │
│  ├──┼────┼──┼──┼──────┼────┼──┼──────────────────  │
│  Jan    Feb   Mar    Apr   May  Jun                │
│                                                      │
│  [Zoom: - Day Week Month +]                        │
└─────────────────────────────────────────────────────┘
```

Key Features:
- Use QGraphicsView and QGraphicsScene for timeline canvas
- Custom QGraphicsItem for evidence markers
- Color-coded markers by file type
- Hover tooltips showing file details
- Click handler to open detail panel
- Smooth scrolling and zooming

**2. File Detail Panel (part of TimelineView)**

Displays when marker clicked:
- Filename
- File type and extension
- File size
- Created date
- Modified date
- Accessed date
- MD5 hash
- Metadata (if available)
- Action buttons: "Open File Location", "View in Table"

**3. Date Range Filter Widget**

Components:
- "From" QDateEdit widget
- "To" QDateEdit widget
- "Apply Filter" button
- "Reset" button
- File count label

### Implementation Steps

**Phase 1: Database Setup (2 hours)**
1. Create milestones table in schema.sql
2. Add milestone CRUD methods to database.py
3. Add date range query methods
4. Test database operations
5. Create sample milestones in seed.sql

**Phase 2: Backend Logic (3 hours)**
1. Create timeline_generator.py
2. Implement get_timeline_data() method
3. Implement date range filtering
4. Implement milestone integration
5. Test with sample data

**Phase 3: Frontend Timeline Canvas (5 hours)**
1. Create timeline_view.py with QGraphicsView
2. Implement date axis rendering
3. Implement evidence marker plotting
4. Add color coding by file type
5. Implement hover tooltips
6. Add click handlers for markers

**Phase 4: Milestone Display (2 hours)**
1. Add milestone markers to timeline
2. Style milestone lines (dashed, accent color)
3. Add milestone labels
4. Test milestone positioning

**Phase 5: Detail Panel (2 hours)**
1. Create sliding detail panel widget
2. Implement panel show/hide animations
3. Populate panel with file details
4. Add action buttons
5. Test panel interactions

**Phase 6: Date Range Filtering (2 hours)**
1. Create date filter widget
2. Connect date pickers to timeline
3. Implement filter logic
4. Add reset functionality
5. Update file count display

**Phase 7: Testing & Polish (2 hours)**
1. Test with test_evidence files (16 files)
2. Test date range filtering
3. Test zoom and scroll
4. Fix bugs and edge cases
5. Polish UI styling

**Total Estimated Time: 18 hours** (buffer included)

### Testing Checklist

- [ ] Timeline displays all 16 test evidence files
- [ ] Files plotted at correct dates
- [ ] Markers color-coded by type
- [ ] Hover shows correct file details
- [ ] Click opens detail panel with correct info
- [ ] Detail panel closes properly
- [ ] Milestones display at correct positions
- [ ] Date range filter works correctly
- [ ] Reset button clears filters
- [ ] File count updates with filters
- [ ] Timeline scrolls smoothly
- [ ] Zoom controls work
- [ ] No crashes with empty case
- [ ] Performance acceptable with 100+ files

---

## US-05: Evidence Status Tracking - Implementation Plan

### Overview
Implement a comprehensive status tracking system that allows investigators to mark evidence as Pending, Analyzed, or Flagged, with filtering and bulk update capabilities.

### Technical Architecture

#### Database Changes

**Modify evidence table:**
```sql
ALTER TABLE evidence ADD COLUMN status TEXT DEFAULT 'Pending';
ALTER TABLE evidence ADD COLUMN notes TEXT;
```

Valid status values: 'Pending', 'Analyzed', 'Flagged'

**Migration Script (database/migration_sprint2.sql):**
```sql
-- Add status column if not exists
ALTER TABLE evidence ADD COLUMN status TEXT DEFAULT 'Pending';

-- Add notes column if not exists
ALTER TABLE evidence ADD COLUMN notes TEXT;

-- Update existing records to have default status
UPDATE evidence SET status = 'Pending' WHERE status IS NULL;
```

#### Backend Components

**1. Database Extensions (backend/app/database.py)**

Add methods:
```python
def update_evidence_status(evidence_id, status):
    """Updates status for a single evidence file"""
    
def bulk_update_status(evidence_ids, status):
    """Updates status for multiple evidence files"""
    
def get_status_statistics(case_id):
    """Returns count of files by status"""
    
def update_evidence_notes(evidence_id, notes):
    """Updates notes for flagged evidence"""
    
def get_evidence_notes(evidence_id):
    """Retrieves notes for an evidence file"""
```

**2. Status Validator (backend/app/helpers.py)**

Add validation:
```python
VALID_STATUSES = ['Pending', 'Analyzed', 'Flagged']

def validate_status(status):
    """Validates status value"""
    return status in VALID_STATUSES
```

#### Frontend Components

**1. Enhanced MetadataTable (frontend/src/metadata_table.py)**

New Columns:
- Checkbox column (leftmost) for bulk selection
- Status column (colored badge)

New Features:
- Status dropdown on badge click
- Bulk selection checkboxes
- "Select All" checkbox in header
- Bulk actions dropdown
- Status filter checkboxes in sidebar

**2. Status Badge Widget**

Visual Design:
- Pending: Yellow badge with "Pending" text
- Analyzed: Green badge with "Analyzed" text
- Flagged: Red badge with "Flagged" text

Interaction:
- Click badge opens dropdown menu
- Dropdown shows 3 status options
- Select option updates status immediately
- Brief highlight animation on update

**3. Status Filter Panel**

Components:
- "Filter by Status" label
- Three checkboxes:
  - ☑ Show Pending
  - ☑ Show Analyzed
  - ☑ Show Flagged
- All checked by default
- Real-time filtering as checkboxes toggled

**4. Bulk Actions Toolbar**

Appears when files selected:
- "X files selected" label
- Dropdown: "Bulk Actions"
  - Mark as Pending
  - Mark as Analyzed
  - Mark as Flagged
- "Clear Selection" button

**5. Status Statistics Widget**

Display:
```
┌─────────────────────────────────────┐
│  Investigation Progress             │
├─────────────────────────────────────┤
│  Pending: 8 | Analyzed: 5 | Flagged: 3 │
│  [████████░░░░░░░░] 31% Complete    │
└─────────────────────────────────────┘
```

Features:
- Real-time count updates
- Progress bar showing % analyzed
- Click count to filter by that status

**6. Notes Dialog (frontend/src/notes_dialog.py)**

For flagged evidence:
- Modal dialog
- Multi-line text area (500 char limit)
- Character counter
- Save and Cancel buttons
- Displays existing notes if present

### Implementation Steps

**Phase 1: Database Setup (1 hour)**
1. Create migration script
2. Add status and notes columns
3. Update existing records with default status
4. Add status methods to database.py
5. Test database operations

**Phase 2: Backend Status Logic (2 hours)**
1. Implement update_evidence_status()
2. Implement bulk_update_status()
3. Implement get_status_statistics()
4. Implement notes methods
5. Add status validation
6. Test all methods

**Phase 3: Status Badge UI (2 hours)**
1. Create status badge widget
2. Add status column to metadata table
3. Implement badge click dropdown
4. Connect dropdown to update method
5. Add visual feedback on update
6. Style badges (colors, fonts)

**Phase 4: Bulk Selection (2 hours)**
1. Add checkbox column to table
2. Implement "Select All" checkbox
3. Track selected rows
4. Create bulk actions toolbar
5. Implement bulk update logic
6. Add confirmation dialog

**Phase 5: Status Filtering (2 hours)**
1. Create status filter panel
2. Add three checkboxes
3. Implement filter logic
4. Connect filters to table display
5. Ensure compatibility with existing filters
6. Test all filter combinations

**Phase 6: Status Statistics (1 hour)**
1. Create statistics widget
2. Fetch status counts from database
3. Calculate percentage
4. Render progress bar
5. Add click-to-filter functionality
6. Update in real-time

**Phase 7: Notes Functionality (2 hours)**
1. Create notes_dialog.py
2. Add notes icon to flagged files
3. Implement dialog open/close
4. Save notes to database
5. Display notes preview on hover
6. Style notes icon (blue when has notes)

**Phase 8: Testing & Polish (2 hours)**
1. Test status updates (single and bulk)
2. Test status filtering
3. Test statistics accuracy
4. Test notes functionality
5. Test with multiple filter combinations
6. Fix bugs and edge cases
7. Polish UI styling

**Total Estimated Time: 14 hours** (buffer included)

### Testing Checklist

- [ ] Status column displays in table
- [ ] Status badges show correct colors
- [ ] Click badge opens dropdown
- [ ] Status updates save to database
- [ ] Status updates reflect immediately in UI
- [ ] Checkboxes select/deselect rows
- [ ] "Select All" works correctly
- [ ] Bulk actions update multiple files
- [ ] Confirmation dialog appears for bulk actions
- [ ] Status filters work independently
- [ ] Status filters work with other filters
- [ ] Statistics show correct counts
- [ ] Progress bar calculates correctly
- [ ] Click statistics filters table
- [ ] Notes dialog opens for flagged files
- [ ] Notes save and load correctly
- [ ] Notes icon changes when notes exist
- [ ] Hover shows notes preview
- [ ] No crashes with edge cases

---

## Integration Plan

### Connecting US-04 and US-05

**Timeline View Integration:**
- Timeline markers show status as color overlay
- Filter timeline by status (show only analyzed files, etc.)
- Status changes update timeline in real-time

**Navigation Flow:**
1. User uploads evidence (Sprint 1)
2. User views metadata table with status column (US-05)
3. User marks files as analyzed/flagged (US-05)
4. User switches to timeline view (US-04)
5. Timeline shows analyzed files with visual indicator
6. User clicks timeline marker to see details
7. Detail panel shows status and allows status change
8. User returns to table view to continue analysis

### Shared Components

**MainWindow Navigation:**
- Add "Timeline" button to navigation bar
- Add "Analytics" button (for Sprint 2 charts)
- Maintain current case context across views
- Status bar shows current view and case name

**Database Queries:**
- Timeline queries respect status filters
- Statistics include timeline date ranges
- Efficient queries to avoid performance issues

---

## Risk Management

### Potential Risks

**Risk 1: Timeline Performance with Large Datasets**
- Impact: High
- Probability: Medium
- Mitigation: Implement lazy loading, render only visible markers, use efficient data structures

**Risk 2: Status Update Conflicts**
- Impact: Medium
- Probability: Low
- Mitigation: Use database transactions, implement optimistic locking

**Risk 3: UI Complexity**
- Impact: Medium
- Probability: Medium
- Mitigation: Break into smaller components, test incrementally, use existing Qt widgets

**Risk 4: Date Parsing Issues**
- Impact: Low
- Probability: Medium
- Mitigation: Standardize date format in database, handle missing dates gracefully

---

## Success Criteria

### US-04 Success Criteria
- [ ] Timeline displays all evidence chronologically
- [ ] Users can zoom and scroll timeline smoothly
- [ ] Date range filtering works correctly
- [ ] Milestones display at correct positions
- [ ] Detail panel shows complete file information
- [ ] Performance acceptable with 100+ files
- [ ] No critical bugs

### US-05 Success Criteria
- [ ] Users can assign and change status for any file
- [ ] Bulk status updates work for multiple files
- [ ] Status filtering works independently and with other filters
- [ ] Statistics display accurate counts and percentages
- [ ] Notes functionality works for flagged files
- [ ] UI is intuitive and responsive
- [ ] No data loss or corruption

---

## Dependencies

### From Sprint 1
- ✅ Database connection and CRUD operations
- ✅ Evidence table with metadata
- ✅ MetadataTable display
- ✅ Case management system
- ✅ MainWindow navigation framework

### For Sprint 2 (US-06 & US-07)
- Timeline data structure (from US-04)
- Status tracking (from US-05)
- Filter framework (from US-05)

---

## Team Assignments

### Gul-e-Zara (Backend Focus)
**US-04 Tasks:**
- Create milestones table and migration
- Implement TimelineGenerator class
- Add database methods for timeline queries
- Optimize date range queries
- Backend testing

**US-05 Tasks:**
- Add status and notes columns
- Implement status update methods
- Implement bulk update operations
- Add status statistics queries
- Backend testing

### Rumesha Naveed (Frontend Focus)
**US-04 Tasks:**
- Create TimelineView screen
- Implement timeline canvas with QGraphicsView
- Build evidence markers and milestone display
- Create detail panel
- Implement date range filter UI
- Frontend testing

**US-05 Tasks:**
- Add status column to MetadataTable
- Create status badge widget
- Implement bulk selection UI
- Build status filter panel
- Create status statistics widget
- Create notes dialog
- Frontend testing

### Shared Tasks
- Integration testing
- Bug fixes
- Code reviews
- Documentation updates
- Trello board updates

---

## Timeline (14 Days)

**Week 1 (Days 1-7):**
- Days 1-2: Database setup and backend for both US-04 and US-05
- Days 3-5: Frontend development for US-04 (Timeline)
- Days 6-7: Frontend development for US-05 (Status tracking)

**Week 2 (Days 8-14):**
- Days 8-9: Complete remaining features
- Days 10-11: Integration and testing
- Days 12-13: Bug fixes and polish
- Day 14: Final testing and documentation

---

## Deliverables

1. **Code:**
   - backend/app/timeline_generator.py
   - frontend/src/timeline_view.py
   - frontend/src/notes_dialog.py
   - database/migration_sprint2.sql
   - Updated database.py
   - Updated metadata_table.py
   - Updated main_window.py

2. **Documentation:**
   - Updated API documentation
   - User flow documentation
   - Screenshots for iteration report

3. **Testing:**
   - Test results document
   - Bug tracking log

---

## Notes

- Keep UI consistent with Sprint 1 design (dark theme, cyan accents)
- Ensure all features work with existing test_evidence folder
- Maintain backward compatibility with Sprint 1 database
- Focus on user experience and intuitive interactions
- Regular commits to Git repository
- Daily standup meetings to track progress

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Status:** Ready for Implementation
