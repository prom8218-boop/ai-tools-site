"""
🔍 Code Analysis & Optimization Module
Provides performance analysis, bug detection, and refactoring suggestions
"""

import ast
import re
from typing import Dict, List, Tuple

class CodeAnalyzer:
    """Advanced code analysis engine"""
    
    def __init__(self):
        self.issues = []
        self.metrics = {}
        self.suggestions = []
    
    # 🐛 BUG DETECTION ENGINE
    def detect_bugs(self, code: str, language: str = 'python') -> Dict:
        """Detect potential bugs and issues"""
        bugs = []
        
        if language == 'python':
            bugs.extend(self._detect_python_bugs(code))
        elif language in ['javascript', 'js']:
            bugs.extend(self._detect_js_bugs(code))
        elif language == 'java':
            bugs.extend(self._detect_java_bugs(code))
        elif language == 'cpp':
            bugs.extend(self._detect_cpp_bugs(code))
        
        return {
            'total_bugs': len(bugs),
            'severity': self._calculate_severity(bugs),
            'issues': bugs
        }
    
    def _detect_python_bugs(self, code: str) -> List[Dict]:
        """Python-specific bug detection"""
        bugs = []
        
        # 1️⃣ Mutable default argument detection
        mutable_default = re.findall(r'def\s+\w+\([^)]*=\s*(?:\[|\{)[^)]*\)', code)
        if mutable_default:
            bugs.append({
                'severity': 'HIGH',
                'type': 'Mutable Default Argument',
                'message': 'Using mutable objects as default arguments can cause unexpected behavior',
                'fix': 'Use None as default and initialize inside function',
                'line': self._find_line_number(code, mutable_default[0])
            })
        
        # 2️⃣ Bare except detection
        if 'except:' in code:
            bugs.append({
                'severity': 'HIGH',
                'type': 'Bare Exception',
                'message': 'Catching all exceptions without specifying type is dangerous',
                'fix': 'Use specific exception types: except ValueError, TypeError: ...',
                'line': code.count('\n', 0, code.index('except:')) + 1
            })
        
        # 3️⃣ Unused variables
        unused_vars = self._find_unused_variables(code)
        for var in unused_vars:
            bugs.append({
                'severity': 'LOW',
                'type': 'Unused Variable',
                'message': f'Variable "{var}" is defined but never used',
                'fix': f'Remove variable or use it in your logic',
                'line': -1
            })
        
        # 4️⃣ Missing return statement
        if 'def ' in code and '->' not in code and 'return' not in code:
            bugs.append({
                'severity': 'MEDIUM',
                'type': 'Missing Return',
                'message': 'Function does not return any value',
                'fix': 'Add return statement or use return type annotation',
                'line': -1
            })
        
        # 5️⃣ SQL Injection risk detection
        if 'query' in code.lower() and '+' in code:
            bugs.append({
                'severity': 'CRITICAL',
                'type': 'SQL Injection Risk',
                'message': 'String concatenation in SQL query detected',
                'fix': 'Use parameterized queries with placeholders (?)',
                'line': -1
            })
        
        # 6️⃣ Infinite loop detection
        if 'while True:' in code and 'break' not in code:
            bugs.append({
                'severity': 'HIGH',
                'type': 'Potential Infinite Loop',
                'message': 'while True loop without break statement',
                'fix': 'Add proper exit condition or break statement',
                'line': -1
            })
        
        return bugs
    
    def _detect_js_bugs(self, code: str) -> List[Dict]:
        """JavaScript-specific bug detection"""
        bugs = []
        
        # 1️⃣ == vs ===
        if '==' in code and '===' not in code:
            bugs.append({
                'severity': 'MEDIUM',
                'type': 'Loose Equality',
                'message': 'Using == instead of === can cause type coercion issues',
                'fix': 'Replace == with === for strict equality check',
                'line': -1
            })
        
        # 2️⃣ Missing var/let/const
        if re.search(r'(?<![var|let|const\s])\s[a-z_]\w*\s*=', code):
            bugs.append({
                'severity': 'HIGH',
                'type': 'Global Variable',
                'message': 'Variable assigned without var/let/const declaration',
                'fix': 'Use const, let, or var to declare variables',
                'line': -1
            })
        
        # 3️⃣ Callback hell
        if code.count('function(') > 3 and code.count('(function') > 2:
            bugs.append({
                'severity': 'MEDIUM',
                'type': 'Callback Hell',
                'message': 'Too many nested callbacks (pyramid of doom)',
                'fix': 'Use Promises or async/await instead',
                'line': -1
            })
        
        # 4️⃣ Missing error handling
        if 'fetch(' in code and '.catch' not in code:
            bugs.append({
                'severity': 'HIGH',
                'type': 'Unhandled Promise Rejection',
                'message': 'fetch() call without .catch() error handler',
                'fix': 'Add .catch() or use try/catch with async/await',
                'line': -1
            })
        
        return bugs
    
    def _detect_java_bugs(self, code: str) -> List[Dict]:
        """Java-specific bug detection"""
        bugs = []
        
        # 1️⃣ Null pointer risk
        if '.toString()' in code or '.length' in code:
            if 'null' not in code and '!=' not in code:
                bugs.append({
                    'severity': 'HIGH',
                    'type': 'NullPointerException Risk',
                    'message': 'Accessing object methods without null check',
                    'fix': 'Add null check: if (obj != null) before accessing',
                    'line': -1
                })
        
        # 2️⃣ Missing @Override
        if 'extends' in code and 'public' in code:
            bugs.append({
                'severity': 'MEDIUM',
                'type': 'Missing @Override',
                'message': 'Overriding methods should have @Override annotation',
                'fix': 'Add @Override annotation to overridden methods',
                'line': -1
            })
        
        return bugs
    
    def _detect_cpp_bugs(self, code: str) -> List[Dict]:
        """C++ specific bug detection"""
        bugs = []
        
        # 1️⃣ Memory leak risk
        if 'new ' in code and 'delete' not in code:
            bugs.append({
                'severity': 'HIGH',
                'type': 'Memory Leak Risk',
                'message': 'Memory allocated with new but never deleted',
                'fix': 'Use smart pointers (unique_ptr, shared_ptr) or delete memory',
                'line': -1
            })
        
        # 2️⃣ Buffer overflow
        if 'strcpy' in code or 'sprintf' in code:
            bugs.append({
                'severity': 'CRITICAL',
                'type': 'Buffer Overflow Risk',
                'message': 'Using unsafe functions: strcpy, sprintf',
                'fix': 'Use strncpy, snprintf instead',
                'line': -1
            })
        
        return bugs
    
    # 📊 PERFORMANCE ANALYSIS
    def analyze_performance(self, code: str, language: str = 'python') -> Dict:
        """Analyze code performance characteristics"""
        metrics = {
            'cyclomatic_complexity': self._calculate_complexity(code),
            'lines_of_code': len(code.split('\n')),
            'function_count': code.count('def ') if language == 'python' else 0,
            'nested_depth': self._max_nesting_depth(code),
            'performance_score': 0
        }
        
        # Calculate performance score (0-100)
        score = 100
        score -= min(metrics['cyclomatic_complexity'] * 2, 30)  # Complexity penalty
        score -= min(metrics['nested_depth'] * 5, 20)  # Nesting penalty
        
        metrics['performance_score'] = max(score, 0)
        metrics['performance_rating'] = self._rate_performance(metrics['performance_score'])
        
        return metrics
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or', 'try', 'except']
        
        for keyword in keywords:
            complexity += code.count(f' {keyword} ') + code.count(f' {keyword}\n')
        
        return complexity
    
    def _max_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char in '({[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')}]':
                current_depth -= 1
        
        return max_depth
    
    def _rate_performance(self, score: int) -> str:
        """Rate performance based on score"""
        if score >= 80:
            return "🟢 Excellent"
        elif score >= 60:
            return "🟡 Good"
        elif score >= 40:
            return "🟠 Average"
        else:
            return "🔴 Needs Improvement"
    
    # 💡 REFACTORING SUGGESTIONS
    def suggest_refactoring(self, code: str, language: str = 'python') -> List[Dict]:
        """Generate refactoring suggestions"""
        suggestions = []
        
        if language == 'python':
            # 1️⃣ Long function detection
            functions = re.findall(r'def\s+(\w+)\([^)]*\):[^d]*(?=\ndef|\Z)', code, re.MULTILINE)
            for func in functions:
                func_code = code[code.index(f'def {func}'):code.index(f'def {func}') + 200]
                if len(func_code) > 500:
                    suggestions.append({
                        'priority': 'HIGH',
                        'type': 'Long Function',
                        'message': f'Function "{func}" is too long (>500 lines)',
                        'suggestion': 'Break function into smaller, single-responsibility functions',
                        'benefit': 'Improved readability and testability'
                    })
            
            # 2️⃣ Magic number detection
            magic_numbers = re.findall(r'[^0-9]\s*([0-9]{4,})\s*(?:[,;:\)])', code)
            if magic_numbers:
                suggestions.append({
                    'priority': 'MEDIUM',
                    'type': 'Magic Numbers',
                    'message': f'Found {len(magic_numbers)} magic numbers in code',
                    'suggestion': 'Extract magic numbers to named constants',
                    'benefit': 'Improved code clarity and maintainability'
                })
            
            # 3️⃣ Duplicate code detection
            lines = code.split('\n')
            if len(lines) > 10:
                suggestions.append({
                    'priority': 'MEDIUM',
                    'type': 'Code Duplication',
                    'message': 'Potential code duplication detected',
                    'suggestion': 'Extract duplicate code into reusable functions',
                    'benefit': 'DRY principle, easier maintenance'
                })
            
            # 4️⃣ Type hints
            if 'def ' in code and '->' not in code:
                suggestions.append({
                    'priority': 'LOW',
                    'type': 'Missing Type Hints',
                    'message': 'No type hints found in function definitions',
                    'suggestion': 'Add type hints for better IDE support and documentation',
                    'benefit': 'Better code clarity and IDE autocompletion'
                })
            
            # 5️⃣ List comprehension opportunity
            if 'for ' in code and '.append(' in code:
                suggestions.append({
                    'priority': 'LOW',
                    'type': 'List Comprehension Opportunity',
                    'message': 'Loop with append can be simplified',
                    'suggestion': 'Use list comprehension: [x for x in items]',
                    'benefit': 'More Pythonic and slightly faster'
                })
        
        elif language in ['javascript', 'js']:
            # 1️⃣ Arrow function suggestion
            if 'function(' in code:
                suggestions.append({
                    'priority': 'LOW',
                    'type': 'Modernize Syntax',
                    'message': 'Using traditional function syntax',
                    'suggestion': 'Use arrow functions: const func = () => {}',
                    'benefit': 'Modern ES6+ syntax, shorter code'
                })
            
            # 2️⃣ Async/await suggestion
            if '.then(' in code and '.catch(' in code:
                suggestions.append({
                    'priority': 'MEDIUM',
                    'type': 'Promise Chain Complexity',
                    'message': 'Promise chain is hard to read',
                    'suggestion': 'Refactor using async/await syntax',
                    'benefit': 'More readable and easier to debug'
                })
        
        return suggestions
    
    def _find_unused_variables(self, code: str) -> List[str]:
        """Find unused variables in Python code"""
        unused = []
        try:
            tree = ast.parse(code)
            defined_vars = set()
            used_vars = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
            
            unused = list(defined_vars - used_vars)
        except:
            pass
        
        return unused
    
    def _find_line_number(self, code: str, text: str) -> int:
        """Find line number of text in code"""
        try:
            return code[:code.index(text)].count('\n') + 1
        except:
            return -1
    
    def _calculate_severity(self, bugs: List[Dict]) -> Dict[str, int]:
        """Calculate severity distribution"""
        severity = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for bug in bugs:
            severity[bug.get('severity', 'LOW')] += 1
        return severity
    
    # 🎯 COMPREHENSIVE ANALYSIS
    def full_analysis(self, code: str, language: str = 'python') -> Dict:
        """Perform comprehensive code analysis"""
        return {
            'bugs': self.detect_bugs(code, language),
            'performance': self.analyze_performance(code, language),
            'refactoring_suggestions': self.suggest_refactoring(code, language),
            'overall_score': self._calculate_overall_score(code, language)
        }
    
    def _calculate_overall_score(self, code: str, language: str) -> int:
        """Calculate overall code quality score"""
        bugs = self.detect_bugs(code, language)
        perf = self.analyze_performance(code, language)
        
        severity_penalty = {
            'CRITICAL': 20,
            'HIGH': 5,
            'MEDIUM': 2,
            'LOW': 1
        }
        
        bug_penalty = sum(severity_penalty.get(sev, 0) for sev in bugs['severity'].keys())
        base_score = perf['performance_score']
        final_score = max(base_score - bug_penalty, 0)
        
        return int(final_score)
