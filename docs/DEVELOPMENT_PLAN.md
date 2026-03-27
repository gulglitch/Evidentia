# Evidentia - Development Plan

## Project Overview
**Total Duration:** 6 weeks (3 iterations × 2 weeks each)  
**Team Size:** 2 members  
**Working Days per Iteration:** ~10 days

---

## Color Scheme & Design System (From Prototypes)

### Primary Palette
| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-darkest` | `#0a1929` | Main app background |
| `--bg-dark` | `#0d2137` | Card/panel backgrounds |
| `--bg-card` | `#122a3a` | Elevated cards, sidebar panels |
| `--bg-card-hover` | `#163545` | Card hover state |
| `--border` | `#1a4a5a` | Card borders, dividers |
| `--border-light` | `#2a6a7a` | Table gridlines, subtle borders |

### Accent Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--accent-primary` | `#00d4aa` | Headings, section titles, active links |
| `--accent-cyan` | `#40e0d0` | Buttons, highlights, interactive elements |
| `--accent-glow` | `#2dd4bf` | Button hover, focus rings |

### Text Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--text-primary` | `#e0e6ed` | Body text, table content |
| `--text-secondary` | `#8899aa` | Muted labels, timestamps |
| `--text-heading` | `#00d4aa` | Section titles (cyan/turquoise) |
| `--text-white` | `#ffffff` | Bold stats, emphasis |

### Status & Risk Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--risk-low` | `#00d4aa` | Low risk, success indicators |
| `--risk-medium` | `#f0c040` | Medium risk, warnings |
| `--risk-high` | `#ff6b6b` | High risk, alerts |
| `--status-open` | `#40e0d0` | Open/Active cases |
| `--status-review` | `#40e0d0` | In Review (shorter bar) |
| `--status-closed` | `#40e0d0` | Closed cases (shortest bar) |

### Component Styles
| Component | Style Rules |
|-----------|-------------|
| **Cards** | Background `#122a3a`, border 1px solid `#1a4a5a`, rounded 8px |
| **Buttons** | Background `#40e0d0`, text `#0a1929`, rounded 6px, padding 8px 20px |
| **Inputs** | Background `#0d2137`, border 1px solid `#1a4a5a`, text `#e0e6ed` |
| **Tables** | Header bg `#122a3a`, rows alternate `#0d2137`/`#0a1929`, gridlines `#1a4a5a` |
| **Header Bar** | Background `#0d2137`, border-bottom 1px `#1a4a5a`, "Evidentia" in `#00d4aa` |
| **Footer** | Background `#0d2137`, text `#40e0d0`, centered |
| **Circle Badges** | Background `#2a6a7a`, text `#ffffff`, round, used for case type counts |
| **Progress Bars** | Track `#0d2137`, fill `#40e0d0` |
| **Checkboxes** | Unchecked border `#2a6a7a`, checked fill `#40e0d0` |
| **Radio Buttons** | Same as checkboxes |

### Typography
| Element | Size | Weight | Color |
|---------|------|--------|-------|
| App Title ("Evidentia") | 22px | Bold | `#00d4aa` |
| Section Headings | 18px | Bold | `#00d4aa` |
| Sub-headings | 14px | Semi-bold | `#00d4aa` |
| Body Text | 13px | Normal | `#e0e6ed` |
| Table Headers | 13px | Bold | `#e0e6ed` |
| Muted Text / Timestamps | 12px | Normal | `#8899aa` |
| Stats Numbers | 36px | Bold | `#ffffff` |

### Footer Convention
All screens include:  
`© 2026 Evidentia Forensics | Secure Digital Investigation Platform`  
Color: `#40e0d0` on `#0d2137` background

---

## Screen Flow Overview

```
[Screen 1: Splash/Welcome]
        ↓
[Screen 2: Sign Up / Login]
        ↓
[Screen 3: User Profile Setup]
        ↓
[Screen 4: Investigation Statistics Dashboard]
        ↓
    ┌───┴───┐
    ↓       ↓
[Screen 5: New Case]  [Screen 6: Open Existing Case]
        ↓
[Screen 7: Case Workspace]
    ├── [Landing: Case Detail View]
    ├── [Evidence Management View]
    │     ├── Sidebar Filters
    │     ├── Metadata Table
    │     └── File Upload Zone
    ├── [Screen 7c: Timeline Grid]
    ├── [Screen 7d: Analytics/Stats]
    └── [Screen 7e: Activity Log]
        ↓
[Screen 8: Report Generator]
        ↓
[Screen 9: Settings]
```

