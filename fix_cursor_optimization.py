#!/usr/bin/env python3
"""
Fix the create_order function to use shared cursor for all DAO operations.
This resolves indentation and adds cursor=cursor to all relevant calls.
"""

import re

def fix_create_order():

    filepath = r'c:\Users\bjones2\NextGen-Finale\main\backend\server.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    #Find the cursor context line
    cursor_ctx_line = -1
    for i, line in enumerate(lines):
        if 'with get_db_cursor() as cursor:' in line and 'create_order' in '\n'.join(lines[max(0, i-50):i]):
            cursor_ctx_line = i
            break
    
    if cursor_ctx_line == -1:
        print("Could not find cursor context")
        return
    
    print(f"Found cursor context at line {cursor_ctx_line + 1}")
    
    # Find the next line after cursor context that needs indenting (should be # 1. Check/Create customer)
    start_indent_line = cursor_ctx_line + 1
    
    # Find the return statement that closes the function
    return_line = -1
    for i in range(cursor_ctx_line, len(lines)):
        if 'return {' in lines[i] and '"order_id":' in lines[i]:
            return_line = i
            break
    
    if return_line == -1:
        print("Could not find return statement")
        return
    
    print(f"Found return statement at line {return_line + 1}")
    
    # Now process the lines between cursor context and return
    updated_lines = lines[:cursor_ctx_line + 1]  # Keep everything up to and including cursor line
    
    # Add indented block
    for i in range(start_indent_line, return_line):
        line = lines[i]
        # Add 4 spaces of indentation if not already deeply indented
        current_indent = len(line) - len(line.lstrip())
        if current_indent >= 8:  # Already has base indentation for function body
            line = '    ' + line  # Add 4 more spaces for cursor context
        
        # Add cursor=cursor to DAO method calls
        if any(method in line for method in ['.get_by_key(', '.create_record(', '.get_all_records(', '.decrement_stock(']):
            if 'cursor=cursor' not in line and 'cursor=' not in line:
                # Handle different patterns
                if line.rstrip().endswith('()'):
                    line = line.replace('()', '(cursor=cursor)')
                elif line.rstrip().endswith('('):
                    # Parameter on next line - will be handled by next iteration
                    pass
                elif ')' in line and not line.strip().startswith('#'):
                    # Try to add cursor parameter
                    line = re.sub(r'\)(\s*)(#.*)?$', r', cursor=cursor)\1\2', line)
        
        updated_lines.append(line)
    
    # Add comment before return
    indent_str = ' ' * 12  # 8 base + 4 for cursor context
    updated_lines.append('')
    updated_lines.append(indent_str + '# All operations completed successfully - commit happens automatically')
    updated_lines.append(indent_str + '# when exiting the cursor context')
    
    # Add the return statement (also indented)
    for i in range(return_line, len(lines)):
        line = lines[i]
        if i == return_line or (i > return_line and i < return_line + 4):  # Return block
            current_indent = len(line) - len(line.lstrip())
            if current_indent >= 8:
                line = '    ' + line
        updated_lines.append(line)
        # Stop after the closing brace of return
        if i > return_line and '}' in line and line.strip() == '}':
            break
    
    # Add rest of file
    for i in range(return_line + 4, len(lines)):
        updated_lines.append(lines[i])
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"Fixed {len(updated_lines)} lines")
    print("Done!")

if __name__ == '__main__':
    fix_create_order()
