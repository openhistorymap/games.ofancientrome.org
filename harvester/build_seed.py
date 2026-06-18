"""THE CURATED CORE of games.ofancientrome.org.

A hand-authored table of the board, dice and guessing games of ancient Rome —
the spine the harvester reads. Each entry carries everything the live site and
the JustPlay launcher need: a `boardgame/1.1` pack (a self-contained SVG board +
glyph pieces, so there are **zero binary assets**), the rules, and a curated
historical `context` blurb that the Wikipedia/Wikidata enrichers later augment.

Run `python -m harvester.build_seed` to (re)write `harvester/data/seed.json`.
Everything in `data/` downstream is generated from it.

House rule (shared with the rulers siblings): never fabricate history. The rules
of several of these games are **not recorded** — where we give a playable set we
mark the game `reconstruction: true` and say so plainly in the rules and context.
"""

import base64
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = Path(__file__).resolve().parent / "data" / "seed.json"

# ---------------------------------------------------------------------------
# palette — a scratched-stone / travertine gaming board
# ---------------------------------------------------------------------------
STONE   = "#1b1410"     # backdrop behind the board
FIELD   = "#e7d7b4"     # the board field (travertine / parchment)
FIELD2  = "#dcc8a0"     # secondary field shade
INCISE  = "#7c5a34"     # incised lines
INCISE2 = "#a07a46"     # lighter incision / highlight
ROSETTE = "#b4472e"     # terracotta accent
NODE    = "#5a3f22"     # marked point

ALBUM = "#ece0c8"       # player one — "the bone/white men"
RUBER = "#a8412e"       # player two — terracotta
NIGER = "#2b241c"       # player two (war games) — slate/dark
GOLD  = "#caa05a"


def data_uri(svg):
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + b64


def _svg(w, h, body, bg=FIELD):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" fill="{bg}"/>'
        f'{body}</svg>'
    )


def _frame(w, h, pad=14):
    return (
        f'<rect x="{pad}" y="{pad}" width="{w-2*pad}" height="{h-2*pad}" '
        f'fill="none" stroke="{INCISE}" stroke-width="6"/>'
        f'<rect x="{pad+10}" y="{pad+10}" width="{w-2*pad-20}" height="{h-2*pad-20}" '
        f'fill="none" stroke="{INCISE2}" stroke-width="2"/>'
    )


