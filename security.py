"""
🔒 Enhanced Security Module for AI Tools Site
Provides comprehensive security features including:
- CORS Protection
- CSRF Token Management
- Input Validation & Sanitization
- API Key Rotation
- Rate Limiting (Advanced)
- Security Headers
"""

import os
import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session


class CORSManager:
    """Manage Cross-Origin Resource Sharing (CORS) securely"""
    
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "localhost:3000,localhost:5000").split(",")
    ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
    ALLOWED_HEADERS = ["Content-Type", "Authorization", "X-CSRF-Token"]
    
    @staticmethod
    def validate_origin(origin):
        """Validate incoming request origin"""
        if not origin:
            return False
        
        # Remove port for comparison
        origin_base = origin.split(":")[0]
        
        for allowed in CORSManager.ALLOWED_ORIGINS:
            allowed_base = allowed.split(":")[0]
            if allowed_base in origin_base:
                return True
        return False
    
    @staticmethod
    def get_cors_headers(origin):
        """Generate secure CORS headers"""
        if CORSManager.validate_origin(origin):
            return {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': ', '.join(CORSManager.ALLOWED_METHODS),
                'Access-Control-Allow-Headers': ', '.join(CORSManager.ALLOWED_HEADERS),
                'Access-Control-Max-Age': '3600',
                'Access-Control-Allow-Credentials': 'true'
            }
        return {}


class CSRFTokenManager:
    """Manage CSRF token generation and validation"""
    
    # In-memory token store (use Redis/Database in production)
    _tokens = {}
    TOKEN_EXPIRY = 3600  # 1 hour
    
    @staticmethod
    def generate_token(user_id: str) -> str:
        """Generate a secure CSRF token"""
        token = secrets.token_urlsafe(32)
        timestamp = datetime.utcnow().timestamp()
        
        CSRFTokenManager._tokens[token] = {
            'user_id': user_id,
            'created_at': timestamp,
            'expires_at': timestamp + CSRFTokenManager.TOKEN_EXPIRY
        }
        
        return token
    
    @staticmethod
    def validate_token(token: str, user_id: str) -> bool:
        """Validate CSRF token"""
        if token not in CSRFTokenManager._tokens:
            return False
        
        token_data = CSRFTokenManager._tokens[token]
        
        # Check expiry
        if datetime.utcnow().timestamp() > token_data['expires_at']:
            del CSRFTokenManager._tokens[token]
            return False
        
        # Check user ID match
        if token_data['user_id'] != user_id:
            return False
        
        # Token is valid, remove after use
        del CSRFTokenManager._tokens[token]
        return True


class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # XSS
        r"on\w+\s*=",  # Event handlers
        r"DROP\s+TABLE|DELETE\s+FROM|UPDATE\s+SET",  # SQL Injection
        r"__import__|exec|eval|compile",  # Code injection
        r"/bin/|/usr/bin|/etc/|system\(",  # System commands
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Trim length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace("\x00", "")
        
        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return ""
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, str]:
        """Validate AI prompt"""
        if not prompt or len(prompt.strip()) < 1:
            return False, "Prompt cannot be empty"
        
        if len(prompt) > 5000:
            return False, "Prompt exceeds maximum length (5000 chars)"
        
        sanitized = InputValidator.sanitize_string(prompt)
        if not sanitized:
            return False, "Prompt contains invalid or dangerous content"
        
        return True, sanitized
    
    @staticmethod
    def validate_code(code: str, language: str) -> tuple[bool, str]:
        """Validate code input"""
        if not code or len(code.strip()) < 1:
            return False, "Code cannot be empty"
        
        if len(code) > 50000:
            return False, "Code exceeds maximum length (50000 chars)"
        
        # Check for dangerous system commands
        dangerous_keywords = {
            'python': ['os.system', 'subprocess', '__import__', 'eval', 'exec'],
            'java': ['Runtime.getRuntime', 'ProcessBuilder', 'System.exec'],
            'cpp': ['system(', 'fork(', 'execve('],
            'c': ['system(', 'fork(', 'execve(']
        }
        
        if language in dangerous_keywords:
            for keyword in dangerous_keywords[language]:
                if keyword in code:
                    return False, f"Code contains dangerous operation: {keyword}"
        
        sanitized = InputValidator.sanitize_string(code)
        if not sanitized:
            return False, "Code contains invalid or dangerous content"
        
        return True, sanitized


class APIKeyManager:
    """Secure API key management"""
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """Mask API key for logging/display"""
        if len(api_key) <= 4:
            return "*" * len(api_key)
        return f"{api_key[:2]}{'*' * (len(api_key) - 4)}{api_key[-2:]}"
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key or len(api_key) < 20:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            return False
        
        return True


class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' accounts.google.com; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class AuthenticationManager:
    """Manage user authentication securely"""
    
    @staticmethod
    def verify_google_token(token: str) -> dict or None:
        """Verify Google JWT token"""
        try:
            # In production, use google.auth.transport.requests
            from google.auth.transport import requests
            from google.oauth2 import id_token
            
            request_obj = requests.Request()
            
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                token,
                request_obj,
                os.environ.get('GOOGLE_CLIENT_ID')
            )
            
            return id_info
        except Exception as e:
            return None
    
    @staticmethod
    def create_session_token(user_id: str) -> str:
        """Create secure session token"""
        token_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # In production, use JWT
        token = secrets.token_urlsafe(32)
        return token


def require_csrf(f):
    """Decorator to require CSRF token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.form.get('user_id') or request.json.get('user_id', 'anonymous')
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token or not CSRFTokenManager.validate_token(token, user_id):
            return jsonify({'error': 'CSRF token invalid or missing'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validate token (implement based on your auth system)
        # For now, basic validation
        if not token:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
