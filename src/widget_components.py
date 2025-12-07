"""
Custom widget component renderers for Grokipedia articles.

These functions take extracted data (from Grok) and generate consistent, Tailwind-styled HTML snippets.
Assumes site's Tailwind CSS is available (inlined in scraped HTML); self-contained with classes for theme matching.
"""

from typing import Any, Dict, List


def render_timeline(events: List[Dict[str, str]]) -> str:
    """
    Render a vertical timeline widget.
    events: [{"date": "1971", "title": "Birth", "description": "Born in Pretoria..."}, ...]
    """
    if not events:
        return ""

    html = '''
<div class="widget-timeline mb-4 p-4 rounded-xl bg-neutral-50 border border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800">
  <h3 class="text-base font-semibold mb-3 text-neutral-900 dark:text-neutral-50">Timeline</h3>
  <div class="space-y-2">
'''

    for event in events[:8]:  # Limit to 8
        html += f'''
    <div class="flex gap-2.5">
      <div class="flex flex-col items-center">
        <span class="w-2 h-2 rounded-full border-2 border-sky-500 dark:border-sky-400 mt-1"></span>
        <span class="w-px flex-1 bg-neutral-300 dark:bg-neutral-700"></span>
      </div>
      <div class="pb-2">
        <time class="text-[11px] font-semibold text-sky-600 dark:text-sky-400">{event.get("date", "")}</time>
        <h4 class="text-sm font-semibold text-neutral-900 dark:text-neutral-100">{event.get("title", "")}</h4>
        <p class="text-xs text-neutral-500 dark:text-neutral-400">{event.get("description", "")}</p>
      </div>
    </div>
'''

    html += '  </div>\n</div>'
    return html


def render_key_facts(facts: List[str]) -> str:
    """
    Render a sidebar key facts panel.
    facts: ["Fact 1...", "Fact 2..."]
    """
    if not facts:
        return ""

    facts_html = ""
    for fact in facts[:10]:  # Limit
        facts_html += (
            '<li class="flex items-start gap-2 text-neutral-700 dark:text-neutral-300">'
            '<span class="shrink-0 text-sky-500 dark:text-sky-400">•</span>'
            f'<span class="leading-snug">{fact}</span>'
            '</li>'
        )

    html = f'''
<aside class="widget-key-facts w-full md:w-1/3 float-right mb-4 p-4 rounded-xl bg-neutral-50 border border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800">
  <h3 class="text-base font-semibold mb-2 text-neutral-900 dark:text-neutral-50">Key Facts</h3>
  <ul class="space-y-1.5 text-xs">
    {facts_html}
  </ul>
</aside>
'''
    return html

# Map type to renderer and data schema hint for Grok prompts
def render_stat_cards(stats: List[Dict[str, str]]) -> str:
    """
    Render a grid of stat cards for notable numerical facts.
    stats: [{"label": "Net Worth", "value": "$180B", "note": "As of 2024"}, ...]
    """
    if not stats:
        return ""

    cards_html = ""
    for stat in stats[:6]:  # Limit to 6 cards
        label = stat.get("label", "")
        value = stat.get("value", "")
        note = stat.get("note", "")
        cards_html += f'''
    <div class="p-3 rounded-lg border border-neutral-200 bg-white dark:border-neutral-700 dark:bg-neutral-800 text-center">
      <p class="text-[11px] uppercase tracking-wide text-neutral-500 dark:text-neutral-400">{label}</p>
      <p class="text-lg font-bold text-neutral-900 dark:text-neutral-50">{value}</p>
      {f'<p class="text-[10px] text-neutral-400 dark:text-neutral-500">{note}</p>' if note else ''}
    </div>
'''

    html = f'''
<div class="widget-stat-cards mb-4 p-4 rounded-xl bg-neutral-50 border border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800">
  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
    {cards_html}
  </div>
</div>
'''
    return html


def render_key_definitions(definitions: List[Dict[str, str]]) -> str:
    """
    Render a box of key definitions/terminology.
    definitions: [{"term": "API", "definition": "Application Programming Interface..."}, ...]
    """
    if not definitions:
        return ""

    defs_html = ""
    for i, defn in enumerate(definitions[:5]):  # Limit to 5
        term = defn.get("term", "")
        definition = defn.get("definition", "")
        border_class = 'border-t border-neutral-200 dark:border-neutral-700 pt-2 mt-2' if i > 0 else ''
        defs_html += f'''
    <div class="{border_class}">
      <span class="text-sm font-semibold text-neutral-900 dark:text-neutral-100">{term}</span>
      <span class="text-neutral-400 mx-1">—</span>
      <span class="text-xs text-neutral-500 dark:text-neutral-400">{definition}</span>
    </div>
'''

    html = f'''
<div class="widget-key-definitions mb-4 p-4 rounded-xl bg-neutral-50 border border-neutral-200 dark:bg-neutral-900 dark:border-neutral-800">
  <h3 class="text-base font-semibold mb-2 text-neutral-900 dark:text-neutral-50">Key Terms</h3>
  <div>
    {defs_html}
  </div>
</div>
'''
    return html



WIDGET_TYPES = {
    "timeline": {
        "renderer": render_timeline,
        "data_schema": "List of dicts: [{'date': str (e.g. '1971'), 'title': str, 'description': str}, ...] Extract 4-8 chronological events from context.",
    },
    "key_facts": {
        "renderer": render_key_facts,
        "data_schema": "List of strings: key facts, stats, or highlights (5-10 bullet points, concise).",
    },
    "stat_cards": {
        "renderer": render_stat_cards,
        "data_schema": "List of dicts: [{'label': str (e.g. 'Net Worth'), 'value': str (e.g. '$180B'), 'note': str (optional, e.g. 'As of 2024')}, ...] Extract 3-6 notable numerical facts.",
    },
    "key_definitions": {
        "renderer": render_key_definitions,
        "data_schema": "List of dicts: [{'term': str (e.g. 'API'), 'definition': str}, ...] Extract 2-5 key terms or concepts introduced in the section.",
    },
    # Add more widget types as needed
}

def render_widget(widget_type: str, extracted_data: Any) -> str:
    """
    Generic renderer: lookup and call specific function.
    """
    config = WIDGET_TYPES.get(widget_type)
    if config and config["renderer"]:
        return config["renderer"](extracted_data)
    else:
        print(f"Warning: No renderer for {widget_type}")
        return f'<div class="widget-unknown p-4 bg-yellow-100">Unsupported widget: {widget_type}</div>'
