"""
🎓 AI Learning Hub Module
Provides tutorials, code snippets, and API documentation
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class LearningHub:
    """Provide educational content and code snippets"""
    
    # Tutorial Content Database
    TUTORIALS = {
        'python_basics': {
            'title': 'Python Basics',
            'description': 'Learn Python fundamentals from scratch',
            'difficulty': 'beginner',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Variables and Data Types',
                    'content': 'Learn about different data types in Python',
                    'code': '''# Variables
name = "Alice"
age = 25
height = 5.6
is_student = True

# Data Types
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>'''
                },
                {
                    'id': 2,
                    'title': 'Functions',
                    'content': 'Create and use functions in Python',
                    'code': '''def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))'''
                }
            ]
        },
        'web_basics': {
            'title': 'Web Development Basics',
            'description': 'Learn HTML, CSS, and JavaScript',
            'difficulty': 'beginner',
            'lessons': [
                {
                    'id': 1,
                    'title': 'HTML Structure',
                    'content': 'Basic HTML document structure',
                    'code': '''<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>'''
                }
            ]
        }
    }
    
    # Code Snippets Library
    CODE_SNIPPETS = {
        'python': [
            {
                'id': 'read_file',
                'title': 'Read File',
                'description': 'Read content from a file',
                'tags': ['file', 'io'],
                'code': '''with open('file.txt', 'r') as f:
    content = f.read()
    print(content)'''
            },
            {
                'id': 'list_comprehension',
                'title': 'List Comprehension',
                'description': 'Create lists using comprehension',
                'tags': ['lists', 'python'],
                'code': '''squares = [x**2 for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]'''
            },
            {
                'id': 'api_request',
                'title': 'API Request',
                'description': 'Make HTTP requests',
                'tags': ['api', 'requests'],
                'code': '''import requests
response = requests.get('https://api.example.com/data')
data = response.json()
print(data)'''
            }
        ],
        'javascript': [
            {
                'id': 'fetch_api',
                'title': 'Fetch API',
                'description': 'Make HTTP requests in JavaScript',
                'tags': ['fetch', 'api'],
                'code': '''fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));'''
            },
            {
                'id': 'async_await',
                'title': 'Async/Await',
                'description': 'Handle asynchronous operations',
                'tags': ['async', 'promises'],
                'code': '''async function getData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('Error:', error);
    }
}'''
            }
        ]
    }
    
    # API Documentation
    API_DOCS = {
        '/api/ai': {
            'method': 'POST',
            'description': 'Chat with AI Assistant',
            'rate_limit': '30 requests/minute',
            'parameters': {
                'prompt': {'type': 'string', 'required': True, 'description': 'Your question or prompt'}
            },
            'response': {
                'result': {'type': 'string', 'description': 'AI response'}
            },
            'example': {
                'request': {'prompt': 'What is Python?'},
                'response': {'result': 'Python is a high-level programming language...'}
            }
        },
        '/api/analyze-code': {
            'method': 'POST',
            'description': 'Analyze code for bugs and performance',
            'rate_limit': '20 requests/minute',
            'parameters': {
                'code': {'type': 'string', 'required': True, 'description': 'Code to analyze'},
                'language': {'type': 'string', 'required': True, 'description': 'Programming language'}
            },
            'response': {
                'overall_score': {'type': 'integer', 'description': 'Code quality score (0-100)'},
                'bugs': {'type': 'object', 'description': 'Bug detection results'}
            }
        },
        '/api/execute': {
            'method': 'POST',
            'description': 'Execute code and get output',
            'rate_limit': '10 requests/minute',
            'parameters': {
                'code': {'type': 'string', 'required': True},
                'language': {'type': 'string', 'required': True, 'values': ['python', 'java', 'cpp', 'c']}
            },
            'response': {
                'output': {'type': 'string', 'description': 'Code execution output'}
            }
        }
    }
    
    def get_tutorials(self, category: str = None) -> Dict:
        """Get available tutorials"""
        if category and category in self.TUTORIALS:
            return {
                'status': 'success',
                'category': category,
                'tutorial': self.TUTORIALS[category]
            }
        
        return {
            'status': 'success',
            'total_tutorials': len(self.TUTORIALS),
            'categories': list(self.TUTORIALS.keys()),
            'tutorials': self.TUTORIALS
        }
    
    def get_tutorial_lesson(self, category: str, lesson_id: int) -> Dict:
        """Get specific tutorial lesson"""
        if category not in self.TUTORIALS:
            return {'status': 'error', 'message': 'Category not found'}
        
        lessons = self.TUTORIALS[category]['lessons']
        lesson = next((l for l in lessons if l['id'] == lesson_id), None)
        
        if not lesson:
            return {'status': 'error', 'message': 'Lesson not found'}
        
        return {
            'status': 'success',
            'category': category,
            'lesson': lesson
        }
    
    def get_code_snippets(self, language: str = None) -> Dict:
        """Get code snippets for a language"""
        if language and language in self.CODE_SNIPPETS:
            return {
                'status': 'success',
                'language': language,
                'count': len(self.CODE_SNIPPETS[language]),
                'snippets': self.CODE_SNIPPETS[language]
            }
        
        return {
            'status': 'success',
            'languages': list(self.CODE_SNIPPETS.keys()),
            'total_snippets': sum(len(s) for s in self.CODE_SNIPPETS.values()),
            'snippets': self.CODE_SNIPPETS
        }
    
    def get_snippet(self, language: str, snippet_id: str) -> Dict:
        """Get specific code snippet"""
        if language not in self.CODE_SNIPPETS:
            return {'status': 'error', 'message': 'Language not found'}
        
        snippet = next(
            (s for s in self.CODE_SNIPPETS[language] if s['id'] == snippet_id),
            None
        )
        
        if not snippet:
            return {'status': 'error', 'message': 'Snippet not found'}
        
        return {'status': 'success', 'snippet': snippet}
    
    def get_api_docs(self, endpoint: str = None) -> Dict:
        """Get API documentation"""
        if endpoint and endpoint in self.API_DOCS:
            return {
                'status': 'success',
                'endpoint': endpoint,
                'documentation': self.API_DOCS[endpoint]
            }
        
        return {
            'status': 'success',
            'total_endpoints': len(self.API_DOCS),
            'endpoints': list(self.API_DOCS.keys()),
            'documentation': self.API_DOCS
        }
    
    def search_snippets(self, query: str) -> Dict:
        """Search code snippets by title or tag"""
        results = []
        
        for language, snippets in self.CODE_SNIPPETS.items():
            for snippet in snippets:
                search_fields = [
                    snippet['title'],
                    snippet['description'],
                    ' '.join(snippet.get('tags', []))
                ]
                
                if any(query.lower() in field.lower() for field in search_fields):
                    results.append({
                        'language': language,
                        **snippet
                    })
        
        return {
            'status': 'success',
            'query': query,
            'results_count': len(results),
            'results': results
        }
    
    def get_learning_path(self, level: str = 'beginner') -> Dict:
        """Get recommended learning path"""
        paths = {
            'beginner': {
                'title': 'Beginner Learning Path',
                'description': 'Start your programming journey',
                'tutorials': ['python_basics', 'web_basics'],
                'duration': '2-3 weeks',
                'topics': ['Variables', 'Functions', 'Loops', 'HTML Basics']
            },
            'intermediate': {
                'title': 'Intermediate Learning Path',
                'description': 'Build on your programming skills',
                'tutorials': [],
                'duration': '4-6 weeks',
                'topics': ['OOP', 'Database', 'APIs', 'Frameworks']
            }
        }
        
        return paths.get(level, paths['beginner'])
