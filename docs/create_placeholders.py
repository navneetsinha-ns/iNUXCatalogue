import pandas as pd
from pathlib import Path
import re
import unicodedata
from typing import Any

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
DATA_FILE = "assets/web_layout/pages.xlsx"
CONTENTS_DIR = Path("contents")
INJECTION_MARKER = "<!--INJECT_RESOURCE_LIST_HERE-->"


# -------------------------------------------------
# HELPERS (copy-pasted to match your generator)
# -------------------------------------------------
def sanitize_name(name: str) -> str:
    """
    Turn a human-readable name into a filesystem-safe, ascii-ish slug.
    Must match the logic in your generator script.
    """
    if not name:
        return ""
    name = str(name).strip()

    # Normalize accents (ä -> a, é -> e, etc.)
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    name = name.lower()
    # keep only letters, digits, spaces, underscores, hyphens
    name = re.sub(r"[^\w\s-]", "", name)
    # collapse spaces/hyphens into single underscore
    name = re.sub(r"[\s-]+", "_", name)
    return name


def safe_code(x: Any) -> str:
    """
    Convert codes to 2-digit strings:
    1 -> '01', 0/''/NaN -> '00'.
    Must match your generator.
    """
    if x is None or x == "" or pd.isna(x):
        return "00"
    try:
        return f"{int(x):02d}"
    except (ValueError, TypeError):
        return str(x).zfill(2)


def build_content_path(row: pd.Series) -> Path:
    """
    Same logic as in your generator:
    contents/<cat_code>_<category>/<sub_code>_<subcategory>/.../<last>.md
    """
    cat_code = safe_code(row.get("cat_code", ""))
    sub_code = safe_code(row.get("sub_cat_code", ""))
    sub_sub_code = safe_code(row.get("sub_sub_cat_code", ""))

    category = row.get("category", "")
    subcategory = row.get("subcategory", "")
    subsubcategory = row.get("subsubcategory", "")

    cat_folder = f"{cat_code}_{sanitize_name(category)}"
    parts = [CONTENTS_DIR, cat_folder]

    if sub_code != "00":
        sub_folder = f"{sub_code}_{sanitize_name(subcategory)}"
        parts.append(sub_folder)

    if sub_sub_code != "00":
        sub_sub_folder = f"{sub_sub_code}_{sanitize_name(subsubcategory)}"
        parts.append(sub_sub_folder)

    md_folder = Path(*parts)
    md_filename = md_folder.name + ".md"
    return md_folder / md_filename


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main() -> None:
    # Load pages
    df = pd.read_excel(DATA_FILE, dtype=str).fillna("")
    print(f"Loaded {len(df)} rows from {DATA_FILE}")

    created = 0
    skipped = 0

    for _, row in df.iterrows():
        title = row.get("title", "") or "Untitled Page"
        content_path = build_content_path(row)

        # Make sure parent folders exist
        content_path.parent.mkdir(parents=True, exist_ok=True)

        if content_path.exists():
            # Don't overwrite existing content
            skipped += 1
            # print(f"Skipping existing file: {content_path}")
            continue

        placeholder = (
            f"# {title}\n\n"
            "Introductory content for this topic will be added here.\n\n"
            f"{INJECTION_MARKER}\n"
        )

        content_path.write_text(placeholder, encoding="utf-8")
        created += 1
        print(f"Created placeholder: {content_path}")

    print(f"\n✅ Done. Created {created} new markdown files, skipped {skipped} existing ones.")


if __name__ == "__main__":
    main()
