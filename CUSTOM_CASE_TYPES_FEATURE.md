# Custom Case Types Feature

## Overview
Users can now create and use custom labels for unique case types in the "Create New Case" dialog.

## Features Implemented

### 1. Custom Case Type Management
- **Add Custom Types**: Users can add new case types via the "+ Add Custom" button
- **Persistent Storage**: Custom types are stored in the database and persist across sessions
- **Duplicate Prevention**: System prevents adding duplicate case types

### 2. Enhanced Case Type Selection
- **Default Types**: Pre-defined case types (Financial Fraud, Cybercrime, etc.)
- **Custom Types**: User-defined types appear in a separate section
- **Other (Custom)**: Quick inline custom type entry option

### 3. User Interface Updates
- **"+ Add Custom" Button**: Opens dialog to add new case type permanently
- **Custom Type Input Field**: Appears when "Other (Custom)" is selected for one-time use
- **Visual Separation**: Separators distinguish default, custom, and other options

## Database Schema

### New Table: `custom_case_types`
```sql
CREATE TABLE custom_case_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Methods

### Database Methods
- `get_custom_case_types()` - Retrieve all custom case types
- `add_custom_case_type(type_name)` - Add a new custom case type
- `delete_custom_case_type(type_name)` - Remove a custom case type

## Usage Flow

1. **Adding a Permanent Custom Type**:
   - Click "+ Add Custom" button
   - Enter custom case type name
   - Type is saved and appears in dropdown for all future cases

2. **Using "Other (Custom)" for One-Time Use**:
   - Select "Other (Custom)" from dropdown
   - Enter custom type name in the input field
   - Type is used for this case only (not saved permanently)

3. **Selecting Existing Types**:
   - Choose from default types or previously saved custom types
   - Custom types appear below default types with a separator

## Files Modified

- `src/ui/new_case_dialog.py` - Enhanced dialog with custom type support
- `src/core/database.py` - Added custom case types table and methods

## Testing

Run `test_custom_case_types.py` to verify:
- Adding custom case types
- Retrieving custom case types
- Duplicate prevention
- Creating cases with custom types
