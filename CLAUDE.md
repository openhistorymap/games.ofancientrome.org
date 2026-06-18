# games.ofancientrome.org

A catalogue of the **games of ancient Rome** — the board, dice and guessing games
Romans actually played — each with its rules, its history, and a **live shared
table you can play with friends**. Move the meridian on the rulers sites to see
*who* held power; come here to do what they did when the senate was dull: play
latrunculi, race fifteen men on three dice, scratch three pebbles in a row.

Sibling, in machinery and house style, to **`rulers.ofancientrome.org`** (ROAR)
and **`rulers.ofthepast.org`**: the same *curated-seed → harvester → static-data →
GitHub-Pages* shape, the same OHM footer, the same "never fabricate history"
discipline. Where the rulers sites are a gallery of faces, this is a **shelf of
boards**; where they speak to an avatar, here you **open a real table**.

## How it fits together (two repos)

1. **This repo** is the catalogue + the data. The harvester turns a hand-authored
   roster into machine-owned `data/`: a compact index, a per-game detail record,
   and — the key artefact — a **`boardgame/1.1` pack** per game under
   `data/packs/<id>.json`.
2. **The launcher** is `JustPlayBo/whitechapel` (the JustPlay shared-board engine,
   working tree at `/srv/justplay-sy`). Each game's **▶ Play with friends** button
   deep-links into it:
   `https://justplaybo.github.io/whitechapel/?game=<absolute pack URL>&room=<code>`.
   The launcher fetches the pack (GitHub Pages serves it CORS-`*`), renders the
   board + pieces, and syncs moves over MQTT. Because the pack carries `rules`,
   `context`, `dice` and `turns`, players land at the table already knowing **how
   to play and what the game is** — a rules drawer, a synced dice roller and a
   "whose turn" chip travel with the pack.

The `boardgame/1.1` blocks (`rules`/`context`/`dice`/`turns`) were added to the
engine for this site — see `/srv/justplay-sy/packs/SCHEMA.md`. They are additive:
old packs are unaffected, and the engine still enforces nothing.

## Scope (decided up front)

- **Nine well-attested games**, the core playable set: `latrunculi`, `tabula`,
  `duodecim-scripta`, `terni-lapilli`, `tali`, `tesserae`, `rota`, `par-impar`,
  `delta`, grouped into five categories (war/hunt, race/tables, alignment,
  dice/lots, hand/guess).
- **Honesty about lost rules.** Several of these games' rules were never written
  down. Where we give a playable set for a game whose rules are unrecorded, the
  game is flagged `reconstruction: true`; the frontend shows a banner and the
  rules say so plainly. **Never present a reconstruction as recovered fact.**
- **Zero binary assets.** Every board is a self-contained inline **SVG**
  (generated in `build_seed.py`, embedded as a `data:` URI in the pack); every
  piece is a unicode/emoji glyph or a coloured chip. The repo ships no images.
- **Curated text is authoritative.** The blurb, rules and sources are
  hand-written; the Wikipedia/Wikidata enrichers only *add* (an illustration, an
  encyclopedic extract, external links). They never overwrite curated content.

## Layout

```
harvester/        Python pipeline (stdlib only for the offline path).
  build_seed.py   THE CURATED CORE — the nine games, their boardgame/1.1 packs
                  (SVG board generators + glyph pieces), rules, and history.
                  `python -m harvester.build_seed` writes harvester/data/seed.json.
  wikipedia.py    MediaWiki client: lead extract, lead image, page URL (lazy `requests`).
  wikidata.py     wbgetentities client: QID + P18 image fallback (lazy `requests`).
  harvest.py      orchestrator -> data/ (packs, details, index, manifest).
  sources/
    base.py       the Enricher contract (run(games, ctx) -> status; failures isolated).
    seed.py       loads the spine (not an enricher).
    wikipedia_enrich.py   illustration + encyclopedic extract + Wikipedia link.
    wikidata_enrich.py    QID + image fallback + Wikidata link.
  data/seed.json  the canonical spine the harvester reads (committed).
web/              static frontend (no build step, relative paths only).
  index.html  style.css  app.js
data/             GENERATED, machine-owned. Committed; published by Deploy.
  games.json             compact index for the catalogue grid (+ board thumbnails)
  games/<id>.json        full per-game detail (rules, context, pack, pieces)
  packs/<id>.json        the boardgame/1.1 pack the JustPlay launcher loads
  manifest.json          totals, categories, per-source status, launcher base, footer
.github/workflows/  harvest.yml + deploy.yml (two independent manual workflows)
CNAME             games.ofancientrome.org
```

