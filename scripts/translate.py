#!/usr/bin/env python3
"""
Auto-translate Hugo blog posts that are missing a translation.
Scans all posts in content/zh/posts and content/en/posts,
translates any that don't have a corresponding version in the other language.
"""

import glob
import os
import re
import shutil
import subprocess
import time
from google import genai

# Fixed category name mapping — never let AI translate these freely
CATEGORY_MAP = {
    ("zh", "en"): {
        "技术探索": "Tech & Projects",
        "读书笔记": "Book Notes",
        "生活随笔": "Life & Travel",
    },
    ("en", "zh"): {
        "Tech & Projects": "技术探索",
        "Book Notes": "读书笔记",
        "Life & Travel": "生活随笔",
    },
}


def fix_categories(translated: str, original: str, from_lang: str, to_lang: str) -> str:
    """Override AI-translated categories with the correct mapped value."""
    mapping = CATEGORY_MAP.get((from_lang, to_lang), {})
    if not mapping:
        return translated

    # Extract categories value from original front matter (string or list format)
    m = re.search(r'^categories:\s*(.+)$', original, re.MULTILINE)
    if not m:
        return translated

    original_cat = m.group(1).strip()
    mapped_cat = mapping.get(original_cat)
    if not mapped_cat:
        return translated

    # Replace whatever the AI wrote for categories with the correct mapped value
    translated = re.sub(
        r'^(categories:).*$',
        f'\\1 {mapped_cat}',
        translated,
        flags=re.MULTILINE,
    )
    return translated


def _remove_file(path):
    """Remove a file and its parent directory if empty."""
    os.remove(path)
    parent = os.path.dirname(path)
    if os.path.isdir(parent) and not os.listdir(parent):
        os.rmdir(parent)


def sync_deletions():
    """Delete translation counterparts for two cases:
    1. Posts deleted in the current commit (fast path via git diff).
    2. Orphaned translations whose source was deleted in any past commit.
    """
    deleted = []

    # ── 1. Current-commit deletions ──────────────────────────────────────────
    try:
        result = subprocess.run(
            ['git', '-c', 'core.quotePath=false', 'diff', '--name-status', 'HEAD^', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if not line.startswith('D\t'):
                continue
            path = line[2:].strip()
            if path.startswith('content/zh/posts/') and path.endswith('.md'):
                counterpart = path.replace('content/zh/', 'content/en/', 1)
            elif path.startswith('content/en/posts/') and path.endswith('.md'):
                counterpart = path.replace('content/en/', 'content/zh/', 1)
            else:
                continue
            if os.path.exists(counterpart):
                _remove_file(counterpart)
                print(f"Deleted counterpart: {counterpart}")
                deleted.append(counterpart)
    except subprocess.CalledProcessError:
        pass  # No parent commit (initial commit)

    # ── 2. Historical orphans ─────────────────────────────────────────────────
    # An en post is an orphan if its zh source was once committed but is now gone.
    for lang_src, lang_dst in [('en', 'zh'), ('zh', 'en')]:
        for path in glob.glob(f"content/{lang_src}/posts/**/*.md", recursive=True):
            counterpart = path.replace(f'content/{lang_src}/', f'content/{lang_dst}/', 1)
            if os.path.exists(counterpart):
                continue  # Counterpart exists — not an orphan
            # Check whether the counterpart was ever committed (i.e. was deleted)
            log = subprocess.run(
                ['git', 'log', '--oneline', '--', counterpart],
                capture_output=True, text=True
            )
            if log.stdout.strip():
                # Counterpart existed before → this file is an orphaned translation
                _remove_file(path)
                print(f"Removed orphaned translation: {path}")
                deleted.append(path)

    return deleted


def get_untranslated_posts():
    """Return (src_path, from_lang, to_lang) for every post missing a translation."""
    pairs = []
    for src in sorted(glob.glob("content/zh/posts/**/*.md", recursive=True)):
        dst = src.replace("content/zh/", "content/en/", 1)
        if not os.path.exists(dst):
            pairs.append((src, "zh", "en"))
    for src in sorted(glob.glob("content/en/posts/**/*.md", recursive=True)):
        dst = src.replace("content/en/", "content/zh/", 1)
        if not os.path.exists(dst):
            pairs.append((src, "en", "zh"))
    return pairs


def translate(client, content, from_lang, to_lang):
    lang_name = {"zh": "Chinese (Simplified)", "en": "English"}
    prompt = (
        f"Translate the following Hugo blog post from {lang_name[from_lang]} "
        f"to {lang_name[to_lang]}.\n\n"
        "Rules:\n"
        "- Keep the YAML front matter block intact\n"
        "- Translate: title, tags values, and the body text\n"
        "- Do NOT translate or change: date, author, slug, image paths, URLs\n"
        "- Preserve all markdown syntax, code blocks, and image references\n"
        "- Return ONLY the translated file content, no explanation\n\n"
        "---\n"
        f"{content}"
    )
    for attempt in range(3):
        try:
            response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
            return response.text.strip()
        except Exception as e:
            if attempt < 2:
                wait = 20 * (attempt + 1)  # 20s, then 40s
                print(f"  Attempt {attempt + 1} failed ({e}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    deleted = sync_deletions()
    if deleted:
        print(f"Synced {len(deleted)} deletion(s).")

    pairs = get_untranslated_posts()
    if not pairs:
        if not deleted:
            print("All posts already have translations.")
        return

    print(f"Found {len(pairs)} post(s) to translate:")
    for src, fl, tl in pairs:
        print(f"  {src}  ({fl} → {tl})")

    for src, from_lang, to_lang in pairs:
        dst = src.replace(f"content/{from_lang}/", f"content/{to_lang}/", 1)
        print(f"\nTranslating: {src} → {dst}")

        with open(src, encoding="utf-8") as f:
            content = f.read()

        try:
            translated = translate(client, content, from_lang, to_lang)
            translated = fix_categories(translated, content, from_lang, to_lang)
        except Exception as e:
            print(f"ERROR translating {src}: {e}")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(translated + "\n")
        print(f"Created: {dst}")

        # Copy page bundle resources (images, etc.) to translation directory
        src_dir = os.path.dirname(src)
        dst_dir = os.path.dirname(dst)
        for resource in os.listdir(src_dir):
            if not resource.endswith(".md"):
                src_res = os.path.join(src_dir, resource)
                dst_res = os.path.join(dst_dir, resource)
                if os.path.isfile(src_res) and not os.path.exists(dst_res):
                    shutil.copy2(src_res, dst_res)
                    print(f"Copied resource: {dst_res}")

    print(f"\nDone: translated {len(pairs)} post(s).")


if __name__ == "__main__":
    main()
