# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

### `search_listings`

- **What it does:** Filters `data/listings.json` by price and size, then ranks what's left by how many of the description's keywords appear in each listing. It does not call the model.
- **Inputs:**
  - `description` (str): keywords such as `"vintage graphic tee"`. Matching ignores case and a trailing plural "s". Filler words ("a", "for", "looking", …) are ignored.
  - `size` (str | None): `None` skips the size filter. Otherwise the size must equal one whole size in the listing's `size` field, ignoring case. That field is split on `/` and spaces, and anything in parentheses is dropped. So `"M"` matches `"S/M"` and `"M/L"`, `"W30"` matches `"W30 L30"`, and `"XL"` matches `"XL (oversized)"`. It is never a substring test: `"S"` does not match `"US 9"`, and `"L"` does not match `"XL"`. `"One Size"` items match only a request for `"one size"`.
  - `max_price` (float | None): `None` skips the price filter. Otherwise the price must be at or below it (inclusive).
- **Returns:** A `list[dict]` of at most `config.SEARCH_RESULT_LIMIT` (10) listing dicts, highest score first. Ties keep the order they have in the dataset. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size` (str), `condition`, `price` (float), `colors` (list), `brand` (str or None), and `platform`. A score is the weighted count of keywords found in each field: title ×3; style_tags, category, colors, and brand ×2; description ×1. Listings that score 0 are dropped.
- **When it has nothing:** It returns an empty list `[]`, never `None` and never an exception. This covers no matches after filtering, and a description that is empty or only filler words.

### `suggest_outfit`

- **What it does:** Asks the model, through `generate()`, for one or two outfits built around the thrifted item. The outfits name pieces the user already owns.
- **Inputs:**
  - `new_item` (dict): one listing dict from `search_listings`, with the fields listed above.
  - `wardrobe` (dict): has an `items` key holding a list of wardrobe item dicts. Each item has `id`, `name`, `category`, `colors` (list), `style_tags` (list), and an optional `notes`. The `items` list may be empty.
- **Returns:** A non-empty `str` of plain text describing one or two outfits. Each outfit names the new item plus specific wardrobe pieces by their `name`.
- **When it has nothing:** If `wardrobe["items"]` is empty, it still returns a non-empty `str`: general styling advice for the item, with the kinds of pieces it pairs well with and no wardrobe items named. It never returns `""` and never raises for an empty wardrobe. If the model can't be reached, `ModelUnavailable` is raised, and the loop handles it.

### `create_fit_card`

- **What it does:** Asks the model, through `generate()`, for a short caption someone would actually post about the find. It should read like a real post, not a product description.
- **Inputs:**
  - `outfit` (str): the text that `suggest_outfit` returned.
  - `new_item` (dict): the same listing dict that was passed to `suggest_outfit`.
- **Returns:** A `str` caption of two to four sentences. It mentions the item's `title`, its `price`, and its `platform` once each, and it is specific about the vibe. It must not assume `brand` is present, because that field is often `None`. The caption varies from run to run, because `TEMPERATURE` is above 0.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns this `str` without calling the model: `"Can't write a fit card yet: no outfit suggestion was given for <title>."` It never raises and never returns `""`.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` and stop, returning the session with `selected_item`, `outfit_suggestion`, and `fit_card` still `None`. The message names the filters that were used and how to loosen each one. Otherwise, take the first result as `session["selected_item"]` and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(l['title'], l['size'], l['price']) for l in search_listings('graphic tee', max_price=30)])"
[('Graphic Tee — 2003 Tour Bootleg Style', 'L', 24.0), ('Y2K Baby Tee — Butterfly Print', 'S/M', 18.0), ('Vintage Band Tee — Faded Grey', 'L', 19.0), ('Vintage Graphic Hoodie — Faded Black', 'L', 26.0), ('Mesh Long-Sleeve Top — Black', 'S/M', 15.0), ('Low-Rise Cargo Pants — Khaki', 'W29', 27.0), ('Oversized Crewneck Sweatshirt — Vintage Navy', 'XL (fits oversized)', 20.0)]

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit one pairs the vintage Levi's 501 jeans with the white ribbed tank top, the vintage black denim jacket, and the chunky white sneakers, finished with the brown leather belt. This outfit works because the fitted white tank balances the straight-leg vintage denim, while the cropped black jacket and chunky sneakers nail an effortless streetwear aesthetic.

Outfit two pairs the vintage Levi's 501 jeans with the oversized grey crewneck sweatshirt, the black combat boots, and the brown leather belt. This outfit works because tucking the front of the super-sized grey sweatshirt into the mid-wash jeans creates a balanced silhouette, and the black lace-up boots add a sharp grunge edge to the classic denim.

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
For a casual streetwear look, pair these medium wash 501s with a relaxed grey cotton crewneck sweatshirt and low-profile canvas skate sneakers. Add a worn-in black leather belt to break up the waist and carry a canvas tote bag.

For a sharper vintage-inspired outfit, tuck a fitted black ribbed turtleneck into the waistband. Layer an oversized plaid flannel overshirt worn unbuttoned on top, and finish the look with dark leather ankle boots. Roll the denim cuffs once or twice to show off the boots and create a clean, intentional silhouette.
```

Run three times on the same item with caching off (`AI201_CACHE=0`), so each try is a real model call. `TEMPERATURE` is 0.9. All three captions are different:

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Scored these vintage Levi's 501s on depop for just $38 and I'm obsessed with the wash. Threw them on with my beat-up white sneakers for an effortless weekend errands kind of vibe. Nothing beats a perfectly worn-in pair of denim.

$ AI201_CACHE=0 python -c "...same command..."
Scored these vintage Levi's 501 jeans for just $38 over on depop and they fit like an absolute dream. I kept it super effortless today by pairing the broken-in indigo denim with some crisp white sneakers for that classic 90s running-errands look. Nothing beats finding a perfectly faded pair that's already soft from day one.

$ AI201_CACHE=0 python -c "...same command..."
Scored these classic medium wash Vintage Levi's 501 Jeans for just $38 over on depop and they fit like an absolute dream. I threw them on with my favorite crisp white sneakers for that effortlessly cool, 90s streetwear look that never misses. Honestly, finding denim with this kind of broken-in fade in the wild is always a massive win.

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('   ', load_listings()[0]))"
Can't write a fit card yet: no outfit suggestion was given for Vintage Levi's 501 Jeans — Medium Wash.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
