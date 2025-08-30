import json
import re 

def build_json(output_text):
    try:
        return json.loads(output_text)
    except json.JSONDecodeError:
        result = {}
        pattern = re.compile(r'\s*([^:]+?)\s*:\s*(.+?)(?=\s*[^:]+:\s*|$)')
        
        matches = pattern.findall(output_text)
        for key, value in matches:
            result[key.strip()] = value.strip().rstrip(',')
        return result