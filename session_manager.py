"""
💾 Session & History Management Module
Handles chat history, session persistence, and favorites
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

class SessionManager:
    """Manage user sessions, chat history, and favorites"""
    
    def __init__(self, data_dir='user_data'):
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, 'sessions')
        self.favorites_dir = os.path.join(data_dir, 'favorites')
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create necessary directories"""
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.favorites_dir, exist_ok=True)
    
    def _get_user_id(self, identifier: str) -> str:
        """Generate user ID from identifier"""
        return hashlib.md5(identifier.encode()).hexdigest()
    
    # 💬 CHAT HISTORY MANAGEMENT
    def save_chat_message(self, user_id: str, role: str, message: str, metadata: Dict = None) -> Dict:
        """Save a chat message to history"""
        session_file = os.path.join(self.sessions_dir, f'{user_id}_chat.json')
        
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'role': role,  # 'user' or 'ai'
            'message': message,
            'metadata': metadata or {}
        }
        
        # Load existing chat or create new
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                chat_history = json.load(f)
        else:
            chat_history = []
        
        chat_history.append(chat_entry)
        
        # Save updated history
        with open(session_file, 'w') as f:
            json.dump(chat_history, f, indent=2)
        
        return {
            'status': 'success',
            'message_id': len(chat_history),
            'saved_at': chat_entry['timestamp']
        }
    
    def get_chat_history(self, user_id: str, limit: int = None) -> List[Dict]:
        """Retrieve chat history for a user"""
        session_file = os.path.join(self.sessions_dir, f'{user_id}_chat.json')
        
        if not os.path.exists(session_file):
            return []
        
        with open(session_file, 'r') as f:
            chat_history = json.load(f)
        
        return chat_history[-limit:] if limit else chat_history
    
    def clear_chat_history(self, user_id: str) -> Dict:
        """Clear chat history for a user"""
        session_file = os.path.join(self.sessions_dir, f'{user_id}_chat.json')
        
        if os.path.exists(session_file):
            os.remove(session_file)
            return {'status': 'success', 'message': 'Chat history cleared'}
        
        return {'status': 'info', 'message': 'No history to clear'}
    
    # 📥 SESSION EXPORT
    def export_session_json(self, user_id: str) -> Dict:
        """Export session as JSON"""
        chat_history = self.get_chat_history(user_id)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'message_count': len(chat_history),
            'chat_history': chat_history,
            'favorites': self.get_favorites(user_id)
        }
        
        return export_data
    
    def export_session_csv(self, user_id: str) -> str:
        """Export session as CSV"""
        import csv
        from io import StringIO
        
        chat_history = self.get_chat_history(user_id)
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Role', 'Message'])
        
        for entry in chat_history:
            writer.writerow([
                entry['timestamp'],
                entry['role'],
                entry['message'][:100]  # Truncate long messages
            ])
        
        return output.getvalue()
    
    def export_session_pdf(self, user_id: str) -> bytes:
        """Export session as PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from io import BytesIO
            
            chat_history = self.get_chat_history(user_id)
            
            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#1e3a8a',
                spaceAfter=30
            )
            elements.append(Paragraph(f"Chat Session Export - {datetime.now().strftime('%Y-%m-%d')}", title_style))
            elements.append(Spacer(1, 12))
            
            # Add chat messages
            for entry in chat_history:
                role_label = "👤 You" if entry['role'] == 'user' else "🤖 AI"
                msg_style = ParagraphStyle(
                    'Message',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor='#374151' if entry['role'] == 'user' else '#047857'
                )
                elements.append(Paragraph(f"<b>{role_label}</b> ({entry['timestamp']})", msg_style))
                elements.append(Paragraph(entry['message'], styles['Normal']))
                elements.append(Spacer(1, 12))
            
            doc.build(elements)
            return buffer.getvalue()
        except ImportError:
            return b"PDF export requires reportlab library"
    
    # ⭐ FAVORITES MANAGEMENT
    def save_favorite(self, user_id: str, prompt: str, category: str = 'general') -> Dict:
        """Save a prompt to favorites"""
        favorites_file = os.path.join(self.favorites_dir, f'{user_id}_favorites.json')
        
        favorite_entry = {
            'id': hashlib.md5(prompt.encode()).hexdigest()[:8],
            'prompt': prompt,
            'category': category,
            'saved_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        # Load existing favorites or create new
        if os.path.exists(favorites_file):
            with open(favorites_file, 'r') as f:
                favorites = json.load(f)
        else:
            favorites = []
        
        # Check if already exists
        if not any(f['id'] == favorite_entry['id'] for f in favorites):
            favorites.append(favorite_entry)
            
            with open(favorites_file, 'w') as f:
                json.dump(favorites, f, indent=2)
            
            return {
                'status': 'success',
                'message': 'Prompt saved to favorites',
                'favorite_id': favorite_entry['id']
            }
        
        return {'status': 'info', 'message': 'Prompt already in favorites'}
    
    def get_favorites(self, user_id: str, category: str = None) -> List[Dict]:
        """Get user's favorite prompts"""
        favorites_file = os.path.join(self.favorites_dir, f'{user_id}_favorites.json')
        
        if not os.path.exists(favorites_file):
            return []
        
        with open(favorites_file, 'r') as f:
            favorites = json.load(f)
        
        if category:
            return [f for f in favorites if f['category'] == category]
        
        return favorites
    
    def delete_favorite(self, user_id: str, favorite_id: str) -> Dict:
        """Delete a favorite prompt"""
        favorites_file = os.path.join(self.favorites_dir, f'{user_id}_favorites.json')
        
        if not os.path.exists(favorites_file):
            return {'status': 'error', 'message': 'No favorites found'}
        
        with open(favorites_file, 'r') as f:
            favorites = json.load(f)
        
        favorites = [f for f in favorites if f['id'] != favorite_id]
        
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f, indent=2)
        
        return {'status': 'success', 'message': 'Favorite deleted'}
    
    def increment_favorite_usage(self, user_id: str, favorite_id: str) -> Dict:
        """Increment usage count for a favorite"""
        favorites_file = os.path.join(self.favorites_dir, f'{user_id}_favorites.json')
        
        if not os.path.exists(favorites_file):
            return {'status': 'error', 'message': 'Favorite not found'}
        
        with open(favorites_file, 'r') as f:
            favorites = json.load(f)
        
        for fav in favorites:
            if fav['id'] == favorite_id:
                fav['usage_count'] += 1
                break
        
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f, indent=2)
        
        return {'status': 'success', 'message': 'Usage count updated'}
    
    # 📊 SESSION STATS
    def get_session_stats(self, user_id: str) -> Dict:
        """Get statistics about user's session"""
        chat_history = self.get_chat_history(user_id)
        favorites = self.get_favorites(user_id)
        
        user_messages = [m for m in chat_history if m['role'] == 'user']
        ai_messages = [m for m in chat_history if m['role'] == 'ai']
        
        return {
            'total_messages': len(chat_history),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'total_favorites': len(favorites),
            'first_message': chat_history[0]['timestamp'] if chat_history else None,
            'last_message': chat_history[-1]['timestamp'] if chat_history else None
        }