---

## Detailed Screen Specifications

### Screen 1: Splash Screen
**Purpose:** App branding and loading  
**Time to build:** 2 hours

| Element | Description |
|---------|-------------|
| Logo | Evidentia logo centered |
| Tagline | "Digital Forensics Made Simple" |
| Loading bar | Shows initialization progress |
| Version | "v1.0 - Iteration X" |

**Auto-transition:** 2 seconds → Screen 2

---

### Screen 2: Login / Sign Up Screen
**Purpose:** User authentication (local/offline)  
**Time to build:** 4 hours

| Element | Type | Description |
|---------|------|-------------|
| App Logo | Image | Top centered |
| Username | Text Input | Required |
| Password | Password Input | Required |
| Remember Me | Checkbox | Save credentials locally |
| Login Button | Button | Validate and proceed |
| Sign Up Link | Text Link | Switch to registration |
| Forgot Password | Text Link | Recovery option |

**Sign Up Form (toggles with Login):**
| Element | Type | Validation |
|---------|------|------------|
| Full Name | Text Input | Required |
| Email | Text Input | Email format |
| Username | Text Input | Min 4 chars |
| Password | Password Input | Min 6 chars |
| Confirm Password | Password Input | Must match |
| Create Account | Button | Submit |

**Data Storage:** SQLite `users` table (local only, no internet)

---

### Screen 3: User Profile Setup
**Purpose:** Collect user role and preferences  
**Time to build:** 3 hours  
**When shown:** First login only

| Element | Type | Options |
|---------|------|---------|
| Welcome Header | Text | "Welcome to Evidentia, [Name]!" |
| Role Selection | Radio Buttons | • Forensic Investigator<br>• Legal Professional<br>• Cybersecurity Analyst<br>• Student/Learner<br>• Other |
| Organization | Text Input | Optional |
| Primary Use | Dropdown | • Case Management<br>• Evidence Analysis<br>• Report Generation<br>• Learning/Training |
| Continue Button | Button | Save and go to Dashboard |
| Skip for Now | Link | Go to Dashboard |

**Stored in:** `user_preferences` table

---

### Screen 4: Investigation Statistics Dashboard
**Purpose:** Central hub with overview stats and case management  
**Time to build:** 6 hours  
**Prototype Reference:** "Investigation Statistics Dashboard" mockup

