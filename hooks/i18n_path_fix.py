"""
MkDocs hook to fix image src paths for multi-language sites.

PROBLEM:
--------
When using mkdocs-static-i18n, translated pages are served under /<lang>/ subdirectory:
  - English: /ControllerList.html
  - Simplified Chinese: /zh-CN/ControllerList.html

But image paths used in the pages are still the same (e.g., /SetupGuide/Images/foo.jpg).
So relative image paths break in translated pages:
  - From /ControllerList.html: "SetupGuide/Images/foo.jpg" → /SetupGuide/Images/foo.jpg ✓
  - From /zh-CN/ControllerList.html: "SetupGuide/Images/foo.jpg" → /zh-CN/SetupGuide/Images/foo.jpg ✗

SOLUTION:
---------
Convert relative path to go to the root, then add extra '../' to escape the /<lang>/ directory.

KEY INSIGHT:
------------
We process ALL pages (English + Simplified Chinese) with the SAME path transformations.
The transformed paths work for BOTH languages because:
  1. Simplified Chinese needs extra '../' to escape /zh-CN/
  2. English works with extra '../' too (can't go above root, so harmless)

EXAMPLE 1 - Root level page (ControllerList.md):
  Image path in the page: "SetupGuide/Images/foo.jpg"
  Transformed path:       "../SetupGuide/Images/foo.jpg"

  English webpage: /ControllerList.html:
    "../" goes to "/" (root) → /SetupGuide/Images/foo.jpg ✓

  Simplified Chinese webpage: /zh-CN/ControllerList.html:
    "../" goes to "/" (escapes /zh-CN/) → /SetupGuide/Images/foo.jpg ✓

EXAMPLE 2 - Nested page (SetupGuide/Controllers/Controller-ESP32-S3.md):
  Image path in the page: "../Images/foo.jpg" (up one level: Controllers → SetupGuide → Images)
  Transformed path:       "../../../SetupGuide/Images/foo.jpg" (up to root, then down to target)

  English /SetupGuide/Controllers/Controller-ESP32-S3.html:
    "../../../" tries to go up 3 levels but stops at "/" (root)
    → /SetupGuide/Images/foo.jpg ✓

  Simplified Chinese /zh-CN/SetupGuide/Controllers/Controller-ESP32-S3.html:
    "../../../" goes up 3 levels: Controllers → SetupGuide → zh-CN → root "/"
    → /SetupGuide/Images/foo.jpg ✓

WHEN IT RUNS:
-------------
The i18n plugin builds the site multiple times (once per language):
  1. English build: Hook processes all pages, adds extra '../' at root level (still works for English)
  2. Simplified Chinese build: Hook processes all pages, adds extra '../' at root level to escape /zh-CN/
  3. Fallback pages (English pages when there is no translations) are copied to /zh-CN/ with fixed paths
"""

import re
import logging

log = logging.getLogger('mkdocs.plugins.i18n_path_fix')

# List of language codes used in the site (add more as needed, e.g., ['zh-CN', 'zh-TW'])
LANGUAGES = ['zh-CN']


def on_page_markdown(markdown: str, page, config, files) -> str:
    """
    Fix relative paths in markdown files to work in both default and translated language builds.

    This hook is called by MkDocs for every page during the build process.
    It modifies image src attributes to add extra '../' levels to fix language-specific URL paths
    like /zh-CN/.

    Args:
        markdown: The markdown content of the page
        page: MkDocs page object with metadata
        config: MkDocs configuration
        files: Collection of all site files

    Returns:
        Modified markdown with fixed paths
    """
    # Extract the directory path of the source file, e.g. get "SetupGuide/Controllers" from
    # "SetupGuide/Controllers/Controller-ESP32-S3.md"
    # This tells us how deeply nested the page is in the directory structure
    src_dir = page.file.src_uri.rsplit('/', 1)[0] if '/' in page.file.src_uri else ''
    # Parse the source directory structure
    # e.g., "SetupGuide/Controllers/" → ["SetupGuide", "Controllers"]
    src_parts = src_dir.split('/') if src_dir else []

    # Fix both types of paths:
    # 1. Paths starting with '../' (e.g., "../Images/foo.jpg")
    # 2. Paths without '../' (e.g., "SetupGuide/Images/foo.jpg")
    markdown = _fix_relative_image_paths(markdown, src_parts)
    markdown = _fix_root_relative_image_paths(markdown)

    # Note: We do NOT modify markdown links ([text](page.md))
    # MkDocs expects links to stay as .md and converts them to .html automatically
    # The i18n plugin handles keeping links within the correct language directory

    return markdown


