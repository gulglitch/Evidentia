# API Documentation

## Database API

### Database Class

The `Database` class in `backend/app/database.py` provides methods for interacting with the SQLite database.

#### Case Management

- `create_case(name, description, case_type)` - Create a new case
- `get_all_cases()` - Retrieve all cases
- `get_case_by_id(case_id)` - Get specific case details
- `update_case(case_id, **kwargs)` - Update case information
- `delete_case(case_id)` - Delete a case

#### Evidence Management

- `add_evidence(case_id, file_path, metadata)` - Add evidence to a case
- `get_evidence_by_case(case_id)` - Get all evidence for a case
- `update_evidence(evidence_id, **kwargs)` - Update evidence details
- `delete_evidence(evidence_id)` - Remove evidence

#### User Management

- `create_user(username, password, full_name, role)` - Create new user
- `authenticate_user(username, password)` - Verify user credentials
- `get_user_by_username(username)` - Retrieve user details

### File Scanner

The `FileScanner` class in `backend/app/file_scanner.py` handles file system operations.

- `scan_directory(path)` - Scan directory for evidence files
- `get_file_info(file_path)` - Extract basic file information
- `calculate_hash(file_path)` - Generate file hash for integrity

### Metadata Extractor

The `MetadataExtractor` class in `backend/app/metadata_extractor.py` extracts metadata from various file types.

- `extract_metadata(file_path)` - Extract metadata from supported file types
- `extract_image_metadata(file_path)` - Extract EXIF data from images
- `extract_document_metadata(file_path)` - Extract metadata from documents
- `extract_pdf_metadata(file_path)` - Extract metadata from PDF files

## Frontend Components

### Main Window
Entry point for the application UI (`frontend/src/main_window.py`)

### Case Management
Interface for creating and managing cases (`frontend/src/case_management.py`)

### Evidence Management
Interface for uploading and managing evidence (`frontend/src/evidence_management.py`)

### Timeline Widget
Visual timeline representation of evidence (`frontend/src/timeline_widget.py`)

## Data Models

### Case
- id: Integer (Primary Key)
- case_number: Text (Unique)
- case_name: Text
- case_type: Text
- description: Text
- investigator: Text
- created_date: Text (ISO format)
- status: Text (Active/Closed/Archived)
- total_evidence_count: Integer
- analyzed_count: Integer
- pending_count: Integer
- flagged_count: Integer

### Evidence
- id: Integer (Primary Key)
- case_id: Integer (Foreign Key)
- file_path: Text
- file_name: Text
- file_type: Text
- file_size: Integer
- hash_value: Text
- created_date: Text
- modified_date: Text
- accessed_date: Text
- metadata: Text (JSON)
- notes: Text
- analysis_status: Text (Pending/Analyzed/Flagged)
- risk_level: Text (Low/Medium/High)
- analyzed_by: Text
- analyzed_date: Text

### User
- id: Integer (Primary Key)
- username: Text (Unique)
- password_hash: Text
- full_name: Text
- role: Text (Admin/Investigator/Analyst)
- created_date: Text

### Case Milestone
- id: Integer (Primary Key)
- case_id: Integer (Foreign Key)
- milestone_name: Text
- milestone_date: Text
- milestone_status: Text (Pending/In Progress/Completed)
- description: Text
- created_by: Text

### Activity Log
- id: Integer (Primary Key)
- case_id: Integer (Foreign Key)
- user_id: Integer (Foreign Key)
- action_type: Text (CREATE/UPDATE/DELETE/UPLOAD)
- action_description: Text
- timestamp: Text
- entity_type: Text (case/evidence/milestone)
- entity_id: Integer
