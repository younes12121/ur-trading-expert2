#!/usr/bin/env python3
"""
Automated Syntax Error Fixer for telegram_bot.py
Finds and fixes common syntax errors like incomplete try blocks
"""

import ast
import re
from pathlib import Path

def find_incomplete_try_blocks(file_path):
    """Find try blocks without except or finally"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    try_blocks = []
    
    for i, line in enumerate(lines, 1):
        # Check for try: statements
        if re.match(r'^\s+try:\s*$', line):
            indent = len(line) - len(line.lstrip())
            try_blocks.append((i, indent))
        
        # Check for except or finally at same or lower indent
        if try_blocks:
            current_indent = len(line) - len(line.lstrip())
            if re.match(r'^\s*(except|finally)', line):
                # Check if this except/finally matches any try block
                for try_line, try_indent in try_blocks[:]:
                    if current_indent <= try_indent:
                        # This except/finally closes the try block
                        try_blocks.remove((try_line, try_indent))
    
    # Any remaining try blocks are incomplete
    for try_line, _ in try_blocks:
        issues.append({
            'line': try_line,
            'type': 'incomplete_try',
            'message': 'Try block without except or finally'
        })
    
    return issues

def check_syntax(file_path):
    """Check for Python syntax errors"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the file
        try:
            ast.parse(source)
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 0,
                'type': 'syntax_error',
                'message': str(e.msg),
                'text': e.text
            })
    except Exception as e:
        issues.append({
            'line': 0,
            'type': 'file_error',
            'message': f'Could not read file: {e}'
        })
    
    return issues

def fix_incomplete_try_block(file_path, line_number):
    """Fix an incomplete try block by adding except clause"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the try block
    try_line_idx = line_number - 1
    if try_line_idx >= len(lines):
        return False
    
    # Find the end of the function/block
    try_indent = len(lines[try_line_idx]) - len(lines[try_line_idx].lstrip())
    
    # Find where to insert except
    insert_pos = None
    for i in range(try_line_idx + 1, len(lines)):
        line = lines[i]
        current_indent = len(line) - len(line.lstrip())
        
        # If we hit a line with same or less indent that's not empty/comment
        if line.strip() and not line.strip().startswith('#'):
            if current_indent <= try_indent:
                # This is the end of the try block
                insert_pos = i
                break
    
    if insert_pos is None:
        insert_pos = len(lines)
    
    # Insert except block
    except_line = ' ' * try_indent + 'except Exception as e:\n'
    error_line = ' ' * (try_indent + 4) + f'await update.message.reply_text(f"❌ Error: {{str(e)}}")\n'
    
    lines.insert(insert_pos, except_line)
    lines.insert(insert_pos + 1, error_line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def main():
    file_path = Path('telegram_bot.py')
    
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return
    
    print("Checking for syntax errors...")
    
    # Check for syntax errors
    syntax_issues = check_syntax(file_path)
    
    # Check for incomplete try blocks
    try_issues = find_incomplete_try_blocks(file_path)
    
    all_issues = syntax_issues + try_issues
    
    if not all_issues:
        print("OK: No syntax errors found!")
        return
    
    print(f"\nFound {len(all_issues)} issue(s):")
    for issue in all_issues:
        print(f"  Line {issue['line']}: {issue['message']}")
    
    # Try to fix incomplete try blocks
    fixed = 0
    for issue in all_issues:
        if issue['type'] == 'incomplete_try':
            print(f"\nFixing incomplete try block at line {issue['line']}...")
            if fix_incomplete_try_block(file_path, issue['line']):
                fixed += 1
                print(f"  Fixed!")
            else:
                print(f"  Could not fix automatically")
    
    if fixed > 0:
        print(f"\nFixed {fixed} issue(s)!")
        print("Re-checking syntax...")
        
        # Re-check
        new_issues = check_syntax(file_path)
        if not new_issues:
            print("OK: All syntax errors fixed!")
        else:
            print(f"Still {len(new_issues)} issue(s) remaining:")
            for issue in new_issues:
                print(f"  Line {issue['line']}: {issue['message']}")
    else:
        print("\nCould not automatically fix issues. Manual review needed.")

if __name__ == '__main__':
    main()