## The harvester

Spine-then-enrich, identical machinery to the rulers siblings. `harvest.py` loads
the **spine** (`seed.json`, built by `build_seed.py`) and runs each **Enricher** in
`sources.REGISTRY` over the shared games list, in isolation: a failing enricher is
recorded `stale` in the manifest and the spine + the other enrichers survive.

- **Offline build (no network):** `GAMES_DISABLE=wikipedia,wikidata python -m
  harvester` — produces a complete `data/` from the curated content alone. This is
  how the committed `data/` is cut; the site is fully functional without ever
  hitting the network.
- **Full build (network):** `python -m harvester` — additionally fetches an
  illustration, an encyclopedic extract and external links per game.
- Editing the roster = edit `GAMES` / `CATEGORIES` (and the SVG board generators)
  in `build_seed.py`, re-run `python -m harvester.build_seed`, eyeball the printed
  roster, then re-harvest. **Never hand-edit `data/`** — it is machine output.

## Frontend

Plain HTML/CSS/JS, **no build step**, **relative paths only** (custom domain + any
`/staging/` subpath both work). Loads `data/manifest.json` + `data/games.json`,
renders category **lanes** of cards (each card shows the board as a thumbnail),
and lazy-loads `data/games/<id>.json` into a detail overlay on click. The overlay
shows history & context, the rules, the pieces legend and the dice — and the **▶
Play with friends** button that opens the launcher. Theme (light/lapidary vs dark)
persists in `localStorage` (`goar-theme`). Design is the **travertine gaming
table**: incised stone, tessera pigments per category, terracotta-and-bone
counters; Cinzel + Spectral. Full design context in `.impeccable.md`.

## Local preview

`web/` and `data/` are separate trees that Deploy merges. To preview them together:

```bash
GAMES_DISABLE=wikipedia,wikidata python -m harvester      # (re)cut data/
mkdir -p _site/data && cp -r web/. _site/ && cp -r data/. _site/data/
python3 -m http.server -d _site 8799   # open http://localhost:8799
```

`_site/` is git-ignored.

## Deploy

**GitHub Pages**, custom domain via `CNAME`. Two independent **manual** workflows
(same discipline as the rulers and map siblings):

- **Harvest** — rebuild the seed, re-pull `data/` (optionally with enrichers),
  commit to `main`. Does *not* publish.
- **Deploy** — stage `web/` to the root + `data/` to `_site/data/` + `CNAME` →
  Pages (`actions/deploy-pages`). Does *not* harvest. Pages source = "GitHub
  Actions".

Typical: *frontend change → push → Deploy*; *roster change → edit
`build_seed.py` → Harvest → eyeball the manifest → Deploy*.

## House rules

- `data/` is machine-owned harvester output — never hand-edit it.
- The roster lives in `build_seed.py`. That is the one file to edit to add,
  remove, or re-rule a game; everything downstream is generated.
- **Never fabricate history.** Games with lost rules are `reconstruction: true`
  and say so. Cite real sources.
- No hard-coded credentials; this repo holds no keys.
- No tests. Don't claim a change is "tested" because nothing broke at import —
  but you *can* validate packs by normalising them with the launcher's
  `js/gamedef.js` (see `/srv/justplay-sy`).
- The footer always reads "Made with <3 in Bologna by OpenHistoryMap" (OHM line).
- Host runtime is old — run one-off tooling under Docker if the host Python
  chokes (`docker run --rm -v "$PWD":/w -w /w python:3-slim …`).