def _fix_relative_image_paths(markdown: str, src_parts: list[str]) -> str:
    """
    Fix image paths that start with '../' (relative paths going up directories).

    Example:
        Source file: SetupGuide/Controllers/Controller-ESP32-S3.md
        Original path: "../Images/foo.jpg" (goes up to SetupGuide, then to Images)
        Chinese URL: /zh-CN/SetupGuide/Controllers/Controller-ESP32-S3.html
        Fixed path: "../../../SetupGuide/Images/foo.jpg" (up 3 levels to root, then down)

    Args:
        markdown: The markdown content
        src_parts: Directories of the source file (e.g.,
            "SetupGuide/Controllers/Controller-ESP32-S3.md" → ["SetupGuide", "Controllers"])

    Returns:
        Markdown with fixed relative image paths
    """
    def fix_path(match):
        original_path = match.group(1)  # e.g., "../Images/foo.jpg"

        # Count how many '../' are in the original path
        up_count = 0
        path_remainder = original_path # path after ../
        while path_remainder.startswith('../'):
            up_count += 1
            path_remainder = path_remainder[3:]  # Remove '../'

        # Calculate which directory we'd be in after going up 'up_count' levels
        # e.g., from "SetupGuide/Controllers/", going up 1 level → "SetupGuide/"
        if up_count > 0 and up_count <= len(src_parts):
            parent_parts = src_parts[:-up_count] if up_count < len(src_parts) else []
        else:
            parent_parts = []

        # Build the new path for non-English builds:
        # 1. Go up enough levels to reach root (escape /zh-CN/ and directory structure)
        #    Need: len(src_parts) + 1 levels (directory depth + 1 for /zh-CN/)
        # 2. Go back down to the parent directory (if any)
        # 3. Append the remainder of the path
        new_up_count = len(src_parts) + 1  # +1 for the /<lang>/ prefix
        new_path = '../' * new_up_count

        if parent_parts:
            new_path += '/'.join(parent_parts) + '/'

        new_path += path_remainder

        return f'src="{new_path}"'

    # Find all image src attributes with relative paths starting with '../'
    # Regex: src="(\.\./[^"]+)" matches src="../anything"
    return re.sub(r'src="(\.\./[^"]+)"', fix_path, markdown)


def _fix_root_relative_image_paths(markdown):
    """
    Fix image paths that don't start with '../' (relative from page location).

    Example:
        Source file: ControllerList.md (at root level)
        Original path: "SetupGuide/Images/foo.jpg"
        Chinese URL: /zh-CN/ControllerList.html
        Fixed path: "../SetupGuide/Images/foo.jpg" (escape /zh-CN/, then down to target)

    Args:
        markdown: The markdown content

    Returns:
        Markdown with fixed root-relative image paths
    """
    def fix_path(match):
        original_path = match.group(1)

        # Skip paths that are already handled or shouldn't be modified:
        # - Already relative: starts with '../'
        # - Absolute: starts with '/'
        # - External: starts with 'http'
        if (original_path.startswith('../') or
            original_path.startswith('/') or
            original_path.startswith('http')):
            return match.group(0)  # Return unchanged

        # Add '../' prefix to escape the /<lang>/ directory
        # e.g., "SetupGuide/Images/foo.jpg" → "../SetupGuide/Images/foo.jpg"
        return f'src="../{original_path}"'

    # Find all image src attributes
    # Regex: src="([^"]+)" matches src="anything"
    # The function above filters which ones to modify
    return re.sub(r'src="([^"]+)"', fix_path, markdown)


# Future enhancement ideas:
# - Auto-detect LANGUAGES by scanning for .{lang}.md files
# - Add support for different path strategies (absolute paths, CDN, etc.)
# - Add validation/logging to help debug path issues
