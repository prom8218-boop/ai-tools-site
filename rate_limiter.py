"""
🛡️ Advanced Rate Limiting & Security Module
Handles API rate limiting, user quotas, and security
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

class RateLimiter:
    """Advanced rate limiting and quota management"""
    
    def __init__(self, config_file='rate_limits.json'):
        self.config_file = config_file
        self.limits = self._load_config()
        self.usage = {}
    
    def _load_config(self) -> Dict:
        """Load rate limit configuration"""
        default_config = {
            'ai_chat': {'requests_per_minute': 30, 'daily_limit': 500},
            'code_execution': {'requests_per_minute': 10, 'daily_limit': 100},
            'image_generation': {'requests_per_minute': 5, 'daily_limit': 50},
            'code_analysis': {'requests_per_minute': 20, 'daily_limit': 200},
            'session_export': {'requests_per_minute': 5, 'daily_limit': 20}
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        return default_config
    
    def _get_user_key(self, user_id: str, endpoint: str) -> str:
        """Generate usage tracking key"""
        return f"{user_id}:{endpoint}"
    
    def _reset_minute_counter(self, key: str) -> None:
        """Reset minute counter"""
        if key not in self.usage:
            self.usage[key] = {
                'minute_count': 0,
                'daily_count': 0,
                'minute_start': time.time(),
                'day_start': datetime.now().date()
            }
    
    def check_rate_limit(self, user_id: str, endpoint: str) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limits
        Returns: (is_allowed, response_dict)
        """
        key = self._get_user_key(user_id, endpoint)
        
        if endpoint not in self.limits:
            return True, {'status': 'allowed', 'message': 'Endpoint not rate limited'}
        
        config = self.limits[endpoint]
        self._reset_minute_counter(key)
        
        usage = self.usage[key]
        current_time = time.time()
        current_date = datetime.now().date()
        
        # Reset minute counter if minute has passed
        if current_time - usage['minute_start'] >= 60:
            usage['minute_count'] = 0
            usage['minute_start'] = current_time
        
        # Reset daily counter if day has changed
        if current_date != usage['day_start']:
            usage['daily_count'] = 0
            usage['day_start'] = current_date
        
        # Check minute limit
        if usage['minute_count'] >= config['requests_per_minute']:
            reset_time = usage['minute_start'] + 60
            return False, {
                'status': 'rate_limited',
                'error': 'Too many requests per minute',
                'limit': config['requests_per_minute'],
                'reset_in_seconds': int(reset_time - current_time)
            }
        
        # Check daily limit
        if usage['daily_count'] >= config['daily_limit']:
            reset_time = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            return False, {
                'status': 'quota_exceeded',
                'error': 'Daily quota exceeded',
                'limit': config['daily_limit'],
                'reset_at': reset_time.isoformat()
            }
        
        # Increment counters
        usage['minute_count'] += 1
        usage['daily_count'] += 1
        
        return True, {
            'status': 'allowed',
            'remaining_minute': config['requests_per_minute'] - usage['minute_count'],
            'remaining_daily': config['daily_limit'] - usage['daily_count']
        }
    
    def get_user_quota(self, user_id: str, endpoint: str = None) -> Dict:
        """Get user's current quota status"""
        if endpoint:
            key = self._get_user_key(user_id, endpoint)
            if key not in self.usage:
                self._reset_minute_counter(key)
            
            config = self.limits.get(endpoint, {})
            usage = self.usage[key]
            
            return {
                'endpoint': endpoint,
                'minute_used': usage['minute_count'],
                'minute_limit': config.get('requests_per_minute', 'unlimited'),
                'daily_used': usage['daily_count'],
                'daily_limit': config.get('daily_limit', 'unlimited')
            }
        
        # Return all endpoints for user
        quotas = {}
        for ep in self.limits:
            quotas[ep] = self.get_user_quota(user_id, ep)
        
        return quotas
    
    def reset_user_quota(self, user_id: str, endpoint: str = None) -> Dict:
        """Reset user's quota (admin function)"""
        if endpoint:
            key = self._get_user_key(user_id, endpoint)
            if key in self.usage:
                self.usage[key]['daily_count'] = 0
            return {'status': 'success', 'message': f'Quota reset for {endpoint}'}
        
        # Reset all endpoints
        for ep in self.limits:
            key = self._get_user_key(user_id, ep)
            if key in self.usage:
                self.usage[key]['daily_count'] = 0
        
        return {'status': 'success', 'message': 'All quotas reset'}


