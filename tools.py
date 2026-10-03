"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()

    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    if size:
        listings = [l for l in listings if _size_matches(size, l["size"])]

    query_words = _keywords(description)
    if not query_words:
        return []

    scored = []
    for listing in listings:
        score = _score(query_words, listing)
        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so ties keep the dataset's order
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# Words that carry no signal about what the user wants to buy.
_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "in", "on", "of", "to", "or",
    "some", "something", "i", "im", "want", "need", "looking", "find", "me",
    "my", "like", "that", "is", "it", "any", "under", "size",
}

# How much a keyword hit in each field counts toward a listing's score.
_FIELD_WEIGHTS = {
    "title": 3,
    "style_tags": 2,
    "category": 2,
    "colors": 2,
    "brand": 2,
    "description": 1,
}


def _normalize_word(word: str) -> str:
    """Lowercase and strip a plural 's' so 'tees' matches 'tee'."""
    word = word.lower()
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """Split text into normalized keywords, dropping stopwords."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {_normalize_word(w) for w in words if w not in _STOPWORDS}


def _score(query_words: set[str], listing: dict) -> int:
    """Weighted count of query keywords that appear in each listing field."""
    fields = {
        "title": listing["title"],
        "style_tags": " ".join(listing["style_tags"]),
        "category": listing["category"],
        "colors": " ".join(listing["colors"]),
        "brand": listing["brand"] or "",  # brand is None for most listings
        "description": listing["description"],
    }
    score = 0
    for field, text in fields.items():
        hits = query_words & _keywords(text)
        score += len(hits) * _FIELD_WEIGHTS[field]
    return score


def _size_tokens(size: str) -> set[str]:
    """
    Break a size string into the whole sizes it stands for.

    "S/M" → {"S/M", "S", "M"}, "W30 L30" → {"W30 L30", "W30", "L30"},
    "XL (oversized)" → {"XL"}, "US 8.5" → {"US 8.5", "US", "8.5"}.
    Parenthetical notes are dropped.
    """
    size = re.sub(r"\(.*?\)", "", size).upper().strip()
    tokens = {size}
    for part in size.split("/"):
        part = part.strip()
        if part:
            tokens.add(part)
            tokens.update(part.split())
    return tokens


def _size_matches(wanted: str, listing_size: str) -> bool:
    """
    True when the requested size is one of the listing's whole sizes.

    Case-insensitive, and never a substring test: "M" matches "S/M" and
    "M/L", but "S" does not match "US 9" and "L" does not match "XL".
    """
    wanted = re.sub(r"\s+", " ", wanted).upper().strip()
    return wanted in _size_tokens(listing_size)


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items") or []
    item_text = _describe_item(new_item)

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            "They haven't told us what's in their wardrobe. Give general styling "
            "advice: two outfit ideas built around this piece, naming the kinds of "
            "pieces it pairs well with (e.g. 'straight-leg dark jeans', 'chunky "
            "white sneakers'). Keep it under 120 words, plain text, no headings."
        )
        fallback = (
            f"Style the {new_item['title']} with simple basics in neutral colors "
            "and let it be the statement piece."
        )
    else:
        wardrobe_text = "\n".join(f"- {_describe_wardrobe_item(w)}" for w in items)
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            f"Here is what they already own:\n{wardrobe_text}\n\n"
            "Suggest one or two complete outfits built around the new piece. Use "
            "only pieces from their wardrobe, and name each one exactly as it's "
            "written above. Say in a sentence why each outfit works. Keep it "
            "under 150 words, plain text, no headings."
        )
        fallback = (
            f"Try the {new_item['title']} with {items[0]['name']} for an easy "
            "starting point."
        )

    system = (
        "You are a stylist who works with thrifted clothes. Be specific and "
        "practical. Never invent wardrobe pieces the user didn't list."
    )
    # The model can come back empty; the spec says this never returns "".
    return generate(prompt, system=system) or fallback


def _describe_item(item: dict) -> str:
    """One listing as prompt text. Brand is left out when it's None."""
    lines = [
        f"Title: {item['title']}",
        f"Category: {item['category']}",
        f"Colors: {', '.join(item['colors'])}",
        f"Style: {', '.join(item['style_tags'])}",
        f"Size: {item['size']}",
        f"Condition: {item['condition']}",
        f"Price: ${item['price']:.2f} on {item['platform']}",
    ]
    if item.get("brand"):
        lines.insert(1, f"Brand: {item['brand']}")
    return "\n".join(lines)


def _describe_wardrobe_item(item: dict) -> str:
    """One wardrobe piece as a single prompt line."""
    text = (
        f"{item['name']} ({item['category']}; {', '.join(item['colors'])}; "
        f"{', '.join(item['style_tags'])})"
    )
    if item.get("notes"):
        text += f" — {item['notes']}"
    return text


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            "Can't write a fit card yet: no outfit suggestion was given for "
            f"{new_item['title']}."
        )

    prompt = (
        f"Write a caption for a social post about this thrift find:\n"
        f"{_describe_item(new_item)}\n\n"
        f"How it's being styled:\n{outfit}\n\n"
        "Rules:\n"
        "- 2 to 4 sentences, first person, casual, like a real post.\n"
        f"- Mention the item, the price written as ${new_item['price']:g}, and "
        f"the platform ({new_item['platform']}) once each.\n"
        "- Be specific about the vibe of the outfit, not generic.\n"
        "- Don't copy the listing text. No hashtags, no emoji lists, no quotes "
        "around the caption."
    )
    system = "You write short, natural captions for outfit posts."
    caption = generate(prompt, system=system)
    return caption or (
        f"Picked up the {new_item['title']} for ${new_item['price']:g} on "
        f"{new_item['platform']} and it already has a place in my rotation."
    )
