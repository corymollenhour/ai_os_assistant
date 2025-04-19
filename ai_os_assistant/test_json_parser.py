import re
import json
import sys

# Sample LLM responses that would previously cause errors
test_cases = [
    # Test case 1: Simple JSON with code 
    '''{"action": "run_code", "code": "open('test.txt', 'w').close()"}''',
    
    # Test case 2: JSON with f-strings that would previously fail
    '''{"action": "run_code", "code": "letters = ['a', 'b', 'c', 'd']; [open(f'{l}.txt', 'w').close() for l in letters]"}''',
    
    # Test case 3: JSON with nested curly braces
    '''{"action": "run_code", "code": "for i in range(26): open(f'{chr(97+i)}.txt', 'w').close()"}''',
    
    # Test case 4: JSON with multiple f-strings and operations
    '''{"action": "run_code", "code": "with open('test.txt', 'a') as f: f.write('Appended text\\n')"}''',
    
    # Test case 5: Messy JSON with thinking and other text around it
    '''<think>
I need to create files for this task.
</think>
{"action": "run_code", "code": "files = ['alpha.txt', 'beta.txt', 'gamma.txt']; [open(f, 'w').close() for f in files]"}
'''
]

def original_parser(content):
    """Simulate the original JSON parser that had issues"""
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in content")
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"Original parser error: {e}")
        return None

def improved_parser(content):
    """Implement our improved JSON parser with f-string handling"""
    # Try several approaches to handle different JSON extraction scenarios
    
    # Approach 1: Balanced brace counting
    try:
        json_start = content.find('{')
        if json_start != -1:
            brace_count = 1
            pos = json_start + 1
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if brace_count == 0:  # Found complete JSON object
                json_str = content[json_start:pos]
                # Pre-process f-strings
                processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                return json.loads(processed_json)
    except json.JSONDecodeError as e:
        print(f"Approach 1 error: {e}")
    
    # Approach 2: Complex regex for nested structures
    try:
        match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', content, re.DOTALL)
        if match:
            json_str = match.group(0).strip()
            processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
            return json.loads(processed_json)
    except json.JSONDecodeError as e:
        print(f"Approach 2 error: {e}")
    
    # Approach 3: Simple greedy pattern as last resort
    try:
        simple_match = re.search(r'\{.*?\}', content, re.DOTALL)
        if simple_match:
            json_str = simple_match.group(0)
            processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
            return json.loads(processed_json)
    except Exception as e:
        print(f"Approach 3 error: {e}")
    
    print("All parsing approaches failed")
    return None

def test_parser():
    """Test both parsers on all test cases and compare results"""
    print("TESTING JSON PARSING IMPROVEMENTS\n")
    print("================================\n")
    
    success_original = 0
    success_improved = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}:")
        print("-" * 40)
        print(f"Input: {test_case[:100]}{'...' if len(test_case) > 100 else ''}")
        
        # Test original parser
        original_result = original_parser(test_case)
        if original_result:
            success_original += 1
            print(f"Original parser SUCCESS: {original_result}")
        else:
            print("Original parser FAILED")
        
        # Test improved parser
        improved_result = improved_parser(test_case)
        if improved_result:
            success_improved += 1
            print(f"Improved parser SUCCESS: {improved_result}")
        else:
            print("Improved parser FAILED")
    
    print("\n\nSUMMARY:")
    print("-" * 40)
    print(f"Original parser success rate: {success_original}/{len(test_cases)} ({success_original/len(test_cases)*100:.1f}%)")
    print(f"Improved parser success rate: {success_improved}/{len(test_cases)} ({success_improved/len(test_cases)*100:.1f}%)")
    
    if success_improved > success_original:
        print("\nCONCLUSION: The improved JSON parser successfully handles cases that the original parser failed on.")
    else:
        print("\nCONCLUSION: The improved JSON parser did not show significant improvement.")

if __name__ == "__main__":
    test_parser()