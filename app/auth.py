"""
Authentication and Role-Based Access Control (RBAC) system
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()

# User data model
class User(BaseModel):
    username: str
    email: str
    full_name: str
    roles: List[str]
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    roles: List[str]

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# In-memory user storage (in production, use a database)
USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "email": "admin@nrrc.gov.sa",
        "full_name": "System Administrator",
        "hashed_password": pwd_context.hash("admin123"),
        "roles": ["admin", "legal", "staff"],
        "is_active": True
    },
    "legal": {
        "username": "legal",
        "email": "legal@nrrc.gov.sa", 
        "full_name": "Legal Advisor",
        "hashed_password": pwd_context.hash("legal123"),
        "roles": ["legal", "staff"],
        "is_active": True
    },
    "staff": {
        "username": "staff",
        "email": "staff@nrrc.gov.sa",
        "full_name": "General Staff",
        "hashed_password": pwd_context.hash("staff123"),
        "roles": ["staff"],
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    return USERS_DB.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        roles=user["roles"],
        is_active=user["is_active"]
    )

def require_roles(required_roles: List[str]):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Check if user has any of the required roles
        user_roles = set(current_user.roles)
        required_roles_set = set(required_roles)
        
        if not user_roles.intersection(required_roles_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        
        return current_user
    
    return role_checker

def check_file_access(user_roles: List[str], doc_id: str) -> bool:
    """
    Check if user has access to a document based on file restrictions.
    Files with 'restricted' in their name can only be accessed by 'legal' and 'admin' roles.
    """
    # Check if document name contains 'restricted'
    if 'restricted' in doc_id.lower():
        # Only legal and admin roles can access restricted files
        allowed_roles = {'legal', 'admin'}
        user_roles_set = set(user_roles)
        return bool(user_roles_set.intersection(allowed_roles))
    
    # All other files are accessible by all roles
    return True

def filter_documents_by_access(user_roles: List[str], documents: List[Dict]) -> List[Dict]:
    """
    Filter documents based on user's role and file restrictions
    """
    filtered_docs = []
    for doc in documents:
        doc_id = doc.get('doc_id', '')
        if check_file_access(user_roles, doc_id):
            filtered_docs.append(doc)
    return filtered_docs

# Role hierarchy for easier management
ROLE_HIERARCHY = {
    "admin": ["admin", "legal", "staff"],
    "legal": ["legal", "staff"], 
    "staff": ["staff"]
}

def get_effective_roles(user_roles: List[str]) -> List[str]:
    """
    Get all effective roles for a user based on role hierarchy
    """
    effective_roles = set()
    for role in user_roles:
        if role in ROLE_HIERARCHY:
            effective_roles.update(ROLE_HIERARCHY[role])
    return list(effective_roles)
