# NRRC Arabic PoV - Role-Based Access Control (RBAC) System

## Overview

This system implements a comprehensive Role-Based Access Control (RBAC) system for the Arabic Legal Document Retrieval platform. The system ensures that users can only access documents based on their assigned roles, with special restrictions for documents containing "restricted" in their names.

## Features

### 🔐 Authentication System
- **JWT-based authentication** with secure token management
- **Password hashing** using bcrypt for security
- **Session management** with configurable token expiration
- **User management** with role-based permissions

### 👥 Role Hierarchy
- **Admin**: Full access to all documents including restricted ones
- **Legal**: Access to general documents and restricted documents
- **Staff**: Access to general documents only

### 📄 Document Access Control
- **File-level restrictions**: Documents with "restricted" in their names are only accessible by `legal` and `admin` roles
- **Role-based filtering**: Documents are filtered based on user's effective roles
- **Transparent access control**: Users are informed about their access level and any hidden results

### 🎨 Frontend Integration
- **Login interface** with Arabic RTL support
- **Role-based UI**: Different interfaces based on user roles
- **Access information display**: Shows user's current access level
- **Session management**: Automatic logout on token expiration

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Test Restricted Documents
```bash
python scripts/add_restricted_docs.py
```

### 3. Run the Application
```bash
uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Web Interface
1. Open `http://localhost:8000` in your browser
2. Login with one of the test accounts:
   - **Admin**: `admin` / `admin123` (Full access)
   - **Legal**: `legal` / `legal123` (Legal + Restricted access)
   - **Staff**: `staff` / `staff123` (General access only)

### CLI Testing
```bash
# Test as staff user (limited access)
python scripts/05_query_cli.py --query "الطاقة النووية" --roles staff --show-restricted

# Test as legal user (full access)
python scripts/05_query_cli.py --query "الطاقة النووية" --roles legal --show-restricted

# Test as admin user (full access)
python scripts/05_query_cli.py --query "الطاقة النووية" --roles admin --show-restricted
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `GET /me` - Get current user info
- `GET /users` - List all users (admin only)

### Search
- `POST /ask` - Search documents (requires authentication)

## Security Features

### 🔒 Access Control
- **JWT tokens** with expiration
- **Role-based permissions** at API level
- **Document-level filtering** based on file names
- **Secure password storage** with bcrypt hashing

### 🛡️ File Restrictions
Documents with "restricted" in their names are automatically restricted to:
- `legal` role users
- `admin` role users

Staff users cannot access these documents and will see a message indicating restricted results.

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key-change-in-production
```

### Role Hierarchy
The system uses a hierarchical role structure:
```python
ROLE_HIERARCHY = {
    "admin": ["admin", "legal", "staff"],
    "legal": ["legal", "staff"], 
    "staff": ["staff"]
}
```

## Testing the RBAC System

### 1. Test Document Access
1. Login as `staff` user
2. Search for "restricted" or "nuclear"
3. Notice that restricted documents are not shown
4. Check the notification showing "X restricted results"

### 2. Test Legal Access
1. Login as `legal` user
2. Search for the same terms
3. Notice that restricted documents are now visible
4. Check the access info showing "Legal + Restricted access"

### 3. Test Admin Access
1. Login as `admin` user
2. Search for the same terms
3. Notice full access to all documents
4. Check the access info showing "Full access"

## File Structure

```
app/
├── auth.py              # Authentication and RBAC logic
├── run_api.py           # Main API with RBAC integration
├── retrieval.py         # Search with role filtering
└── ...

scripts/
├── add_restricted_docs.py  # Add test restricted documents
├── 05_query_cli.py         # CLI with RBAC support
└── ...
```

## Customization

### Adding New Roles
1. Update `ROLE_HIERARCHY` in `app/auth.py`
2. Add new users to `USERS_DB` in `app/auth.py`
3. Update frontend role display logic

### Modifying Access Rules
1. Update `check_file_access()` function in `app/auth.py`
2. Modify the restriction logic as needed
3. Update frontend access information display

### Adding New Restricted Documents
1. Use the `scripts/add_restricted_docs.py` script
2. Ensure document names contain "restricted"
3. Set appropriate roles in the document metadata

## Security Considerations

- **Change default passwords** in production
- **Use strong SECRET_KEY** for JWT signing
- **Implement HTTPS** in production
- **Regular security audits** of access controls
- **Monitor access logs** for suspicious activity

## Troubleshooting

### Common Issues
1. **Login fails**: Check username/password combinations
2. **No results shown**: Verify user roles and document permissions
3. **Token expired**: Re-login to get new token
4. **Access denied**: Check if user has required roles

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```

## Support

For issues or questions about the RBAC system:
1. Check the logs for error messages
2. Verify user roles and permissions
3. Test with different user accounts
4. Review the API documentation