**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER BAR: "Evidentia"                         [Logout]       │
├──────────────────────────────────────────────────────────────────┤
│               Investigation Statistics Dashboard                 │
├──────────────┬───────────────┬───────────────────────────────────┤
│  Total Cases │ Team Members  │  Case Status Distribution        │
│     245      │      15       │  Open Cases   ████████ 38        │
│  [New Case]  │ [Add Investig]│  In Review    ██████ 21          │
│              │               │  Closed Cases ████ 186           │
├──────────────┴───────────────┼───────────────────────────────────┤
│  Case Types                  │  Risk Level Distribution         │
│  (42) (68) (31) (12)        │     104                          │
│  Cyber  FF   DT   IB        │  59      82                      │
│                              │  ▓▓  ▓▓▓  ▓▓                    │
├──────────────────────────────│  Low Med High                    │
│  Report Generation Summary   │                                  │
│  Total Evidence Files: 126   │                                  │
│  Files Analyzed: 94          │                                  │
│  Pending Review: 32          │                                  │
│  [Generate Final Report]     │                                  │
├──────────────────────────────┴───────────────────────────────────┤
│  © 2026 Evidentia Forensics | Secure Digital Investigation      │
└──────────────────────────────────────────────────────────────────┘
```

**Sections:**

| Section | Details |
|---------|---------|
| **Total Cases** | Large stat number, "New Case" cyan button below |
| **Team Members** | Large stat number, "Add Investigator" cyan button below |
| **Case Status Distribution** | Horizontal progress bars: Open, In Review, Closed with counts |
| **Case Types** | Circle badges with counts: Cybercrime, Financial Fraud, Data Theft, Internal Breach |
| **Risk Level Distribution** | Vertical bar chart (Low/Medium/High) in cyan shades |
| **Report Generation Summary** | Total files, analyzed, pending counts + "Generate Final Report" button |

---

### Screen 5: New Case Creation
**Purpose:** Start a new investigation  
**Time to build:** 3 hours  
**Type:** Modal dialog over Dashboard

| Field | Type | Required |
|-------|------|----------|
| Case Name | Text Input | ✓ |
| Case Type | Dropdown | ✓ |
| Description | Text Area | |
| Priority | Radio | Low / Medium / High |
| Tags | Tag Input | Multiple optional tags |

**Case Type Options:**
- Financial Fraud
- Cybercrime
- Data Breach
- Intellectual Property Theft
- Corporate Investigation
- Personal Investigation
- Other

**Buttons:** Cancel | Create Case

**On Create:** → Screen 7 (Case Workspace)

---

### Screen 6: Open Existing Case
**Purpose:** Browse and select previous cases  
**Time to build:** 3 hours  
**Type:** Modal dialog or dedicated screen

**Features:**
| Feature | Description |
|---------|-------------|
| Search Bar | Filter by case name |
| Filter Dropdown | By status, type, date |
| Sort Options | Name, Date, Evidence count |
| Case Cards | Grid of cases with preview |

**Case Card Shows:**
- Case name
- Type badge
- Created date
- Evidence count
- Status indicator

**Actions per card:** Open | Archive | Delete

---

### Screen 7: Case Workspace (Main Work Area)
**Purpose:** Primary investigation interface  
**Time to build:** 12 hours (largest screen)

This screen has two main views: the **Case Overview** (landing) and the **Evidence Management** tabs.

---

#### Screen 7 - Landing: Case Detail View
**Prototype Reference:** "Case 0013: Financial Fraud Investigation" mockup

**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│           Case 0013: Financial Fraud Investigation               │
├──────────────────┬──────────────────┬────────────────────────────┤
│  Case Summary    │  Case Dates      │  Evidence Summary          │
│  Investigator:   │  Opened:         │  Total Files: 18           │
│    Jane Smith    │   12 Oct 2025    │  Analyzed: 12              │
│  Team Members: 4 │  Closed:         │  Pending: 6               │
│                  │   15 Nov 2025    │                            │
├──────────────────┴──────────────────┴────────────────────────────┤
│                     Case Overview                                │
│  "This investigation focuses on suspected financial fraud..."    │
├──────────────────────────────────────────────────────────────────┤
│  Recent Case Timeline                                            │
│  12 Oct — Case Created                                           │
│  13 Oct — Evidence Uploaded (6 files)                            │
│                                        [View Full Timeline]      │
├──────────────────────────────────────────────────────────────────┤
│  © 2026 Evidentia Forensics | Secure Digital Investigation       │
└──────────────────────────────────────────────────────────────────┘
```

**Sections:**

| Section | Details |
|---------|---------|
| **Case Title Header** | "Case [ID]: [Name]" in cyan on dark card |
| **Case Summary Card** | Investigator name, Team Members count |
| **Case Dates Card** | Opened date, Closed date (or "Ongoing") |
| **Evidence Summary Card** | Total Files, Analyzed, Pending counts |
| **Case Overview** | Description text in a bordered panel |
| **Recent Case Timeline** | Last few activities, "View Full Timeline" cyan button |

---

#### Screen 7 - Main View: Evidence Management
**Prototype Reference:** "Evidence Management" mockup