class SecurityManager:
    """Advanced security features"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.blocked_keywords = [
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO',
            'eval(', 'exec(', '__import__',
            'system(', 'os.system', 'subprocess'
        ]
    
    def validate_input(self, user_input: str, input_type: str = 'text') -> Tuple[bool, str]:
        """
        Validate user input for security issues
        Returns: (is_valid, message)
        """
        
        # Check for injection patterns
        for keyword in self.blocked_keywords:
            if keyword.lower() in user_input.lower():
                return False, f'Potentially dangerous command detected: {keyword}'
        
        # Check input length
        max_lengths = {
            'prompt': 5000,
            'code': 50000,
            'filename': 255
        }
        
        if len(user_input) > max_lengths.get(input_type, 10000):
            return False, f'Input exceeds maximum length of {max_lengths.get(input_type)}'
        
        # Check for null bytes
        if '\x00' in user_input:
            return False, 'Null bytes not allowed in input'
        
        return True, 'Input validation passed'
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        import re
        
        # Remove path separators and special characters
        filename = re.sub(r'[/\\:\*\?"<>\|]', '', filename)
        filename = filename.replace('..', '')
        
        # Limit length
        return filename[:255]
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format"""
        import re
        
        # Simple validation - API key should be alphanumeric with hyphens
        pattern = r'^[a-zA-Z0-9\-]{32,}$'
        return bool(re.match(pattern, api_key))
    
    def check_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def add_blocked_ip(self, ip_address: str) -> Dict:
        """Add IP to blocklist"""
        self.blocked_ips.add(ip_address)
        return {'status': 'success', 'message': f'IP {ip_address} blocked'}
    
    def remove_blocked_ip(self, ip_address: str) -> Dict:
        """Remove IP from blocklist"""
        self.blocked_ips.discard(ip_address)
        return {'status': 'success', 'message': f'IP {ip_address} unblocked'}


class ErrorHandler:
    """Advanced error handling and logging"""
    
    def __init__(self, log_file='error_log.json'):
        self.log_file = log_file
        self.error_counts = {}
    
    def log_error(self, error_type: str, message: str, user_id: str = None, endpoint: str = None) -> Dict:
        """Log error with context"""
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'user_id': user_id,
            'endpoint': endpoint
        }
        
        # Load existing log
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(error_entry)
        
        # Keep only last 1000 errors
        logs = logs[-1000:]
        
        # Save log
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        # Update error counts
        key = f"{error_type}:{endpoint}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        return {'status': 'logged', 'message': 'Error logged successfully'}
    
    def get_error_stats(self, hours: int = 24) -> Dict:
        """Get error statistics"""
        
        if not os.path.exists(self.log_file):
            return {'error_count': 0, 'errors': []}
        
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            log for log in logs
            if datetime.fromisoformat(log['timestamp']) > cutoff_time
        ]
        
        # Group by error type
        error_groups = {}
        for error in recent_errors:
            error_type = error['error_type']
            error_groups[error_type] = error_groups.get(error_type, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_groups,
            'recent_errors': recent_errors[-10:]
        }
    
    def get_error_recovery_suggestion(self, error_type: str) -> str:
        """Get recovery suggestion for common errors"""
        
        suggestions = {
            'timeout': 'Request timed out. Try again with simpler code or smaller input.',
            'rate_limit': 'You have exceeded rate limit. Please wait before trying again.',
            'invalid_input': 'Invalid input provided. Check your code syntax or prompt.',
            'api_error': 'AI service error. Please try again in a moment.',
            'auth_error': 'Authentication failed. Please check your API key.',
            'memory_error': 'Out of memory. Try with smaller code or input.',
            'syntax_error': 'Syntax error in code. Review your code syntax.',
            'security_error': 'Security check failed. The input contains potentially dangerous content.'
        }
        
        return suggestions.get(error_type, 'An unexpected error occurred. Please try again.')
