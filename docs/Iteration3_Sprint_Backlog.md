# Iteration 3 Sprint Backlog
## Reporting & History Module (Weeks 5-6)

---

## STORY ID: US-08
**Story Title: Recent Activity Feed**

**Priority: High**  
**Estimated Hours: 8**

### User Story:
As a user, I want to see a list of my last actions so I remember what I did.

### Description:
This story adds a live activity feed that shows recent actions taken in the investigation. Users can see what they did recently, like uploading files or adding milestones, so they don't forget their progress.

### Sub User Stories:
- As a user, I want to see when I uploaded evidence files so I know what work I completed today.
- As a user, I want to see when I created a new case so I can track my case history.
- As a user, I want to see when I added milestones so I remember important dates I marked.
- As a user, I want to see timestamps like "5 minutes ago" so I can quickly understand how recent an action was.

### Acceptance Criteria:
- Activity feed displays the last 20 actions taken by the user.
- Each activity shows the action type, details, case name, and timestamp.
- Timestamps show relative time (e.g., "2 hours ago", "Yesterday").
- Activity feed automatically refreshes every 30 seconds.
- Activities are color-coded by type (uploads are green, deletions are red, etc.).

---

## STORY ID: US-09
**Story Title: Quick Stats Dashboard**

**Priority: High**  
**Estimated Hours: 10**

### User Story:
As a user, I want to see a total count of my files and team members on one screen.

### Description:
This story creates a dashboard that shows important numbers at a glance. Users can see how many cases they have, how many evidence files are collected, and how many are analyzed without clicking through multiple screens.

### Sub User Stories:
- As a user, I want to see my total number of cases so I know how much work I have.
- As a user, I want to see how many evidence files I collected so I can track my progress.
- As a user, I want to see how many files are still pending review so I know what work is left.
- As a user, I want to see how many high-risk files I have so I can prioritize dangerous evidence.
- As a user, I want the dashboard to refresh automatically so the numbers stay up to date.

### Acceptance Criteria:
- Dashboard shows 6 stat cards: Total Cases, Active Cases, Total Evidence, Analyzed, Pending, and High Risk.
- Each stat card displays a large number with a descriptive label.
- Stats are color-coded (green for active, red for high risk, blue for evidence, etc.).
- Dashboard has a manual refresh button.
- Dashboard automatically refreshes every 30 seconds.
- Back button returns user to the cases list.

---

## STORY ID: US-10
**Story Title: Automated Final Report**

**Priority: High**  
**Estimated Hours: 12**

### User Story:
As a user, I want to click a button to save my findings as a professional PDF.

### Description:
This story adds a report generation feature that creates a PDF document with all the case information, evidence details, timeline, and charts. Users can export their investigation results in a professional format for submission or sharing.

### Sub User Stories:
- As a user, I want to click a "Generate Report" button so I can create a PDF without manual work.
- As a user, I want the report to include case details like case name and type so the report is complete.
- As a user, I want the report to include a list of all evidence files so I have a record of what was collected.
- As a user, I want the report to include risk level charts so I can show which files are dangerous.

### Acceptance Criteria:
- Report generation button is visible on the case home screen.
- Clicking the button creates a PDF file with case information.
- PDF includes case name, type, description, and investigator name.
- PDF includes a table of all evidence files with names, dates, and status.
- PDF includes risk level distribution chart.
- PDF includes timeline of case milestones.
- User can choose where to save the PDF file.
- Success message appears after PDF is generated.

---

## Sprint Summary

**Total User Stories:** 3  
**Total Estimated Hours:** 30 hours  
**Sprint Duration:** 2 weeks (Weeks 5-6)

### Team Assignment:
- **Gul-e-Zara:** Backend report generation logic, PDF creation, activity logging system
- **Rumesha Naveed:** Dashboard UI, activity feed UI, report layout design

### Definition of Done:
- All acceptance criteria met for each user story
- Code is tested and bug-free
- Features work together without breaking existing functionality
- Documentation is updated
- Demo-ready for presentation

---

## Notes:
- Feature 8 and 9 are already implemented and tested
- Feature 10 (PDF Report) is the main focus for remaining sprint time
- All features must integrate smoothly with existing case management workflow
