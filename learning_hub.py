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
    
    # Tutorial Content
    TUTORIALS = {
        'python_basics': {
            'title': 'Python Basics',
            'description': 'Learn Python fundamentals',
            'lessons': [
                {
                    'id': 1,
                    'title': 'Variables and Data Types',
                    'code': '''# Variables
name = "Alice"
age = 25
height = 5.6
is_student = True

# Data Types
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>
print(type(height))    # <class 'float'>
print(type(is_student)) # <class 'bool'>'''
                },
                {
                    'id': 2,
                    'title': 'Functions',
                    'code': '''# Function Definition
def greet(name):
    return f"Hello, {name}!"

# Function Call
print(greet("Alice"))  # Output: Hello, Alice!

# Function with Default Parameter
def welcome(name="Guest"):
    return f"Welcome, {name}!"

print(welcome())       # Output: Welcome, Guest!
print(welcome("Bob"))  # Output: Welcome, Bob!'''
                },
                {
                    'id': 3,
                    'title': 'Loops',
                    'code': '''# For Loop
for i in range(5):
    print(f"Count: {i}")

# While Loop
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1

# List Iteration
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)'''
                }
            ]
        },
        'web_development': {
            'title': 'Web Development Basics',
            'description': 'Learn HTML, CSS, and JavaScript',
            'lessons': [
                {
                    'id': 1,
                    'title': 'HTML Basics',
                    'code': '''<!DOCTYPE html>
<html>
<head>
    <title>My First Page</title>
</head>
<body>
    <h1>Welcome to Web Development</h1>
    <p>This is a paragraph.</p>
    <a href="https://example.com">Click here</a>
</body>
</html>'''
                },
                {
                    'id': 2,
                    'title': 'CSS Styling',
                    'code': '''/* Selector */
body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
}

/* Class */
.header {
    color: #333;
    font-size: 24px;
}

/* ID */
#main {
    max-width: 1200px;
    margin: 0 auto;
}'''
                },
                {
                    'id': 3,
                    'title': 'JavaScript Events',
                    'code': '''// Click Event
document.getElementById("btn").addEventListener("click", function() {
    alert("Button clicked!");
});

// Input Event
document.getElementById("input").addEventListener("input", function(e) {
    console.log(e.target.value);
});

// Form Submission
document.getElementById("form").addEventListener("submit", function(e) {
    e.preventDefault();
    console.log("Form submitted");
});'''
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
                'code': '''with open('file.txt', 'r') as f:
    content = f.read()
    print(content)'''
            },
            {
                'id': 'list_comprehension',
                'title': 'List Comprehension',
                'description': 'Create lists using comprehension',
                'code': '''# Simple comprehension
squares = [x**2 for x in range(10)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# Nested comprehension
matrix = [[j for j in range(3)] for i in range(3)]'''
            },
            {
                'id': 'api_request',
                'title': 'API Request',
                'description': 'Make HTTP requests using requests library',
                'code': '''import requests

# GET request
response = requests.get('https://api.example.com/data')
data = response.json()

# POST request
payload = {'key': 'value'}
response = requests.post('https://api.example.com/submit', json=payload)'''
            }
        ],
        'javascript': [
            {
                'id': 'fetch_api',
                'title': 'Fetch API',
                'description': 'Make HTTP requests in JavaScript',
                'code': '''// GET request
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));

// POST request
fetch('/api/submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({key: 'value'})
})'''
            },
            {
                'id': 'async_await',
                'title': 'Async/Await',
                'description': 'Handle asynchronous operations',
                'code': '''async function getData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error('Error:', error);
    }
}

getData();'''
            }
        ]
    }
    
    # API Documentation
    API_DOCS = {
        '/api/ai': {
            'method': 'POST',
            'description': 'Chat with AI Assistant',
            'parameters': {
                'prompt': 'str - Your question or prompt'
            },
            'response': {
                'result': 'str - AI response'
            },
            'example': {
                'request': {'prompt': 'What is Python?'},
                'response': {'result': 'Python is a high-level programming language...'}
            }
        },
        '/api/analyze-code': {
            'method': 'POST',
            'description': 'Analyze code for bugs and performance',
            'parameters': {
                'code': 'str - Code to analyze',
                'language': 'str - Programming language'
            },
            'response': {
                'overall_score': 'int - Code quality score (0-100)',
                'bugs': 'dict - Bug detection results',
                'performance': 'dict - Performance metrics'
            },
            'example': {
                'request': {
                    'code': 'def hello(): print("Hello")',
                    'language': 'python'
                },
                'response': {
                    'overall_score': 85,
                    'bugs': {'total_bugs': 0},
                    'performance': {'performance_score': 85}
                }
            }
        },
        '/api/execute': {
            'method': 'POST',
            'description': 'Execute code and get output',
            'parameters': {
                'code': 'str - Code to execute',
                'language': 'str - python|java|cpp|c'
            },
            'response': {
                'output': 'str - Code execution output'
            },
            'example': {
                'request': {
                    'code': 'print("Hello World")',
                    'language': 'python'
                },
                'response': {
                    'output': 'Hello World'
                }
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
                'snippets': self.CODE_SNIPPETS[language]
            }
        
        return {
            'status': 'success',
            'languages': list(self.CODE_SNIPPETS.keys()),
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
            'endpoints': list(self.API_DOCS.keys()),
            'documentation': self.API_DOCS
        }
    
    def search_snippets(self, query: str) -> Dict:
        """Search code snippets"""
        results = []
        
        for language, snippets in self.CODE_SNIPPETS.items():
            for snippet in snippets:
                if (query.lower() in snippet['title'].lower() or
                    query.lower() in snippet['description'].lower()):
                    results.append({
                        'language': language,
                        **snippet
                    })
        
        return {
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results)
        }
    
    def generate_api_doc(self, code: str, language: str = 'python') -> Dict:
        """Generate API documentation from code"""
        
        doc = {
            'generated_at': datetime.now().isoformat(),
            'language': language,
            'endpoints': [],
            'functions': [],
            'classes': []
        }
        
        if language == 'python':
            # Extract functions
            import re
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):\s*"""([^"]*)"""', code)
            for func_name, func_doc in functions:
                doc['functions'].append({
                    'name': func_name,
                    'description': func_doc.strip()
                })
            
            # Extract classes
            classes = re.findall(r'class\s+(\w+)', code)
            for class_name in classes:
                doc['classes'].append({'name': class_name})
        
        return {
            'status': 'success',
            'documentation': doc
        }
