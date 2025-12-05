import pandas as pd
from pathlib import Path
import yaml
import re
import unicodedata
from typing import Any, Dict, List, Optional  # <-- only change: added Optional

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
DATA_FILE = "assets/web_layout/pages.xlsx"      # master spreadsheet
RESOURCES_DIR = Path("assets/resources")         # YAML submissions from Streamlit app
OUTPUT_DOCS_DIR = Path("docs")            # final Jekyll pages
CONTENTS_DIR = Path("contents")           # base page content

OUTPUT_DOCS_DIR.mkdir(exist_ok=True)

# This marker must also exist in your markdown templates in contents/
INJECTION_MARKER = "<!--INJECT_RESOURCE_LIST_HERE-->"


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def sanitize_name(name: str) -> str:
    """
    Turn a human-readable name into a filesystem-safe, ascii-ish slug.
    Used for reconstructing paths into the contents/ tree.
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
    """
    if x is None or x == "" or pd.isna(x):
        return "00"
    try:
        return f"{int(x):02d}"
    except (ValueError, TypeError):
        return str(x).zfill(2)


def as_bool(x: Any) -> bool:
    """
    Robust boolean cast for YAML/string values.
    Accepts True, "true", "yes", "y", "1", "on".
    """
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    return str(x).strip().lower() in {"true", "yes", "y", "1", "on"}


def as_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except (ValueError, TypeError):
        return default


def as_list(x: Any) -> List[str]:
    """
    Normalize a YAML field to a list of strings.

    - list -> list of str
    - str  -> [str] if not empty
    - None/"" -> []
    """
    if isinstance(x, list):
        return [str(v).strip() for v in x if str(v).strip()]
    if x is None:
        return []
    s = str(x).strip()
    if not s:
        return []
    return [s]


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "resource"


