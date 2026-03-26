import json

def clean_notebook(path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            lines = cell.get('source', [])
            new_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Check for 3-line banner within JSON source list
                if line.startswith("# ===") and i+2 < len(lines):
                    next_line = lines[i+1].strip()
                    third_line = lines[i+2].strip()
                    
                    if next_line.startswith("# ") and third_line.startswith("# ==="):
                        # Keep only the descriptive middle line
                        new_lines.append(lines[i+1])
                        i += 3
                        continue
                new_lines.append(lines[i])
                i += 1
            cell['source'] = new_lines

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

if __name__ == "__main__":
    clean_notebook('Credit Card Fraud Detection.ipynb')
    print("Notebook banners cleaned successfully! 🧼")