**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│                     Evidence Management                          │
├────────────────┬─────────────────────────────────────────────────┤
│  SIDEBAR       │  Metadata Overview                              │
│                │  "Explore detailed metadata information..."     │
│  File Type     │  ┌─────┬──────────┬──────┬──────┬────────┐     │
│  ☐ PDF         │  │ ID  │File Name │ Type │ Date │ Status │     │
│  ☐ Image       │  ├─────┼──────────┼──────┼──────┼────────┤     │
│  ☐ ZIP         │  │     │          │      │      │        │     │
│  ☐ Email       │  │     │          │      │      │        │     │
│                │  │     │          │      │      │        │     │
│  Upload Date   │  └─────┴──────────┴──────┴──────┴────────┘     │
│  ○ Last 24 hrs │                                                 │
│  ○ Last week   │         Upload File Here                        │
│  ○ Last month  │        ┌─────────────────┐                      │
│                │        │       +         │                      │
│  Status        │        └─────────────────┘                      │
│  ☐ Analyzed    │                                                 │
│  ☐ Pending     │                                                 │
│  ☐ Flagged     │                                                 │
├────────────────┴─────────────────────────────────────────────────┤
│  © 2026 Evidentia Forensics | Secure Digital Investigation       │
└──────────────────────────────────────────────────────────────────┘
```

**Left Sidebar Filters:**

| Filter Group | Type | Options |
|-------------|------|---------|
| **File Type** | Checkboxes | PDF, Image, ZIP, Email |
| **Upload Date** | Radio Buttons | Last 24 hours, Last week, Last month |
| **Status** | Checkboxes | Analyzed, Pending, Flagged |

**Main Content Area:**

| Section | Details |
|---------|---------|
| **Title** | "Metadata Overview" in cyan |
| **Subtitle** | "Explore detailed metadata information for files..." |
| **Table** | Columns: ID, File Name, Type, Date, Status |
| **Upload Zone** | "Upload File Here" text + clickable "+" area below table |

---

#### Screen 7a: Evidence Upload (via Upload Zone)
**Purpose:** Bulk folder import  
**Time to build:** 4 hours

| Element | Description |
|---------|-------------|
| Drop Zone | "+" area at bottom of Evidence Management screen |
| Browse Button | Manual folder/file selection |
| Progress Bar | Shows import progress |
| File Counter | "Importing X of Y files..." |
| Cancel Button | Stop import |

**Post-Import:**
- Show results summary
- Auto-switch to Evidence Table

#### Screen 7b: Evidence Table Tab
**Purpose:** View all evidence metadata  
**Time to build:** 5 hours

| Column | Sortable | Filterable |
|--------|----------|------------|
| ID | ✓ | |
| File Name | ✓ | ✓ (search) |
| Type | ✓ | ✓ (dropdown) |
| Size | ✓ | |
| Created Date | ✓ | ✓ (range) |
| Modified Date | ✓ | ✓ (range) |
| Status | ✓ | ✓ (checkbox) |
| Risk Level | ✓ | ✓ (checkbox) |

**Row Actions:**
- Click: View metadata details (side panel)
- Right-click: Context menu (Open, Flag, Set Risk, Delete)

**Bulk Actions:**
- Select multiple → Change status, Change risk, Export

#### Screen 7c: Timeline Tab
**Purpose:** Visual chronological view  
**Time to build:** 6 hours  
**Prototype Reference:** "Timeline Grid" from main dashboard mockup

**Layout:**
```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER: "Evidentia"                                [Logout]     │
├────────────────────────────────────────────┬─────────────────────┤
│  Timeline Grid                             │  Quick Stats        │
│                                            │                     │
│  ●────●──────────●─────●──────●────●       │  Case Number: 0013  │
│  Case   Evidence   Forensic  Inter  Report │  Investigator:      │
│  Created Collected  Analysis views  Drafted│    Jane Smith       │
│                                     Closed │  Current Status:    │
│                                            │    In Progress      │
├────────────────────────────────────────────┴─────────────────────┤
│  Recent Activity                                                 │
│                                                                  │
│  Investigative meeting held on 12th Oct          2 hours ago     │
│  Evidence submitted for review                   5 hours ago     │
│  Suspect Interview scheduled                     8 hours ago     │
├──────────────────────────────────────────────────────────────────┤
│  © 2026 Evidentia Forensics | Secure Digital Investigation       │
└──────────────────────────────────────────────────────────────────┘
```

**Elements:**

| Element | Description |
|---------|-------------|
| **Timeline Grid** | Horizontal progress bar with milestone dots connected by lines |
| **Milestone Labels** | Case Created → Evidence Collected → Forensic Analysis → Interviews → Report Drafted → Closed |
| **Milestone Dots** | Cyan circles (`#40e0d0`) on connecting line |
| **Quick Stats Panel** | Right-side card showing Case Number, Investigator, Current Status |
| **Recent Activity** | Feed list with action description (left) and relative time (right, muted) |

#### Screen 7d: Analytics Tab
**Purpose:** Charts and statistics  
**Time to build:** 4 hours  
**Prototype Reference:** Risk Level Distribution + Case Status Distribution from dashboard mockup

**Charts:**
1. **Risk Level Distribution** (Vertical Bar Chart)
   - Low / Medium / High counts
   - Bars in cyan (`#40e0d0`) shades
   - Values displayed above each bar

2. **Case Status Distribution** (Horizontal Progress Bars)
   - Open Cases → count with filled bar
   - In Review → count with shorter bar
   - Closed Cases → count with varied bar
   - All bars in `#40e0d0`

