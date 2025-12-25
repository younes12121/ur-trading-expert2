#!/usr/bin/env python3
"""
Automated Syntax Checker and Fixer
Checks telegram_bot.py for syntax errors and fixes common issues
"""

import ast
import sys
import re
from pathlib import Path

def check_syntax(file_path):
    """Check Python file for syntax errors"""
    print(f"Checking {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse
        try:
            ast.parse(source)
            print("  [OK] Syntax is valid")
            return True, None
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f"\n  Code: {e.text.strip()}"
            print(f"  [ERROR] {error_msg}")
            return False, e
    except Exception as e:
        print(f"  [ERROR] Could not check file: {e}")
        return False, e

def check_try_blocks(file_path):
    """Check for incomplete try blocks"""
    print(f"Checking try/except blocks in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    try_stack = []  # Stack of (line_num, indent_level)
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Check for try:
        if re.match(r'^\s+try:\s*$', line):
            try_stack.append((i, indent))
        
        # Check for except or finally
        elif re.match(r'^\s+(except|finally)', line):
            if try_stack:
                # Check if this matches the most recent try
                last_try_line, last_try_indent = try_stack[-1]
                if indent <= last_try_indent:
                    # This closes the try block
                    try_stack.pop()
        
        # Check for function/class definitions (they close any open try blocks)
        elif re.match(r'^\s*(async\s+)?def\s+\w+', line) or re.match(r'^\s*class\s+\w+', line):
            if try_stack:
                # Check if we're at same or lower indent
                last_try_line, last_try_indent = try_stack[-1]
                if indent <= last_try_indent:
                    # Function/class starts, so try block should be closed
                    issues.append({
                        'line': last_try_line,
                        'type': 'incomplete_try',
                        'message': f'Try block at line {last_try_line} not closed before function/class definition'
                    })
                    try_stack = []
    
    # Any remaining try blocks are incomplete
    for try_line, _ in try_stack:
        issues.append({
            'line': try_line,
            'type': 'incomplete_try',
            'message': f'Try block at line {try_line} missing except or finally clause'
        })
    
    if issues:
        print(f"  [WARNING] Found {len(issues)} incomplete try block(s):")
        for issue in issues:
            print(f"    Line {issue['line']}: {issue['message']}")
        return False, issues
    else:
        print("  [OK] All try blocks are complete")
        return True, None

def test_import(file_path):
    """Test if the module can be imported"""
    print(f"Testing import of {file_path}...")
    
    try:
        # Add current directory to path
        import sys
        sys.path.insert(0, str(file_path.parent))
        
        # Try to import
        module_name = file_path.stem
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        __import__(module_name)
        print("  [OK] Module imports successfully")
        return True, None
    except SyntaxError as e:
        print(f"  [ERROR] Syntax error during import: {e}")
        return False, e
    except Exception as e:
        print(f"  [WARNING] Import error (may be expected): {e}")
        return None, e  # Not a syntax error, might be missing dependencies

def main():
    file_path = Path('telegram_bot.py')
    
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return 1
    
    print("=" * 60)
    print("AUTOMATED SYNTAX CHECKER")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. Check syntax
    syntax_ok, syntax_error = check_syntax(file_path)
    if not syntax_ok:
        all_ok = False
    
    print()
    
    # 2. Check try blocks
    try_ok, try_issues = check_try_blocks(file_path)
    if not try_ok:
        all_ok = False
    
    print()
    
    # 3. Test import
    import_ok, import_error = test_import(file_path)
    if import_ok is False:  # Explicitly False (not None)
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("RESULT: All checks passed! File is syntactically correct.")
        return 0
    else:
        print("RESULT: Issues found. Review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