# -------------------------------------------------
# IMAGE / COVER HELPERS
# -------------------------------------------------
def pick_cover_figure(figures: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Decide which figure to use as the cover image for a resource.

    Priority:
    1. First figure with 'is_cover: true' (set in CataLogger).
    2. Otherwise, the first figure in the list.
    """
    if not figures:
        return None

    # 1) explicit cover flag from CataLogger
    for fig in figures:
        if fig.get("is_cover"):
            return fig

    # 2) fallback: first figure
    return figures[0]


def infer_figure_url(resource: Dict[str, Any], fig: Dict[str, Any]) -> Optional[str]:
    """
    Build the URL for a specific figure of this resource.
    Uses the same naming convention as the ZIP export.

    /assets/resources/<stem>/<stem>_fig<ID>.<ext>
    """
    base_name = resource.get("_file_stem")
    if not base_name:
        return None

    fig_id = fig.get("id")
    orig = fig.get("original_filename") or ""
    ext = Path(orig).suffix.lower()  # keep original extension

    if not fig_id or not ext:
        return None

    return f"/assets/resources/{base_name}/{base_name}_fig{fig_id}{ext}"


def infer_cover_url(resource: Dict[str, Any]) -> Optional[str]:
    """
    Wrapper around pick_cover_figure + infer_figure_url.
    """
    figures = resource.get("figures") or []
    if not figures:
        return None

    cover_fig = pick_cover_figure(figures)
    if not cover_fig:
        return None

    return infer_figure_url(resource, cover_fig)


# -------------------------------------------------
# RESOURCE LOADING (YAML FROM STREAMLIT APP)
# -------------------------------------------------
def load_all_resources(resources_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load all YAML resource files and group them by the "topic_page_id" (if present)
    or by "topic" (which should match the page title).

    Supports:
    - New CataLogger format (item_id, authors[], fit_for, Streamlit metadata, etc.)
    - Older format with author / author_institute fields.
    """
    resource_data: Dict[str, List[Dict[str, Any]]] = {}

    for yaml_file in resources_dir.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading {yaml_file.name}: {e}")
            continue

        # --- Common core fields (with fallbacks) ---
        title = (data.get("title") or yaml_file.stem).strip()
        topic = str(data.get("topic") or "").strip()
        topic_page_id = str(data.get("topic_page_id") or "").strip()  # optional, future use

        # remember where this YAML came from + its figures
        data["_file_stem"] = yaml_file.stem
        data["figures"] = data.get("figures") or []  # list of {id, original_filename, ..., is_cover}

        # Prefer explicit ID-based mapping if available
        if topic_page_id:
            key = topic_page_id
        elif topic:
            key = topic
        else:
            print(
                f"Warning: Resource {yaml_file.name} missing 'topic_page_id' "
                f"and 'topic'. Skipping."
            )
            continue

        # --- Normalize lists/booleans from CataLogger ---
        data["keywords"] = as_list(data.get("keywords"))
        data["fit_for"] = as_list(data.get("fit_for"))

        # references: ensure list of strings
        refs = data.get("references", [])
        if isinstance(refs, list):
            data["references"] = [str(r).strip() for r in refs if str(r).strip()]
        elif refs:
            data["references"] = [str(refs).strip()]
        else:
            data["references"] = []

        # --- Authors normalization ---
        # New format: authors: [ {name, affiliation}, ... ]
        authors = data.get("authors")
        if isinstance(authors, list) and authors:
            normalized_authors = []
            for a in authors:
                if not isinstance(a, dict):
                    continue
                name = (a.get("name") or "").strip()
                aff = (a.get("affiliation") or "").strip()
                if not name:
                    continue
                if not aff:
                    aff = "TO_BE_FILLED_BY_COURSE_MANAGER"
                normalized_authors.append({"name": name, "affiliation": aff})
            data["authors"] = normalized_authors
        else:
            # Fallback: older single-author fields
            author_name = (data.get("author") or "").strip()
            author_inst = (data.get("author_institute") or "").strip()
            if author_name:
                data["authors"] = [{"name": author_name, "affiliation": author_inst or "N/A"}]
            else:
                data["authors"] = []

        # --- item_id / resource_id alignment ---
        item_id = (data.get("item_id") or "").strip()
        if item_id and not item_id.startswith("TO_BE_FILLED_BY_COURSE_MANAGER"):
            resource_id = item_id
        else:
            resource_id = slugify(title)
        data["resource_id"] = resource_id

        # Store under key
        resource_data.setdefault(key, []).append(data)

    return resource_data


# -------------------------------------------------
# RESOURCE → MARKDOWN
# -------------------------------------------------
def format_authors_for_table(authors: List[Dict[str, str]]) -> str:
    """
    Convert list of {name, affiliation} into a single string:
    'Name1 (Aff1); Name2 (Aff2)' or 'N/A' if empty.
    """
    if not authors:
        return "N/A"
    chunks = []
    for a in authors:
        name = (a.get("name") or "").strip()
        aff = (a.get("affiliation") or "").strip()
        if name and aff:
            chunks.append(f"{name} ({aff})")
        elif name:
            chunks.append(name)
    return "; ".join(chunks) if chunks else "N/A"


def format_resource_markdown(resource: Dict[str, Any]) -> str:
    """
    Format a single resource block as markdown, compatible with
    the YAML generated by the CataLogger Streamlit app.
    """
    title = resource.get("title", "Untitled Resource")
    resource_type = resource.get("resource_type", "N/A")
    time_required = resource.get("time_required", "N/A")
    date_released = resource.get("date_released", "N/A")
    description_short = resource.get("description_short", "No description provided.")
    url = resource.get("url", "#")

    keywords = as_list(resource.get("keywords"))
    fit_for = as_list(resource.get("fit_for"))
    authors = resource.get("authors", [])
    authors_str = format_authors_for_table(authors)

    figures = resource.get("figures") or []
    cover_fig = pick_cover_figure(figures) if figures else None

    cover_url = infer_cover_url(resource)

    md = ""

    # --- Header first ---
    md += f"## {title}\n\n"


    # --- Main summary line ---
   # Released: only show if a meaningful value exists
    release_value = str(date_released).strip()
    if release_value and not release_value.upper().startswith("TO_BE_FILLED"):
        release_part = f" | **Released:** {release_value}"
    else:
        release_part = ""

    md += (
        f"**Type:** {resource_type} | "
        f"**Time:** {time_required}"
        f"{release_part}\n\n"
    )
    
     # --- Then optional cover image (per-resource) ---
    if cover_url:
        md += f"![{title}]({cover_url})\n\n"

    md += f"{description_short}\n\n"


    # --- Launch link + main detail table ---
    md += f"[**LAUNCH RESOURCE**]({url})\n\n"
    md += "| Detail | Value |\n"
    md += "| :--- | :--- |\n"
    md += f"| **URL** | [{url}]({url}) |\n"
    md += f"| **Author(s)** | {authors_str} |\n"
    md += f"| **Keywords** | {', '.join(keywords) if keywords else '—'} |\n"
    md += f"| **Fit For** | {', '.join(fit_for) if fit_for else '—'} |\n"
    md += f"| **Prerequisites** | {resource.get('prerequisites', 'None specified.')} |\n"

    refs = resource.get("references", [])
    if refs:
        ref_text = "<br>".join(refs)
        md += f"| **References** | {ref_text} |\n"

    # --- Extra table only for Streamlit apps (CataLogger metadata) ---
    if str(resource_type).lower().startswith("streamlit"):
        multipage_app = as_bool(resource.get("multipage_app", False))
        num_pages = as_int(resource.get("num_pages", 0))

        interactive_plots = as_bool(resource.get("interactive_plots", False))
        num_interactive_plots = as_int(resource.get("num_interactive_plots", 0))

        assessments_included = as_bool(resource.get("assessments_included", False))
        num_assessment_questions = as_int(resource.get("num_assessment_questions", 0))

        videos_included = as_bool(resource.get("videos_included", False))
        num_videos = as_int(resource.get("num_videos", 0))

        md += "\n### Streamlit app details\n\n"
        md += "| Detail | Value |\n"
        md += "| :--- | :--- |\n"
        md += f"| Multipage app | {'yes' if multipage_app else 'no'} |\n"
        md += f"| Number of pages | {num_pages if multipage_app and num_pages > 0 else '—'} |\n"
        md += f"| Interactive plots | {'yes' if interactive_plots else 'no'} |\n"
        md += f"| Number of interactive plots | {num_interactive_plots if interactive_plots and num_interactive_plots > 0 else '—'} |\n"
        md += f"| Assessments included | {'yes' if assessments_included else 'no'} |\n"
        md += f"| Number of assessment questions | {num_assessment_questions if assessments_included and num_assessment_questions > 0 else '—'} |\n"
        md += f"| Videos included | {'yes' if videos_included else 'no'} |\n"
        md += f"| Number of videos | {num_videos if videos_included and num_videos > 0 else '—'} |\n"

    # --- Images section for remaining figures ---
    other_figs: List[Dict[str, Any]] = []
    if figures:
        if cover_fig is not None and cover_fig.get("id") is not None:
            cover_id = cover_fig.get("id")
            other_figs = [f for f in figures if f.get("id") != cover_id]
        else:
            other_figs = figures

    if other_figs:
        md += "\n### Images\n\n"
        for fig in other_figs:
            url_fig = infer_figure_url(resource, fig)
            if not url_fig:
                continue

            fid = fig.get("id")
            fcap = (fig.get("caption") or "").strip()
            ftype = (fig.get("type") or "").strip()

            alt = fcap or f"Image {fid} for {title}"
            md += f"![{alt}]({url_fig})\n\n"

            caption_parts = []
            if fcap:
                caption_parts.append(fcap)
            if ftype:
                caption_parts.append(f"({ftype})")
            if caption_parts:
                md += "*" + " ".join(caption_parts) + "*\n\n"

    md += "\n---\n\n"
    return md



# -------------------------------------------------
# CONTENT PATH RECONSTRUCTION
# -------------------------------------------------
def build_content_path(row: pd.Series) -> Path:
    """
    Reconstruct the path to the base markdown in contents/ using the codes
    from the spreadsheet:

      contents/<cat_code>_<category>/<sub_code>_<subcategory>/.../<last>.md

    where codes are always 2 digits (01, 02, ...)
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
# MAIN EXECUTION
# -------------------------------------------------
def main() -> None:
    # 1. Load spreadsheet
    df = pd.read_excel(DATA_FILE, dtype=str).fillna("")
    all_resources = load_all_resources(RESOURCES_DIR)

    # Precompute title and parent lookups by page_id
    title_by_page_id: Dict[str, str] = dict(zip(df["page_id"], df["title"]))
    parent_by_page_id: Dict[str, str] = dict(zip(df["page_id"], df["parent_id"]))

    print(f"Loaded {len(df)} pages from {DATA_FILE}")
    print(f"Loaded {sum(len(v) for v in all_resources.values())} resources.")

    for _, row in df.iterrows():
        page_id = row["page_id"]
        parent_id = row["parent_id"]
        title = row["title"]
        layout = (row.get("layout") or "home") or "home"
        lang_code = (row.get("lang_code") or "en") or "en"

        # nav_order from display_order
        try:
            nav_order = int(row["display_order"])
        except (ValueError, TypeError):
            print(f"Warning: display_order invalid for {page_id} ({title}). Skipping.")
            continue

        has_children = as_bool(row.get("has_children", ""))

        # --- Jekyll / Just-the-Docs front matter ---
        frontmatter: Dict[str, Any] = {
            "title": title,
            "layout": layout,
            "nav_order": nav_order,
            "has_children": has_children,
        }

        # JTD parent / grand_parent resolved by title from page_id
        if parent_id:
            parent_title = title_by_page_id.get(parent_id)
            if parent_title:
                frontmatter["parent"] = parent_title

                # optional grand_parent
                gp_id = parent_by_page_id.get(parent_id, "")
                if gp_id:
                    gp_title = title_by_page_id.get(gp_id)
                    if gp_title:
                        frontmatter["grand_parent"] = gp_title

        fm_text = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n"

        # Internal metadata as HTML comments (safe for JTD)
        meta_comments = (
            f"<!-- page_id: {page_id} -->\n"
            f"<!-- parent_id: {parent_id} -->\n"
            f"<!-- lang_code: {lang_code} -->\n\n"
        )

        # 2. Load base content from contents/ tree
        content_path = build_content_path(row)
        try:
            existing_body = content_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Base content not found at {content_path}. Using placeholder for {page_id}.")
            existing_body = f"# {title}\n\nNo introductory content yet.\n\n{INJECTION_MARKER}\n"

        # 3. Gather resources for this page
        # Prefer page_id-based mapping; fallback to title (= topic)
        resources_for_topic = all_resources.get(page_id, [])
        if not resources_for_topic:
            resources_for_topic = all_resources.get(title, [])

        resources_list_md = f"## Interactive Resources ({title})\n\n"
        if resources_for_topic:
            # stable order by resource title
            resources_for_topic = sorted(
                resources_for_topic, key=lambda r: str(r.get("title", "")).lower()
            )
            for res in resources_for_topic:
                resources_list_md += format_resource_markdown(res)
        else:
            resources_list_md += "No resources submitted for this topic yet.\n\n"

        # 4. Inject resource list at marker (or append at the end)
        if INJECTION_MARKER in existing_body:
            before_marker, _, after_marker = existing_body.partition(INJECTION_MARKER)
            final_body = (
                before_marker
                + INJECTION_MARKER
                + "\n\n"
                + resources_list_md
                + after_marker
            )
        else:
            final_body = existing_body + "\n\n" + resources_list_md
            print(f"Note: marker not found in {content_path.name}, appended resources at end.")

        # 5. Write final Jekyll page
        out_path = OUTPUT_DOCS_DIR / f"{page_id}.md"
        out_path.write_text(fm_text + meta_comments + final_body, encoding="utf-8")
        print(f"✅ Wrote {out_path}")


if __name__ == "__main__":
    main()
