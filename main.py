"""
1. Take an article and convert to JSON
2. Generate image slots JSON
3. Search for 1 image per query using the queries in image slots and convert to image slots with URLs
4. Use inject_images_into_html to insert image slots back into HTML
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from article_to_json import html_to_article_view, inject_images_into_html
from grok_image_suggester import generate_image_slots
# Import local modules
from image_search import search_images


def build_image_slots_from_specs(slot_specs):
    image_slots = []

    print(f"Processing {len(slot_specs)} image slots...")
    for spec in slot_specs:
        query = spec["search_query"]
        print(f"  Searching for: {query}")
        try:
            candidates = search_images(query, num_results=5)  # Google/Bing/Wikimedia/etc.
        except Exception as e:
            print(f"    Error searching for '{query}': {e}")
            continue

        if not candidates:
            print(f"    No images found for '{query}'")
            continue

        # simplest: just take top candidate
        top = candidates[0]

        alt_text = spec.get("alt_text_hint") or top.get("title") or ""
        caption = spec.get("caption_hint") or top.get("title") or ""

        image_slots.append({
            "section_id": spec["section_id"],
            "paragraph_id": spec.get("paragraph_id"),
            "position": spec.get("position", "after"),
            "image_url": top["url"],
            "alt_text": alt_text,
            "caption": caption,
        })

    return image_slots

def main(html_file_path):
    load_dotenv()
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Read HTML
    print(f"\n1. Reading article from {html_file_path}...")
    try:
        html_content = Path(html_file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Step 2: Convert to Article View JSON
    print("\n2. Converting to Article View JSON...")
    mutated_html, article_view = html_to_article_view(html_content)

    # Step 3: Generate image slots
    print("\n3. Generating image slot suggestions with Grok...")
    
    # Check for API key
    if not os.getenv("XAI_API_KEY"):
        print("Warning: XAI_API_KEY not found. Skipping Grok generation.")
        print("Please set XAI_API_KEY in .env file.")
        return

    # Save article_view temporarily for Grok API
    article_view_path = output_dir / "article_view.json"
    article_view_path.write_text(json.dumps(article_view, indent=2), encoding="utf-8")
    
    try:
        slots_data = generate_image_slots(
            input_path=str(article_view_path),
            output_path=str(output_dir / "image_slots_suggestions.json")
        )
    except Exception as e:
        print(f"Error generating slots: {e}")
        return

    # Step 4: Search for images and build final slots
    print("\n4. Searching for images...")
    suggested_slots = slots_data.get("slots", [])
    if not suggested_slots:
        print("No slots suggested.")
        return

    final_slots = build_image_slots_from_specs(suggested_slots)
    
    # Step 5: Inject images
    print("\n5. Injecting images into HTML...")
    enhanced_html = inject_images_into_html(mutated_html, final_slots)
    
    output_html_path = output_dir / "enhanced_article.html"
    output_html_path.write_text(enhanced_html, encoding="utf-8")
    
    print(f"\nDone! Enhanced article saved to {output_html_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python main.py <html_file_path>")
        sys.exit(1)
