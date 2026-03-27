# Non-Functional Requirements (NFRs) Specification
## Evidentia - Digital Evidence Timeline System

---

## Project Description

The project is to develop Evidentia, a desktop-based digital evidence management system that enables forensic investigators and legal professionals to organize and analyze digital files without manual data entry. Users will upload folders containing evidence files, and the system will automatically extract metadata, display comprehensive file information in sortable tables, and organize cases by investigation type. The goal is to provide an efficient, reliable, and user-friendly environment suitable for students, junior investigators, and cybersecurity analysts working with digital evidence.

---

## Non-Functional Requirements (NFRs)

### 1. Performance

The system should maintain responsive file processing and smooth UI interactions during evidence analysis operations. It must process and extract metadata from at least 100 files within 30 seconds on standard hardware (Intel i5 or equivalent, 8GB RAM). The application should remain responsive during file scanning operations, with UI interactions responding within 200 milliseconds even while background processing is active. The metadata table must render and display up to 500 evidence entries without noticeable lag, with sorting and filtering operations completing within 500 milliseconds. Database queries for case retrieval and evidence listing should execute in under 100 milliseconds for typical datasets.

### 2. Usability

The application should be intuitive and accessible for users with minimal technical background in digital forensics. A new user must be able to create a case, upload a folder of evidence, and view the metadata table within 5 minutes without external documentation. The drag-and-drop interface should provide clear visual feedback with border color changes and hover states. All forms must include inline validation with descriptive error messages that explain what went wrong and how to fix it. Navigation between screens should be logical and consistent, with clearly labeled back buttons and breadcrumb indicators showing the current case context. The interface should use recognizable icons and consistent color coding to help users quickly identify file types and case categories.

### 3. Scalability

The system should efficiently handle growing evidence collections as investigations expand over time. It must support individual cases containing at least 500 evidence files without performance degradation. The database should accommodate at least 50 active cases simultaneously with quick retrieval times. The application should handle evidence folders with nested directory structures up to 10 levels deep without errors or excessive processing time. The metadata extraction pipeline should scale linearly, maintaining consistent per-file processing time regardless of total file count. The architecture should allow future expansion to support additional file types and metadata extraction capabilities without requiring major refactoring.

### 4. Reliability

The application should operate consistently without data loss or unexpected failures during normal investigative workflows. The system should not crash more than once in 8 hours of continuous use under typical conditions. All evidence uploads must be protected by database transactions to ensure data integrity, with automatic rollback on failure. The application must gracefully handle corrupted files, password-protected documents, and inaccessible files by logging errors and continuing with remaining files rather than terminating the entire upload. File hash calculations must be accurate and consistent, producing identical MD5 hashes for the same file across multiple uploads. The database must maintain referential integrity with proper foreign key constraints, preventing orphaned evidence records if a case is deleted.

### 5. Responsiveness

All user interactions within the application should feel immediate and provide clear feedback. UI elements such as buttons, dropdowns, and navigation controls should respond within 100 milliseconds of user action. The drag-and-drop zone should provide instant visual feedback when a folder is dragged over it, with border color changes occurring within 50 milliseconds. Form validation should occur in real-time as users type, with error messages appearing immediately when validation fails. The metadata table search and filter operations should update the displayed results within 300 milliseconds of user input. Progress indicators during file analysis should update at least once per second to show continuous activity and prevent the perception of a frozen application.

### 6. Compatibility

The application should function consistently across multiple operating systems without requiring platform-specific modifications. It must fully support Windows 10+ and Windows 11 with identical features and user experience. The application should handle file paths correctly on both Windows (backslash separators) and Unix-based systems (forward slash separators). All file metadata extraction should work consistently regardless of the operating system where files were created. The SQLite database format must be portable across platforms, allowing users to transfer their database file between systems without corruption. The PySide6 GUI framework should render consistently across supported platforms with no visual discrepancies in layout, fonts, or colors.

### 7. Maintainability

The codebase should be organized, documented, and structured to facilitate future development and bug fixes. Code must follow a clear modular architecture with separation between backend logic (database, file scanning, metadata extraction), frontend UI (screens, widgets, dialogs), and data storage (database schema). Each Python module should have clear docstrings explaining its purpose, and complex functions should include inline comments. The project structure must match the submission requirements with distinct backend/, frontend/, and database/ directories. Database schema changes should be manageable through SQL migration scripts. The code should follow PEP 8 style guidelines for Python to ensure readability and consistency across team members.

