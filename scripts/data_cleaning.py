import os
import json
import re

def clean_markdown(text):
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'http\S+', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        "title": data.get("metadata", {}).get("title", ""),
        "description": data.get("metadata", {}).get("description", ""),
        "url": data.get("metadata", {}).get("url", ""),
        "content": clean_markdown(data.get("markdown", ""))
    }

def process_all_jsons(directory):
    output = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            print(f"Processing: {filename}")
            cleaned = process_json_file(filepath)
            output.append(cleaned)
    return output

if __name__ == "__main__":
    directory = "datafiles"
    cleaned_data = process_all_jsons(directory)

    # Save combined output (optional)
    with open('datafiles/cleaned_output.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print("✅ All files processed. Output saved to cleaned_output.json.")