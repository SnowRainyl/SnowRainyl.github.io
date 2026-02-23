#!/usr/bin/env python3
"""
Auto-translate newly added Hugo blog posts between Chinese and English.
Called by GitHub Actions when content/zh/posts/** or content/en/posts/** changes.
"""

import os
import subprocess
import google.generativeai as genai


def get_added_posts(before_sha, after_sha):
    """Return markdown files that were Added in this push."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", before_sha, after_sha],
        capture_output=True, text=True, check=True,
    )
    return [f for f in result.stdout.strip().splitlines() if f.endswith(".md")]


def translate(model, content, from_lang, to_lang):
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
    response = model.generate_content(prompt)
    return response.text.strip()


def main():
    before_sha = os.environ.get("BEFORE_SHA", "HEAD~1")
    after_sha = os.environ.get("AFTER_SHA", "HEAD")

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")

    added = get_added_posts(before_sha, after_sha)
    if not added:
        print("No new posts detected.")
        return

    results = []
    for src in added:
        if src.startswith("content/zh/posts/"):
            dst = src.replace("content/zh/", "content/en/", 1)
            from_lang, to_lang = "zh", "en"
        elif src.startswith("content/en/posts/"):
            dst = src.replace("content/en/", "content/zh/", 1)
            from_lang, to_lang = "en", "zh"
        else:
            continue

        if os.path.exists(dst):
            print(f"Skip (already exists): {dst}")
            continue

        print(f"Translating {src} → {dst}")
        with open(src, encoding="utf-8") as f:
            content = f.read()

        translated = translate(model, content, from_lang, to_lang)

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(translated + "\n")

        results.append(dst)
        print(f"Created: {dst}")

    if results:
        print(f"\nDone: translated {len(results)} post(s).")
    else:
        print("Nothing to translate.")


if __name__ == "__main__":
    main()