3. **Case Types** (Circle Badges)
   - Cybercrime, Financial Fraud, Data Theft, Internal Breach
   - Numbered circles in `#2a6a7a` background

4. **Report Generation Summary** (Stats Card)
   - Total Evidence Files count
   - Files Analyzed count
   - Pending Review count
   - "Generate Final Report" button (`#40e0d0`)

#### Screen 7e: Activity Log Tab
**Purpose:** History of actions  
**Time to build:** 2 hours

| Column | Description |
|--------|-------------|
| Timestamp | When action occurred |
| Action | What was done |
| Details | Additional info |
| User | Who did it |

**Filterable by:** Date range, Action type

---

### Screen 8: Report Generator
**Purpose:** Create final investigation report  
**Time to build:** 4 hours  
**Type:** Modal wizard (3 steps)

**Step 1: Select Content**
- [ ] Include Executive Summary
- [ ] Include Evidence Table
- [ ] Include Timeline Visualization
- [ ] Include Risk Analysis Charts
- [ ] Include Activity Log

**Step 2: Customize**
- Report Title: [text input]
- Author Name: [text input]
- Date Range: [date picker]
- Include confidentiality notice: [checkbox]
- Add custom notes: [text area]

**Step 3: Preview & Export**
- PDF Preview pane
- Export as PDF button
- Save Draft button

---

### Screen 9: Settings
**Purpose:** App configuration  
**Time to build:** 2 hours

**Sections:**

| Section | Options |
|---------|---------|
| **Profile** | Edit name, email, password |
| **Preferences** | Theme (Light/Dark), Language |
| **Data** | Export all data, Clear cache, Backup database |
| **About** | Version, Credits, Help link |

---

## Sidebar Navigation (Evidence Management Screen)

Left sidebar filter panel (matches Evidence Management prototype):

```
┌──────────────────┐
│ File Type        │  (cyan heading)
│ ☐ PDF            │
│ ☐ Image          │
│ ☐ ZIP            │
│ ☐ Email          │
├──────────────────┤
│ Upload Date      │  (cyan heading)
│ ○ Last 24 hours  │
│ ○ Last week      │
│ ○ Last month     │
├──────────────────┤
│ Status           │  (cyan heading)
│ ☐ Analyzed       │
│ ☐ Pending        │
│ ☐ Flagged        │
└──────────────────┘
```

**Styling:**
- Panel background: `#122a3a`
- Headings: `#00d4aa` 14px bold
- Checkbox/Radio labels: `#00d4aa` 13px
- Unchecked border: `#2a6a7a`
- Checked fill: `#40e0d0`

### Global Header Bar (All Screens)

```
┌──────────────────────────────────────────────────────────────────┐
│  Evidentia                                        [Logout]       │
│  (#00d4aa, bold 22px)                    (cyan outlined button)  │
└──────────────────────────────────────────────────────────────────┘
Background: #0d2137 | Border-bottom: 1px #1a4a5a
```

---

## Iteration Breakdown with Time Estimates

### Iteration 1: Evidence Engine (Weeks 1-2)
**Goal:** Import files, extract metadata, display in table

| Task | Screen | Hours | Assignee |
|------|--------|-------|----------|
| Splash Screen | 1 | 2 | Dev 1 |
| Login/Signup UI | 2 | 4 | Dev 1 |
| User authentication logic | 2 | 4 | Dev 1 |
| Profile Setup Screen | 3 | 3 | Dev 1 |
| Database schema (users, cases, evidence) | - | 4 | Dev 2 |
| Dashboard Layout | 4 | 6 | Dev 2 |
| New Case Dialog | 5 | 3 | Dev 2 |
| Case Workspace skeleton | 7 | 4 | Dev 1 |
| Evidence Upload Drop Zone | 7a | 4 | Dev 2 |
| File Scanner + Metadata Extractor | - | 6 | Dev 2 |
| Evidence Table View | 7b | 5 | Dev 1 |
| Testing & Bug Fixes | - | 5 | Both |
| **Total** | | **50 hrs** | |

**Per person:** ~25 hours = ~2.5 hrs/day for 10 working days ✓

---

### Iteration 2: Timeline & Analytics (Weeks 3-4)
**Goal:** Interactive timeline, charts, search/filter

