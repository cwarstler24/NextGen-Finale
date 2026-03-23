#!/usr/bin/env python3
"""
Script to add cursor=cursor parameter to all DAO method calls in create_order function.
"""

import re

def update_server_cursor_params():
    file_path = r'c:\Users\bjones2\NextGen-Finale\main\backend\server.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_lines = []
    in_cursor_context = False
    cursor_indent = 0
    
    for i, line in enumerate(lines):
        # Detect when we enter the cursor context
        if 'with get_db_cursor() as cursor:' in line:
            in_cursor_context = True
            cursor_indent = len(line) - len(line.lstrip())
            updated_lines.append(line)
            continue
        
        # Detect when we exit the cursor context (return statement at same or lesser indent)
        if in_cursor_context and line.strip().startswith('return ') and (len(line) - len(line.lstrip())) <= cursor_indent:
            # Add comment before return
            indent_str = ' ' * (cursor_indent + 4)
            updated_lines.append('')
            updated_lines.append(indent_str + '# All operations completed successfully - commit happens automatically')
            updated_lines.append(indent_str + '# when exiting the cursor context')
            in_cursor_context = False
            updated_lines.append(line)
            continue
        
        # If we're in cursor context and line has a DAO method call, add cursor=cursor
        if in_cursor_context and line.strip():
            # Pattern for .method_name(
            pattern = r'(\.\s*(get_by_key|create_record|get_all_records|decrement_stock)\s*\()'
            
            if re.search(pattern, line):
                # Check if it already has cursor parameter
                if 'cursor=cursor' not in line and 'cursor=' not in line:
                    # Check if it's a multiline call (ends with comma or open paren)
                    if line.rstrip().endswith('('):
                        # Next line will have the params, mark for next iteration
                        updated_lines.append(line)
                        continue
                    elif line.rstrip().endswith(',') or not line.rstrip().endswith(')'):
                        # Multiline call with params already started
                        updated_lines.append(line)
                        continue
                    elif '()' in line:
                        # No parameters - add cursor=cursor
                        line = line.replace('()', '(cursor=cursor)')
                    else:
                        # Has parameters - add cursor=cursor at the end
                        # Find the closing paren
                        if re.search(r'\([^)]+\)', line):
                            line = re.sub(r'\)(\s*)(#.*)?$', r', cursor=cursor)\1\2', line)
        
        updated_lines.append(line)
    
    # Write back
    updated_content = '\n'.join(updated_lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Updated server.py with cursor parameters")
    print(f"Modified {len([l for l in updated_lines if 'cursor=cursor' in l and i > 0 and 'cursor=cursor' not in lines[updated_lines.index(l)]])} lines")

if __name__ == '__main__':
    update_server_cursor_params()
