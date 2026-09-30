# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Parsing and search don't use the model, so they give the same result every time. The two tools after them call the model twice, and a slow or empty reply on either call ends the run without a fit card. I allow one of those in five tries. A bad parse is a second risk: my regex only knows a few ways of saying a price, so "under thirty bucks" gets no price limit.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
The whole path up to the branch uses no model: regex parsing, a keyword search, and an `if` on an empty list. The same query takes the same path every time, so there is no randomness to allow for. One failure out of five would mean the branch itself is wrong.

---

## 3. Something about state

Given a query that matches at least one listing, one listing is used from start to finish, in 5 of 5 tries. Three things show this:

- `session["selected_item"]["id"]` equals `session["search_results"][0]["id"]`.
- The item in the trace's `suggest_outfit` input line and in its `create_fit_card` input line has that listing's `title`, `price`, and `platform`.
- The fit card names no other listing's title.

**Why this target:**
The item goes from the session into both tools through plain Python, with no model involved, so there is no randomness to allow for. If a single try shows two different items, something in the loop overwrote the session. That's a bug, not bad luck. The third check is the only one that depends on the model. Captions are written from one item's details, so a card naming a different listing would mean the wrong item reached the tool.

---

## 4. Something about the fit card

The same matching query is run 5 times. At least 4 of the 5 fit cards meet all four of these conditions:

- The card is 2–4 sentences long.
- It contains the item's price as a dollar amount (e.g. `$24`).
- It contains the platform name, ignoring case (e.g. `depop`).
- It does not use the listing's `description` text word for word.

On top of that, no two of the 5 cards are identical word for word.

**Why this target:**
The model decides the wording, and it can legitimately write "24 bucks" or leave the platform out of a casual caption. So I allow one miss in five. I don't lower the target any further, because the prompt asks for the price and platform directly. The "no two identical" rule is 5 of 5. Identical cards mean caching is on or `TEMPERATURE` is 0, which is a settings mistake, not model variation.

---

## 5. Your choice

Five queries are each run once. Each query sets a size, a price limit, or both. Four examples:

- `graphic tee size M under $30`
- `jacket size S`
- `sneakers size US 9`
- `jeans under $40`

For every listing in `session["search_results"]`, both of these hold in 5 of 5 queries:

- `price` is at or below the price limit.
- The requested size is one whole size of the listing's `size` field, under the rule in the README's Tool Inventory. No `XL` comes back for `L`, and no `US 9` comes back for `S`.

**Why this target:**
Both filters are plain comparisons in `search_listings`, with no model involved. Filtering also happens before scoring, so keyword phrasing can't let an out-of-range listing through. Shoes shown to someone who asked for a small top look like a broken search, and a price over their limit breaks the one promise they gave us. So even one bad result in one query counts as a fail.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