### 8. Security

The application should protect the integrity and confidentiality of sensitive investigation data. All file hash calculations must use cryptographically secure MD5 algorithms to ensure evidence integrity verification. The database file should be stored locally with appropriate file system permissions to prevent unauthorized access. User authentication credentials (when implemented) must never be stored in plain text, requiring secure hashing algorithms. The application should validate all user inputs to prevent SQL injection attacks, using parameterized queries exclusively. File path inputs must be sanitized to prevent directory traversal attacks. The system should not expose sensitive file paths or system information in error messages displayed to users.

### 9. Data Integrity

The system must ensure that evidence data remains accurate, consistent, and unmodified throughout the investigation lifecycle. All evidence file uploads must be wrapped in database transactions, ensuring that either all files in a batch are saved successfully or none are saved if an error occurs. The MD5 hash stored for each file must match the actual file hash, providing tamper detection capability. Foreign key constraints must be enforced to prevent orphaned evidence records when cases are deleted (CASCADE DELETE). The metadata extraction process must preserve original file timestamps without modification. The database must use appropriate data types (INTEGER for IDs, TEXT for strings, REAL for sizes) to prevent data corruption. Backup and recovery mechanisms should allow restoration of the database to a consistent state in case of corruption.

### 10. Testability

The application architecture should facilitate comprehensive testing at unit, integration, and system levels. Each backend module (Database, FileScanner, MetadataExtractor) should be independently testable with clear input/output contracts. The frontend screens should be testable in isolation using mock data and signals. The test_evidence/ folder should contain representative samples of all supported file types for consistent testing. Test cases should cover normal workflows (happy path), edge cases (empty folders, single file), and error conditions (corrupted files, missing permissions). The application should include sample data (seed.sql) that can be loaded for demonstration and testing purposes. Manual testing procedures should be documented with expected outcomes for each user story's acceptance criteria.

---

## NFR Verification Methods

| NFR Category | Verification Method | Success Criteria |
|--------------|---------------------|------------------|
| Performance | Manual testing with 100-file folder | Processing completes in < 30 seconds |
| Performance | UI responsiveness testing | All interactions respond in < 200ms |
| Usability | New user testing | Complete first workflow in < 5 minutes |
| Scalability | Load testing with 500 files | No performance degradation |
| Reliability | Continuous operation testing | < 1 crash per 8 hours |
| Responsiveness | Interaction timing measurement | UI updates within 100ms |
| Compatibility | Cross-platform testing | Identical functionality on Windows 10+ |
| Maintainability | Code review | Clear structure, documented modules |
| Security | Security audit | No plain text credentials, parameterized queries |
| Data Integrity | Database consistency checks | All transactions atomic, hashes accurate |
| Testability | Test coverage analysis | All modules independently testable |

---

## Priority Classification

**Critical (Must Have for Sprint 1):**
- Performance: File processing and UI responsiveness
- Reliability: No data loss during uploads
- Data Integrity: Accurate metadata extraction and storage
- Compatibility: Windows 10+ support

**Important (Should Have for Sprint 1):**
- Usability: Intuitive interface for new users
- Responsiveness: Immediate feedback on user actions
- Security: Input validation and secure queries

**Desirable (Nice to Have for Future Sprints):**
- Scalability: Support for 500+ files (current target: 100-200)
- Maintainability: Comprehensive inline documentation
- Testability: Automated test suite

---

## Constraints and Assumptions

**Constraints:**
- Desktop-only application (no mobile or web version)
- Local file system access only (no cloud storage integration)
- SQLite database (single-user, file-based)
- Sprint 1 scope limited to evidence upload and metadata display
- No advanced forensic features (file recovery, password cracking)

**Assumptions:**
- Users have basic computer literacy (can navigate file systems)
- Evidence files are accessible and not encrypted
- Standard hardware available (Intel i5 equivalent, 8GB RAM)
- Windows 10 or higher operating system
- Users have read permissions for evidence folders
- Internet connection not required for core functionality

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | March 19, 2026 | Team | Initial NFR specification for Sprint 1 |

