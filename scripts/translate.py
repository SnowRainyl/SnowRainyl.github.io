#!/usr/bin/env python3
"""
Auto-translate Hugo blog posts that are missing a translation.
Scans all posts in content/zh/posts and content/en/posts,
translates any that don't have a corresponding version in the other language.
"""

import glob
import os
from google import genai


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
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text.strip()


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    pairs = get_untranslated_posts()
    if not pairs:
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

        translated = translate(client, content, from_lang, to_lang)

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(translated + "\n")
        print(f"Created: {dst}")

    print(f"\nDone: translated {len(pairs)} post(s).")


if __name__ == "__main__":
    main()