| Task | Screen | Hours | Assignee |
|------|--------|-------|----------|
| Open Case Browser | 6 | 3 | Dev 1 |
| Timeline Widget | 7c | 6 | Dev 1 |
| Timeline zoom controls | 7c | 2 | Dev 1 |
| Risk Bar Chart | 7d | 4 | Dev 2 |
| File Type Pie Chart | 7d | 3 | Dev 2 |
| Status Donut Chart | 7d | 3 | Dev 2 |
| Global Search functionality | 7 | 4 | Dev 1 |
| Filter integration (sidebar → table) | 7 | 4 | Dev 2 |
| Evidence status update UI | 7b | 3 | Dev 1 |
| Risk level assignment UI | 7b | 3 | Dev 2 |
| Context menu for evidence | 7b | 3 | Dev 1 |
| Testing & Bug Fixes | - | 6 | Both |
| **Total** | | **44 hrs** | |

**Per person:** ~22 hours = ~2.2 hrs/day ✓

---

### Iteration 3: Reporting & Polish (Weeks 5-6)
**Goal:** Activity log, PDF reports, settings, polish

| Task | Screen | Hours | Assignee |
|------|--------|-------|----------|
| Activity Log Tab | 7e | 2 | Dev 1 |
| Activity logging throughout app | - | 3 | Dev 1 |
| Report Generator Wizard | 8 | 4 | Dev 2 |
| PDF Generation (reportlab) | 8 | 6 | Dev 2 |
| Settings Screen | 9 | 2 | Dev 1 |
| Quick Stats on Dashboard | 4 | 3 | Dev 1 |
| Drag-and-drop case priority | 4 | 2 | Dev 2 |
| Theme polish (consistent styling) | - | 4 | Dev 2 |
| Error handling improvements | - | 3 | Dev 1 |
| User onboarding tooltips | - | 2 | Dev 1 |
| Final testing | - | 6 | Both |
| Documentation | - | 3 | Both |
| **Total** | | **40 hrs** | |

**Per person:** ~20 hours = ~2 hrs/day ✓

---

## Feature Checklist by Iteration

### Iteration 1 Deliverables
- [x] User can sign up and log in
- [x] User can create a new case
- [x] User can drag-drop a folder to import evidence
- [x] App extracts metadata from .docx, .pdf, .jpg, .txt files
- [x] User sees evidence in a sortable table
- [x] User can label case type (Financial Fraud, Cybercrime, etc.)

### Iteration 2 Deliverables
- [ ] User can view evidence on an interactive timeline
- [ ] User can filter by status (Analyzed, Pending, Flagged)
- [ ] User can see risk level bar chart
- [ ] User can search evidence by filename
- [ ] User can change evidence status/risk level
- [ ] User can open recent cases from dashboard

### Iteration 3 Deliverables
- [ ] User can see activity log of recent actions
- [ ] User can view quick stats on dashboard
- [ ] User can generate a PDF report with one click
- [ ] User can customize report contents
- [ ] User can access settings
- [ ] App has consistent, polished UI

---

## Data Model Summary

### Users Table
```
id | username | password_hash | full_name | email | role | created_at
```

### Cases Table
```
id | user_id | name | description | case_type | status | priority | created_at | updated_at
```

### Evidence Table
```
id | case_id | file_name | file_path | extension | size | created_time | modified_time | status | risk_level | metadata_json | added_at
```

### Activity Log Table
```
id | case_id | user_id | action | details | timestamp
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PySide6 learning curve | Use simple widgets first, add complexity later |
| Metadata extraction fails | Gracefully handle errors, show partial data |
| PDF generation complex | Use templates, keep format simple |
| Time runs out | Prioritize core features, cut polish |

---

## Out of Scope (Reminder)
❌ Mobile app  
❌ Web version  
❌ Cloud sync  
❌ Password-protected file decryption  
❌ Deleted file recovery  
❌ Real-time collaboration  
❌ Social media tracking  

---

## Success Criteria

By end of Week 6, a user should be able to:
1. Open Evidentia and log in
2. Create a case called "Financial Fraud Investigation"
3. Drop a folder containing mixed files
4. See all files appear in a table with extracted metadata
5. View files on a timeline sorted by date
6. Flag suspicious files as "High Risk"
7. Mark files as "Analyzed" when reviewed
8. Click "Generate Report" and get a professional PDF
9. See a log of everything they did

---

*Document created: March 8, 2026*  
*Last updated: March 8, 2026*