def board_grid(cols, rows, cell=90):
    """A cols x rows board of incised squares (latrunculorum / scacchiera)."""
    w, h = cols * cell, rows * cell
    body = [_frame(w, h, 0)]
    for c in range(cols + 1):
        x = c * cell
        body.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{INCISE}" stroke-width="3"/>')
    for r in range(rows + 1):
        y = r * cell
        body.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{INCISE}" stroke-width="3"/>')
    # faint diagonal hatching on a couple of cells gives the "scratched stone" feel
    return {"image": data_uri(_svg(w, h, "".join(body))), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": round(0.82 / cols, 4)}


def board_points(per_side=12):
    """A backgammon-style board of 24 elongated points in two tables (tabula)."""
    w, h = 1320, 760
    pad, bar = 30, 60
    half = (w - 2 * pad - bar) / 2
    pw = half / 6
    ph = 250
    body = [f'<rect x="{pad}" y="{pad}" width="{w-2*pad}" height="{h-2*pad}" fill="{FIELD}" stroke="{INCISE}" stroke-width="6"/>']
    body.append(f'<rect x="{w/2-bar/2}" y="{pad}" width="{bar}" height="{h-2*pad}" fill="{FIELD2}" stroke="{INCISE}" stroke-width="4"/>')

    def point(px, top, idx):
        col = ROSETTE if idx % 2 == 0 else NIGER
        if top:
            return f'<polygon points="{px},{pad+6} {px+pw},{pad+6} {px+pw/2},{pad+6+ph}" fill="{col}" opacity="0.78"/>'
        return f'<polygon points="{px},{h-pad-6} {px+pw},{h-pad-6} {px+pw/2},{h-pad-6-ph}" fill="{col}" opacity="0.78"/>'

    for i in range(6):
        lx = pad + i * pw
        rx = pad + half + bar + i * pw
        body.append(point(lx, True, i))
        body.append(point(rx, True, i + 6))
        body.append(point(lx, False, i))
        body.append(point(rx, False, i + 6))
    return {"image": data_uri(_svg(w, h, "".join(body))), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": 0.038}


def board_scripta():
    """Three lines of twelve markers, split by a central rosette (XII scripta)."""
    cols, rows = 12, 3
    cell = 100
    w, h = cols * cell, rows * cell + 40
    body = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="{FIELD}" stroke="{INCISE}" stroke-width="6"/>']
    for r in range(rows):
        cy = 20 + r * cell + cell / 2
        for c in range(cols):
            cx = c * cell + cell / 2
            # the famous six-letter-word boards: a roundel at each station
            body.append(f'<circle cx="{cx}" cy="{cy}" r="26" fill="none" stroke="{INCISE}" stroke-width="3"/>')
            body.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{NODE}"/>')
    # central rosette dividing the middle row into two sixes
    body.append(f'<circle cx="{w/2}" cy="{20+cell+cell/2}" r="34" fill="{ROSETTE}" opacity="0.85"/>')
    body.append(f'<circle cx="{w/2}" cy="{20+cell+cell/2}" r="16" fill="{FIELD}"/>')
    return {"image": data_uri(_svg(w, h, "".join(body))), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": 0.05}


def board_morris():
    """Three men's morris: a 3x3 lattice of points joined by rows, columns, diagonals."""
    s = 600
    pad = 90
    g = (s - 2 * pad) / 2
    pts = [(pad + c * g, pad + r * g) for r in range(3) for c in range(3)]
    lines = []
    for r in range(3):
        lines.append((pts[r * 3], pts[r * 3 + 2]))      # rows
    for c in range(3):
        lines.append((pts[c], pts[c + 6]))              # cols
    lines.append((pts[0], pts[8]))                       # diagonals
    lines.append((pts[2], pts[6]))
    body = [_frame(s, s, 24)]
    for a, b in lines:
        body.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{INCISE}" stroke-width="4"/>')
    for (x, y) in pts:
        body.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{NODE}"/>')
    return {"image": data_uri(_svg(s, s, "".join(body))), "aspect": 1.0,
            "color": STONE, "pieceSize": 0.12}, pts, s


def board_wheel():
    """Rota — a wheel of eight rim points + a hub, joined by four spokes."""
    s = 600
    cx = cy = s / 2
    R = 230
    import math
    rim = []
    for k in range(8):
        a = math.pi / 2 + k * math.pi / 4          # start at top, clockwise
        rim.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    body = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INCISE}" stroke-width="5"/>']
    for k in range(4):                              # four diameters -> eight spokes
        a, b = rim[k], rim[k + 4]
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{INCISE}" stroke-width="4"/>')
    nodes = rim + [(cx, cy)]
    for (x, y) in nodes:
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="{NODE}"/>')
    return {"image": data_uri(_svg(s, s, "".join(body))), "aspect": 1.0,
            "color": STONE, "pieceSize": 0.11}, nodes, s


def board_delta():
    """A triangular (delta) tabula lusoria diagram — game unrecorded (reconstruction)."""
    w, h = 620, 560
    A, B, C = (310, 40), (40, 520), (580, 520)
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    mAB, mBC, mCA = mid(A, B), mid(B, C), mid(C, A)
    cen = ((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3)
    body = []
    body.append(f'<polygon points="{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]}" fill="none" stroke="{INCISE}" stroke-width="5"/>')
    for v, m in ((A, mBC), (B, mCA), (C, mAB)):     # medians through the centre
        body.append(f'<line x1="{v[0]}" y1="{v[1]}" x2="{m[0]:.1f}" y2="{m[1]:.1f}" stroke="{INCISE}" stroke-width="3"/>')
    nodes = [A, B, C, mAB, mBC, mCA, cen]
    for (x, y) in nodes:
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{NODE}"/>')
    return {"image": data_uri(_svg(w, h, "".join(body))), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": 0.1}, nodes, (w, h)


def board_table(word="ALEA"):
    """A bare gaming table for the dice / guessing games — a parchment field."""
    w, h = 900, 620
    body = [_frame(w, h, 22)]
    body.append(f'<ellipse cx="{w/2}" cy="{h/2}" rx="250" ry="160" fill="none" stroke="{INCISE2}" stroke-width="3" opacity="0.5"/>')
    body.append(
        f'<text x="{w/2}" y="{h/2+22}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="92" letter-spacing="14" '
        f'fill="{INCISE}" opacity="0.22">{word}</text>'
    )
    return {"image": data_uri(_svg(w, h, "".join(body))), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": 0.06}


# ---------------------------------------------------------------------------
# helpers for piece supplies / setups
# ---------------------------------------------------------------------------
def nodes_to_norm(nodes, w, h):
    return [(round(x / w, 4), round(y / h, 4)) for (x, y) in nodes]


def disc(t, label, fill):
    return {"type": t, "label": label, "glyph": "", "bg": fill}


def row(t, n, y, x0=0.12, x1=0.88):
    step = (x1 - x0) / max(1, n - 1)
    return [{"type": t, "x": round(x0 + i * step, 4), "y": y} for i in range(n)]


# ---------------------------------------------------------------------------
# categories (ordered; each carries a pigment used by the frontend)
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"key": "war",       "label": "War & hunt",     "pigment": "#7a8a3a",
     "note": "Games of capture and position — soldiers on a grid."},
    {"key": "race",      "label": "Race & tables",  "pigment": "#b4472e",
     "note": "Dice-driven race games — the tabula family, ancestors of backgammon."},
    {"key": "alignment", "label": "Alignment",      "pigment": "#3a6ea5",
     "note": "Three-in-a-row games scratched on steps and pavements across the empire."},
    {"key": "dice",      "label": "Dice & lots",    "pigment": "#caa05a",
     "note": "Gambling with knucklebones and cubic dice — alea."},
    {"key": "guessing",  "label": "Hand & guess",   "pigment": "#8a5a8a",
     "note": "Quick wagering games of the hand needing nothing but nimble fingers."},
]

OHM_FOOTER = "Made with <3 in Bologna by OpenHistoryMap"


# ---------------------------------------------------------------------------
# pre-built boards that also hand back their node coordinates
# ---------------------------------------------------------------------------
_morris, _morris_pts, _ms = board_morris()
_wheel, _wheel_pts, _ws = board_wheel()
_delta, _delta_pts, _dsz = board_delta()


# ---------------------------------------------------------------------------
# THE ROSTER
# ---------------------------------------------------------------------------
GAMES = [
    # =================================================================== 1
    {
        "id": "latrunculi", "name": "Ludus latrunculorum",
        "latin": "Ludus latrunculorum", "aka": ["Latrunculi", "Latrones", "The game of little soldiers"],
        "category": "war", "players": "2", "duration": "20–40 min",
        "wp": "Ludus latrunculorum", "reconstruction": True,
        "tagline": "Rome's game of soldiers — surround and capture on a grid of squares.",
        "rules": {
            "objective": "Capture your opponent's soldiers by trapping them, and corner their commander.",
            "setup": "Each player takes a row of soldiers (the latrones) of one colour plus a single commander (the dux). Boards of many sizes survive — 8×8, 8×12, 9×10; this pack uses 12×8. Lay your soldiers along your back two rows.",
            "howToPlay": [
                "Players alternate, moving one piece per turn.",
                "A soldier moves any number of empty squares straight along a rank or file (like a rook) — not diagonally.",
                "Capture by custodia: bracket a single enemy soldier between two of yours on opposite sides (along a line). The bracketed soldier is removed.",
                "Moving your own piece *into* a gap between two enemies is safe — you are only captured when the enemy closes the bracket.",
                "The dux (commander) moves the same way; in the common reconstruction it may also jump an adjacent enemy to an empty square beyond.",
            ],
            "winning": "You win by reducing the enemy until they cannot resist, or by blockading the enemy dux so it cannot move (ad incitas redactus — 'driven to a standstill').",
            "variants": [
                "Board size is a house choice — the smaller the board, the sharper the game.",
                "Play without a dux for a pure surround-capture game.",
            ],
        },
        "context": {
            "period": "Roman Republic & Empire, c. 2nd c. BCE – 4th c. CE",
            "blurb": (
                "Ludus latrunculorum — 'the game of little robbers/soldiers' — was Rome's "
                "game of military skill, praised by Varro, Ovid, Martial and the poet of the "
                "Laus Pisonis as a contest of strategy without luck. Soldiers (latrones or "
                "milites) were captured by being flanked on two sides. The exact rules were "
                "never written down: what is played today is a careful modern reconstruction "
                "(notably by Ulrich Schädler and R. C. Bell) from scattered literary hints and "
                "surviving boards. Treat the moves below as one well-argued reading, not gospel."
            ),
            "sources": [
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
                "Schädler, U. (1994). Latrunculi — ein verlorenes strategisches Brettspiel der Römer.",
                "Austin, R. G. (1934). 'Roman Board Games.' Greece & Rome 4(11).",
            ],
        },
        "board": board_grid(12, 8),
        "pieces": [
            disc("rome", "Roman soldier", ALBUM),
            disc("host", "Opposing soldier", NIGER),
            {"type": "dux-r", "label": "Roman dux", "glyph": "✪", "color": ROSETTE, "bg": ALBUM},
            {"type": "dux-h", "label": "Opposing dux", "glyph": "✪", "color": GOLD, "bg": NIGER},
        ],
        "setup": (
            row("rome", 12, 0.94) + row("rome", 11, 0.81, 0.16, 0.84)
            + row("host", 12, 0.06) + row("host", 11, 0.19, 0.16, 0.84)
            + [{"type": "dux-r", "x": 0.5, "y": 0.94}, {"type": "dux-h", "x": 0.5, "y": 0.06}]
        ),
        "turns": {"players": ["Roma", "Hostes"], "track": True},
    },
    # =================================================================== 2
    {
        "id": "tabula", "name": "Tabula",
        "latin": "Tabula", "aka": ["Alea"],
        "category": "race", "players": "2", "duration": "15–30 min",
        "wp": "Tabula (game)", "reconstruction": False,
        "tagline": "The direct ancestor of backgammon — race fifteen men home on three dice.",
        "rules": {
            "objective": "Be the first to move all fifteen of your men around the board and bear them all off.",
            "setup": "A board of twenty-four points in two tables. Each player has fifteen men, entered at the start point and travelling the same direction around the board. Use 'Load sample layout' to line up the two armies.",
            "howToPlay": [
                "Roll the three dice (tesserae). Move men forward by each die value — three separate moves, one per die.",
                "More than one of your own men may share (and so hold) a point.",
                "A point held by two or more enemy men is blocked; you cannot land there.",
                "Land a single man alone on a point and an arriving enemy can hit it — the hit man goes back to re-enter.",
                "Once all your men are in the final table, you may bear them off.",
            ],
            "winning": "The first player to bear off all fifteen men wins. The emperor Zeno is recorded losing a famously bad throw mid-game in 480 CE.",
            "variants": [
                "Two dice instead of three for a faster, backgammon-like game.",
                "Agree whether a man may be borne off on an exact roll only.",
            ],
        },
        "context": {
            "period": "Later Roman Empire, c. 1st–6th c. CE",
            "blurb": (
                "Tabula ('the board') is the immediate ancestor of backgammon: two players, "
                "fifteen men each, three six-sided dice, racing around twenty-four points. We "
                "know it unusually well because of a single game — an epigram in the Greek "
                "Anthology records the exact disastrous throw the emperor Zeno made around "
                "480 CE, point by point, the best-attested individual game from antiquity."
            ),
            "sources": [
                "Austin, R. G. (1934). 'Zeno's Game of τάβλη.' Journal of Hellenic Studies 54.",
                "Becq de Fouquières, L. (1873). Les Jeux des Anciens.",
            ],
        },
        "board": board_points(),
        "pieces": [disc("w", "Albus (white)", ALBUM), disc("b", "Ruber (red)", RUBER)],
        "setup": row("w", 15, 0.9, 0.06, 0.45) + row("b", 15, 0.1, 0.55, 0.94),
        "dice": [{"id": "tesserae", "label": "Tesserae", "glyph": "🎲", "sides": 6, "count": 3}],
        "turns": {"players": ["Albus", "Ruber"], "track": True},
    },
    # =================================================================== 3
    {
        "id": "duodecim-scripta", "name": "Duodecim Scripta",
        "latin": "Ludus duodecim scriptorum", "aka": ["XII scripta", "Twelve lines"],
        "category": "race", "players": "2", "duration": "20–35 min",
        "wp": "Ludus duodecim scriptorum", "reconstruction": True,
        "tagline": "Three lines of twelve — the older race game whose boards were carved as word-puzzles.",
        "rules": {
            "objective": "Race your fifteen men along the three lines of twelve points and off the board before your opponent.",
            "setup": "A board of three rows of twelve markers, the middle row split by a central ornament. Each player has fifteen men and three dice. The precise path each player follows is debated — agree it before you start.",
            "howToPlay": [
                "Roll three dice and advance men by the values, as in tabula.",
                "Men travel along the three lines in a fixed serpentine path (commonly: along the middle row outward, then up and back along the outer rows).",
                "Hold points with two or more men; a lone man can be sent back.",
                "Bear men off once they reach the end of the track.",
            ],
            "winning": "First to bear off all fifteen men wins.",
            "variants": [
                "Many surviving boards spell out a six-letter × six-word verse (e.g. 'VIRTVS / IMPERI / …'); pick a word board for flavour.",
                "Play the simpler tabula path if the three-line route is disputed at your table.",
            ],
        },
        "context": {
            "period": "Roman Republic & early Empire, c. 1st c. BCE – 3rd c. CE",
            "blurb": (
                "Duodecim scripta — 'twelve markings' — is the older cousin of tabula, played "
                "on three lines of twelve points. Dozens of its boards survive carved into the "
                "steps of the Basilica Julia, temple pavements and tavern tables, many of them "
                "inscribed as six-letter-by-six-word puzzles (tabulae lusoriae) such as "
                "'LEVATE / DALOCV / LVDERE / NESCIS / IDIOTA / RECEDE' — 'Get up, clear off, "
                "you don't know how to play, you fool, go away.' The exact track is reconstructed."
            ),
            "sources": [
                "Ferrua, A. (2001). Tavole lusorie epigrafiche.",
                "Purcell, N. (1995). 'Literate Games: Roman Urban Society and the Game of Alea.' Past & Present 147.",
            ],
        },
        "board": board_scripta(),
        "pieces": [disc("w", "Albus (white)", ALBUM), disc("b", "Ruber (red)", RUBER)],
        "setup": row("w", 12, 0.83) + row("w", 3, 0.83, 0.12, 0.3) + row("b", 12, 0.17) + row("b", 3, 0.17, 0.7, 0.88),
        "dice": [{"id": "tesserae", "label": "Tesserae", "glyph": "🎲", "sides": 6, "count": 3}],
        "turns": {"players": ["Albus", "Ruber"], "track": True},
    },
    # =================================================================== 4
    {
        "id": "terni-lapilli", "name": "Terni Lapilli",
        "latin": "Terni lapilli", "aka": ["Three men's morris", "Roman three-in-a-row"],
        "category": "alignment", "players": "2", "duration": "5 min",
        "wp": "Three men's morris", "reconstruction": False,
        "tagline": "Rome's three-in-a-row, scratched on a thousand steps and pavements.",
        "rules": {
            "objective": "Make a straight line of your three pieces along any row, column or diagonal.",
            "setup": "An empty board of nine points. Each player has three pieces. Drag them from the tray.",
            "howToPlay": [
                "Take turns placing one of your three pieces on any empty point.",
                "When all six pieces are down, take turns moving one piece along a line to an adjacent empty point.",
                "Keep manoeuvring until someone lines up three.",
            ],
            "winning": "Three of your pieces in a straight line wins at once.",
            "variants": [
                "Allow a piece to move to any empty point (not only adjacent) for a faster game.",
                "Forbid re-making the same mill twice in a row to avoid stalemates.",
            ],
        },
        "context": {
            "period": "Roman Empire, ubiquitous 1st–5th c. CE",
            "blurb": (
                "Terni lapilli — 'three little stones' — is Rome's version of three men's "
                "morris, mentioned by Ovid in the Ars Amatoria as a game a fashionable woman "
                "should know. Its boards are among the commonest Roman graffiti: scratched into "
                "the steps of the Forum, the Basilica Julia and pavements all over the empire, "
                "wherever people waited and wanted a quick game with three pebbles each."
            ),
            "sources": [
                "Ovid, Ars Amatoria III.365–366.",
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
            ],
        },
        "board": _morris,
        "pieces": [disc("a", "Album (bone)", ALBUM), disc("r", "Ruber (terracotta)", RUBER)],
        "setup": [],
        "turns": {"players": ["Album", "Ruber"], "track": True},
        "_nodes": nodes_to_norm(_morris_pts, _ms, _ms),
    },
    # =================================================================== 5
    {
        "id": "tali", "name": "Tali",
        "latin": "Tali", "aka": ["Astragali", "Knucklebones"],
        "category": "dice", "players": "2+", "duration": "10 min",
        "wp": "Astragalus (game)", "reconstruction": False,
        "tagline": "Four knucklebones, four faces — throw for the Venus and avoid the Dog.",
        "rules": {
            "objective": "Throw the best combination of the four tali — and win the stakes.",
            "setup": "Four tali (sheep or goat knucklebones). Each lands on one of four faces, valued 1, 3, 4 and 6 (the two narrow ends never settle). Put up a wager of denarii.",
            "howToPlay": [
                "Each player in turn throws all four tali, from the hand or a fritillus (dice-cup).",
                "Read the four faces. Special throws beat any plain total.",
                "The Venus (iactus Venereus) — all four faces different (1·3·4·6) — is the best throw of all.",
                "The Dog (canis) — all four showing 1 — is the worst.",
                "Otherwise the higher pip total wins the round.",
            ],
            "winning": "Best throw takes the pot; play to an agreed number of rounds or until the stakes run out.",
            "variants": [
                "Children played a skill version (like jacks): toss and catch the bones on the back of the hand.",
                "Many house scales of named throws existed — agree yours before betting.",
            ],
        },
        "context": {
            "period": "Greek & Roman, archaic through late antiquity",
            "blurb": (
                "Tali (Greek astragaloi) were knucklebones — the small ankle bones of sheep or "
                "goats — used as four-sided dice. Their faces counted 1, 3, 4 and 6; the throw "
                "of four different faces was the 'Venus', the luckiest, while four ones was the "
                "'Dog'. Augustus mentions losing happily at tali in a letter quoted by Suetonius. "
                "Bronze, glass and crystal tali survive, and children played a skill game of "
                "toss-and-catch with the same bones."
            ),
            "sources": [
                "Suetonius, Divus Augustus 71.",
                "Becq de Fouquières, L. (1873). Les Jeux des Anciens.",
            ],
        },
        "board": board_table("VENVS"),
        "pieces": [{"type": "stake", "label": "Denarius (stake)", "glyph": "✸", "color": GOLD, "bg": "#3a2c1a"}],
        "setup": [],
        "dice": [{"id": "tali", "label": "Tali", "glyph": "🦴", "count": 4,
                  "faces": [{"label": "I", "value": 1}, {"label": "III", "value": 3},
                            {"label": "IV", "value": 4}, {"label": "VI", "value": 6}]}],
        "turns": {"track": True},
    },
    # =================================================================== 6
    {
        "id": "tesserae", "name": "Tesserae",
        "latin": "Tesserae", "aka": ["Cubic dice", "Alea"],
        "category": "dice", "players": "2+", "duration": "10 min",
        "wp": "Dice", "reconstruction": False,
        "tagline": "Three cubic dice and a cup — 'the die is cast'.",
        "rules": {
            "objective": "Throw the highest with three six-sided dice and take the stakes.",
            "setup": "Three tesserae (cubic dice), ideally thrown from a fritillus (dice-tower / cup) to stop cheating. Each player puts up a stake.",
            "howToPlay": [
                "Players throw the three dice in turn.",
                "Compare totals — and watch for named throws: three sixes (the best) or three ones (the worst).",
                "Settle the wager on each round.",
            ],
            "winning": "Highest throw wins the pot. Gambling with dice was technically illegal except at the Saturnalia — which never stopped anyone.",
            "variants": [
                "Add the Venus/Dog conventions from tali for named winning and losing throws.",
                "Play 'highest of three throws' to smooth out the luck.",
            ],
        },
        "context": {
            "period": "Roman Republic & Empire",
            "blurb": (
                "Tesserae were ordinary cubic dice, marked one to six with the one and six on "
                "opposite faces just as today. Romans gambled with them constantly despite laws "
                "(the lex alearia) banning dice except during the Saturnalia, and threw them "
                "from a fritillus, a ridged cup, to foil sharps. Caesar's 'alea iacta est' — "
                "'the die is cast' — at the Rubicon is the most famous dice throw in history."
            ),
            "sources": [
                "Suetonius, Divus Iulius 32 (alea iacta est).",
                "Horace, Odes III.24; Cicero, Philippics II.",
            ],
        },
        "board": board_table("ALEA"),
        "pieces": [{"type": "stake", "label": "Denarius (stake)", "glyph": "✸", "color": GOLD, "bg": "#3a2c1a"}],
        "setup": [],
        "dice": [{"id": "tesserae", "label": "Tesserae", "glyph": "🎲", "sides": 6, "count": 3}],
        "turns": {"track": True},
    },
    # =================================================================== 7
    {
        "id": "rota", "name": "Rota",
        "latin": "Rota", "aka": ["The wheel", "Roman round merels"],
        "category": "alignment", "players": "2", "duration": "5 min",
        "wp": "Rota (game)", "reconstruction": True,
        "tagline": "A wheel of eight spokes — the round cousin of three-in-a-row.",
        "rules": {
            "objective": "Line up your three pieces through the hub of the wheel.",
            "setup": "A wheel with eight points on the rim and one at the centre, joined by spokes. Each player has three pieces.",
            "howToPlay": [
                "Take turns placing your three pieces on empty points.",
                "Then take turns sliding a piece along a line (spoke or rim) to the next empty point.",
                "A line of three must pass through the central hub to count.",
            ],
            "winning": "Three in a row through the centre wins.",
            "variants": [
                "Only the player who moves second may occupy the centre first — a common handicap to balance the strong opening.",
            ],
        },
        "context": {
            "period": "Roman Empire, late antiquity",
            "blurb": (
                "Rota — Latin for 'wheel' — is a circular three-in-a-row game known from "
                "wheel-shaped boards scratched in Roman pavements, including at Ostia and in "
                "the forum at Rome. Eight rim points and a central hub make it a round relative "
                "of terni lapilli. As with most of these scratched games no rulebook survives, "
                "so the moves here are a sensible modern reconstruction."
            ),
            "sources": [
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
            ],
        },
        "board": _wheel,
        "pieces": [disc("a", "Album (bone)", ALBUM), disc("r", "Ruber (terracotta)", RUBER)],
        "setup": [],
        "turns": {"players": ["Album", "Ruber"], "track": True},
        "_nodes": nodes_to_norm(_wheel_pts, _ws, _ws),
    },
    # =================================================================== 8
    {
        "id": "par-impar", "name": "Par Impar",
        "latin": "Par impar ludere", "aka": ["Odds and evens"],
        "category": "guessing", "players": "2", "duration": "2 min",
        "wp": "Odds and evens (hand game)", "reconstruction": False,
        "tagline": "Odd or even? A fistful of nuts and a guess — the simplest Roman wager.",
        "rules": {
            "objective": "Guess whether the hidden number of counters is odd or even.",
            "setup": "A handful of small counters — nuts, knucklebones or coins. One player is the hider.",
            "howToPlay": [
                "The hider conceals some counters in a closed fist.",
                "The guesser calls 'par!' (even) or 'impar!' (odd).",
                "Open the hand and count.",
                "A correct guess wins the counters (or the agreed stake); a wrong guess loses the stake. Swap roles and repeat.",
            ],
            "winning": "Play to an agreed pot or number of rounds; the richer hand wins.",
            "variants": [
                "Guess the exact number for a bigger payout.",
                "Roman children played it with walnuts — losing your nuts meant losing the game (and 'relinquere nuces', to give up nuts, meant to put away childish things).",
            ],
        },
        "context": {
            "period": "Roman, all periods — a children's and tavern game",
            "blurb": (
                "Par impar ludere — 'to play odds and evens' — needed nothing but a hand and a "
                "few nuts or coins. One player hid a number of counters in a fist and the other "
                "guessed odd or even. Suetonius lists it among the emperor Augustus' easy "
                "amusements, and it appears on wall paintings and in children's games with "
                "walnuts. It is the most minimal of all Roman games — pure luck and a quick wager."
            ),
            "sources": [
                "Suetonius, Divus Augustus 71.",
                "Nuts: Ovid, Nux; Martial, Epigrams V.84.",
            ],
        },
        "board": board_table("PAR · IMPAR"),
        "pieces": [
            {"type": "nut", "label": "Nut (counter)", "glyph": "🌰"},
            {"type": "fist", "label": "Closed fist", "glyph": "✊"},
            {"type": "coin", "label": "As (coin)", "glyph": "✸", "color": GOLD, "bg": "#3a2c1a"},
        ],
        "setup": [],
        "turns": {"players": ["Celator (hider)", "Coniector (guesser)"], "track": True},
    },
    # =================================================================== 9
    {
        "id": "delta", "name": "Delta",
        "latin": "Tabula in formam deltae", "aka": ["The delta board", "Triangular tabula lusoria"],
        "category": "alignment", "players": "2", "duration": "10 min",
        "wp": "Tabula lusoria", "reconstruction": True,
        "tagline": "A triangular game-diagram from Roman stone — its rules unrecorded, here reconstructed.",
        "rules": {
            "objective": "Be first to line up your three pieces along a full side or median of the delta.",
            "setup": "A triangular (delta) diagram of seven points: three corners, three edge-midpoints and the centre, joined by the three sides and three medians. Each player has three pieces.",
            "howToPlay": [
                "Take turns placing your three pieces on empty points.",
                "Then take turns sliding a piece along a drawn line to the next empty point.",
                "Aim to occupy three points that all lie on one straight line of the figure.",
            ],
            "winning": "Three of your pieces on a single side or median wins.",
            "variants": [
                "Treat it as a small race instead: enter at a corner and run a piece to the opposite midpoint on dice throws.",
            ],
        },
        "context": {
            "period": "Roman, imperial — board attested, game lost",
            "blurb": (
                "Among the tabulae lusoriae — gaming diagrams carved into Roman steps and "
                "pavements — are circular, square and triangular figures. The triangular "
                "'delta' board is real and recurring, but unlike tabula or terni lapilli no "
                "ancient source tells us how it was played. Everything below is an explicit "
                "modern reconstruction offered so the board can be enjoyed; it is a plausible "
                "game in the Roman idiom, not a recovered one. We flag it honestly as such."
            ),
            "sources": [
                "Ferrua, A. (2001). Tavole lusorie epigrafiche.",
                "Purcell, N. (1995). 'Literate Games.' Past & Present 147.",
            ],
        },
        "board": _delta,
        "pieces": [disc("a", "Album (bone)", ALBUM), disc("r", "Ruber (terracotta)", RUBER)],
        "setup": [],
        "turns": {"players": ["Album", "Ruber"], "track": True},
        "_nodes": nodes_to_norm(_delta_pts, _dsz[0], _dsz[1]),
    },
]


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------
def curated_records():
    out = []
    cat_labels = {c["key"]: c["label"] for c in CATEGORIES}
    for g in GAMES:
        rec = dict(g)
        rec["category_label"] = cat_labels.get(g["category"], g["category"])
        # mirror players/duration into the rules block (the launcher reads rules.*)
        rules = dict(rec["rules"])
        rules.setdefault("players", rec.get("players", ""))
        rules.setdefault("duration", rec.get("duration", ""))
        rec["rules"] = rules
        out.append(rec)
    return out


def finalize():
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "title": "Games of Ancient Rome",
        "categories": CATEGORIES,
        "footer": OHM_FOOTER,
        "games": curated_records(),
    }


def write_seed():
    SEED.parent.mkdir(parents=True, exist_ok=True)
    data = finalize()
    SEED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {SEED.relative_to(ROOT)} — {len(data['games'])} games, "
          f"{len(data['categories'])} categories")
    # a quick contemporaneity / sanity print
    for g in data["games"]:
        flag = " [reconstruction]" if g.get("reconstruction") else ""
        print(f"  · {g['id']:<18} {g['category']:<9} {g['name']}{flag}")
    return data


if __name__ == "__main__":
    write_seed()
