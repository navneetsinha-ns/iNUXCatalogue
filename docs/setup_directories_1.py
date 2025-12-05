import pandas as pd
from pathlib import Path
import re # Need re for sanitizing folder names

# --- CONFIGURATION ---
DATA_FILE = "assets/web_layout/pages.xlsx" 
#CONTENTS_ROOT = Path("docs") / "contents"
CONTENTS_ROOT = Path("contents")

# --- UTILITY FUNCTION ---
def sanitize_name(name):
    """Converts a string (title) into a safe, slug-like folder name."""
    # Replace spaces with underscores, remove non-alphanumeric characters, and convert to lowercase
    if pd.notna(name):
        name = str(name).strip()
        # Remove characters that are unsafe for file names
        name = re.sub(r'[^\w\s-]', '', name).strip()
        # Replace spaces and hyphens with a single underscore
        name = re.sub(r'[\s-]+', '_', name) 
        return name.lower()
    return ""

def safe_code(x):
    """Converts code to a padded string (e.g., 4 -> '04'), handles NaN."""
    return str(int(x)).zfill(2) if pd.notna(x) else None


# --- MAIN EXECUTION ---
try:
    # 1. Load Data
    df = pd.read_excel(DATA_FILE)
    print(f"Loaded data from {DATA_FILE}. Total rows: {len(df)}")

    # 2. Drop rows where Category Code is missing
    df.dropna(subset=['cat_code'], inplace=True)

    unique_paths = set()
    
    # 3. Iterate and construct the human-readable paths
    for _, row in df.iterrows():
        
        # --- Collect Codes and Names ---
        cat_code = safe_code(row.get('cat_code'))
        subcat_code = safe_code(row.get('sub_cat_code'))
        sub_sub_cat_code = safe_code(row.get('sub_sub_cat_code'))
        
        # NOTE: We use .get() here as the name columns might not be perfectly defined
        cat_name = sanitize_name(row.get('category'))
        subcat_name = sanitize_name(row.get('subcategory'))
        sub_sub_cat_name = sanitize_name(row.get('subsubcategory'))
        
        path_parts = []
        
        # 4. Build Path (Code + Name) incrementally
        
        if cat_code:
            # Level 1: Category Folder (e.g., 04_basic_hydrogeology)
            cat_folder = f"{cat_code}_{cat_name}" if cat_name else cat_code
            path_parts.append(cat_folder)
            
            if subcat_code and subcat_code != '00':
                # Level 2: Subcategory Folder (e.g., 01_concepts)
                subcat_folder = f"{subcat_code}_{subcat_name}" if subcat_name else subcat_code
                path_parts.append(subcat_folder)
                
                if sub_sub_cat_code and sub_sub_cat_code != '00':
                    # Level 3: Sub-Subcategory Folder (e.g., 02_theory)
                    sub_sub_cat_folder = f"{sub_sub_cat_code}_{sub_sub_cat_name}" if sub_sub_cat_name else sub_sub_cat_code
                    path_parts.append(sub_sub_cat_folder)
        
        if not path_parts:
            continue

        full_creation_path = CONTENTS_ROOT / Path(*path_parts)
        unique_paths.add(full_creation_path)

    # 5. Create Directories
    print(f"Creating {len(unique_paths)} unique directory structures...")
    
    for path in sorted(unique_paths):
        Path(path).mkdir(parents=True, exist_ok=True)
        print(f"Created: {path}")
        
    print("\n✅ Directory setup complete with human-readable names!")
    
except FileNotFoundError:
    print(f"\nFATAL ERROR: Could not find data file at {DATA_FILE}.")
    print("Please ensure you have downloaded 'pages.xlsx' and placed it in the 'spreadsheet/' folder.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")