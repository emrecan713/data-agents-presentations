"""Draws the SVG illustrations and diagrams in assets/ for this deck.

    python make-figures.py

Each figure is a line drawing made here in one style: black 3 px strokes with round
ends, and fills from a small palette (white, Aalto yellow, light blue). Several redraw
ideas from Emrecan's own talks: the person at a laptop and the thinking researcher
(TUM Think Tank), the role oscillation in one workshop chat, the metaphors and the
asymmetry of consequences (CHI 2026 talk), and the nested responsibility circles
(TUM). Nothing is traced from an image model or copied from the paper's figures.
Labels are real SVG text; alt text and figure descriptions live in the deck's .md.
All output is own work (see assets/CREDITS.md).
"""
import math
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
FONT = "font-family='Arial, Helvetica, sans-serif'"
INK, GREY, LIGHT, PAPER = "#000000", "#5a5a5a", "#e8e8e8", "#ffffff"
YELLOW, SKY = "#f7e159", "#dcecfb"
# darker series colours that keep 3:1 on white; every use is also labelled in text
BLUE, RED, TEAL, OCHRE = "#005a9c", "#a51f39", "#006b61", "#8a5a00"
S = f"stroke='{INK}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'"


def svg(w, h, body):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' {FONT}>\n{body}\n</svg>\n"


def text(x, y, s, size=20, anchor="middle", weight="400", fill=INK, italic=False):
    st = " font-style='italic'" if italic else ""
    return f"<text x='{x:.0f}' y='{y:.0f}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}'{st}>{s}</text>"


def line(*pts, stroke=S, fill="none"):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f"<path d='{d}' fill='{fill}' {stroke}/>"


def arrow(x1, y1, x2, y2, colour=INK, width=3, dash=""):
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 14 * math.cos(a), y2 - 14 * math.sin(a)
    px, py = 7 * math.sin(a), -7 * math.cos(a)
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{hx:.1f}' y2='{hy:.1f}' stroke='{colour}' stroke-width='{width}' stroke-linecap='round'{d}/>"
            f"<path d='M{x2:.1f} {y2:.1f} L{hx + px:.1f} {hy + py:.1f} L{hx - px:.1f} {hy - py:.1f} Z' fill='{colour}'/>")


def bubble(x, y, w, h, tail_x, tail_y, fill=PAPER, lines=2):
    """Rounded speech bubble whose tail points at (tail_x, tail_y) below it."""
    r = 16
    bx = min(max(tail_x, x + r + 16), x + w - r - 16)
    d = (f"M{x + r} {y} H{x + w - r} Q{x + w} {y} {x + w} {y + r} V{y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} "
         f"H{bx + 10} L{tail_x} {tail_y} L{bx - 10} {y + h} H{x + r} Q{x} {y + h} {x} {y + h - r} V{y + r} Q{x} {y} {x + r} {y} Z")
    out = [f"<path d='{d}' fill='{fill}' {S}/>"]
    for i in range(lines):
        ln = (w - 44) * (1 if i < lines - 1 else 0.55)
        out.append(f"<path d='M{x + 22} {y + 22 + i * 16} h{ln:.0f}' stroke='{GREY}' stroke-width='3' stroke-linecap='round'/>")
    return "\n".join(out)


# ------------------------------------------------------------------ the seated researcher
def seated_scene(pose="typing", laptop_lines=True):
    """Chair, person, desk and laptop. The person faces right. Coordinates in a 420x330 frame."""
    p = []
    # chair: back, seat, two legs
    p.append(line((66, 168), (72, 300)))
    p.append(line((62, 240), (136, 240)))
    p.append(line((124, 240), (124, 300)))
    # desk: top and two legs, clear of the person's knees
    p.append(line((196, 210), (384, 210)))
    p.append(line((212, 210), (212, 300)))
    p.append(line((368, 210), (368, 300)))
    # laptop: base on the desk, screen facing the person
    p.append(line((214, 207), (288, 207)))
    p.append(line((288, 207), (310, 140), (360, 140), (338, 207), (288, 207), fill=PAPER))
    if laptop_lines:
        for i, (a, b) in enumerate([(316, 344), (311, 337), (306, 330)]):
            y = 160 + i * 14
            p.append(f"<path d='M{a - i * 2} {y} H{b - i * 2}' stroke='{GREY}' stroke-width='3' stroke-linecap='round'/>")
    # person: spine, thigh, shin and foot (knee stops short of the desk)
    p.append(f"<path d='M110 150 C104 180 100 210 102 238' fill='none' {S}/>")
    p.append(line((102, 238), (176, 238), (178, 296), (194, 296)))
    # head and a small fringe of hair
    p.append(f"<circle cx='112' cy='128' r='21' fill='{PAPER}' {S}/>")
    p.append(f"<path d='M92 122 C96 104 122 100 132 116' fill='none' {S}/>")
    if pose == "typing":
        p.append(line((106, 168), (160, 196), (222, 204)))
    else:  # one arm folded up, hand to the chin
        p.append(line((107, 170), (154, 202), (134, 152)))
    return p


def person_laptop():
    p = seated_scene("typing")
    p.append(bubble(24, 22, 176, 62, 104, 100, fill=SKY))
    p.append(bubble(232, 30, 164, 62, 318, 128, fill=YELLOW))
    return svg(420, 320, "\n".join(p))


def thinking_person():
    p = seated_scene("thinking", laptop_lines=False)
    p.append(text(160, 84, "?", 52, weight="700"))
    p.append(text(196, 58, "?", 36, weight="700", fill=GREY))
    return svg(420, 320, "\n".join(p))


# ------------------------------------------------------------------ relationships moving in one chat
LANES = [("Directing", "Director"), ("Correcting", "Trainer"), ("Collaborating", "Partner"), ("Deferring", "Student")]
TINTS = ["#fbe3e3", "#fbf1d0", "#ece4f6", "#e1edf8"]


def person_icon(x, y, colour):
    return (f"<circle cx='{x}' cy='{y}' r='17' fill='{PAPER}' stroke='{colour}' stroke-width='3.5'/>"
            f"<circle cx='{x}' cy='{y - 4}' r='5.5' fill='{colour}'/>"
            f"<path d='M{x - 9} {y + 10} Q{x} {y - 2} {x + 9} {y + 10}' fill='{colour}'/>")


def ai_icon(x, y, colour):
    return (f"<rect x='{x - 16}' y='{y - 15}' width='32' height='30' rx='7' fill='{PAPER}' stroke='{colour}' stroke-width='3.5'/>"
            f"<circle cx='{x - 6}' cy='{y}' r='3.5' fill='{colour}'/><circle cx='{x + 6}' cy='{y}' r='3.5' fill='{colour}'/>"
            f"<path d='M{x} {y - 15} V{y - 22}' stroke='{colour}' stroke-width='3' stroke-linecap='round'/>")


def oscillation():
    """Researcher and AI positions, turn by turn, in one workshop chat."""
    w, h = 1180, 510
    left, right, top, lh = 196, 1166, 84, 84
    p = []
    for i, ((verb, role), tint) in enumerate(zip(LANES, TINTS)):
        y = top + i * lh
        p.append(f"<rect x='{left}' y='{y}' width='{right - left}' height='{lh - 8}' rx='10' fill='{tint}'/>")
        p.append(text(left - 16, y + 60, role, 18, anchor="end", fill=GREY))
    mid = lambda lane: top + lane * lh + (lh - 8) / 2
    # one exchange = a researcher turn and the AI reply; positions from the CHI 2026 talk (researcher)
    # and the paper's description of the system's replies (AI)
    human = [0, 2, 1, 2, 1, 3, 2]
    ai = [2, 3, 3, 2, 3, 1, 2]
    step = (right - left - 90) / len(human)
    hx = [left + 50 + k * step for k in range(len(human))]
    ax = [x + step * 0.5 for x in hx]
    p.append(f"<polyline points='{' '.join(f'{x:.0f},{mid(l):.0f}' for x, l in zip(hx, human))}' fill='none' stroke='{TEAL}' stroke-width='5' stroke-linejoin='round'/>")
    p.append(f"<polyline points='{' '.join(f'{x:.0f},{mid(l):.0f}' for x, l in zip(ax, ai))}' fill='none' stroke='{OCHRE}' stroke-width='5' stroke-dasharray='12 9' stroke-linejoin='round'/>")
    for x, l in zip(hx, human):
        p.append(person_icon(x, mid(l), TEAL))
    for x, l in zip(ax, ai):
        p.append(ai_icon(x, mid(l), OCHRE))
    # quotes, placed in free space above the lanes and joined by thin leader lines
    def note(px, py, row_y, s, colour, anchor="middle", above=True):
        # vertical leader from the point to its label row, so leaders never cross
        end = row_y + 8 if above else row_y - 22
        p.append(f"<path d='M{px:.0f} {py:.0f} V{end:.0f}' stroke='{colour}' stroke-width='2' stroke-dasharray='3 4'/>")
        p.append(text(px, row_y, s, 20, anchor=anchor, italic=True))
    bottom = top + 4 * lh
    note(hx[0], mid(0) - 18, 26, "“You are an excellent qualitative researcher …”", TEAL, anchor="start")
    note(hx[1], mid(2) - 18, 58, "“Perception vs. Reality seems not correct”", TEAL, anchor="start")
    note(hx[6], mid(2) - 18, 26, "“I like this idea”", TEAL, anchor="end")
    note(ax[1], mid(3) + 16, bottom + 28, "“You’re absolutely right to challenge that”", OCHRE, anchor="end", above=False)
    note(ax[2], mid(3) + 16, bottom + 58, "“Excellent observation!”", OCHRE, anchor="start", above=False)
    note(ax[6], mid(2) + 16, bottom + 28, "“I am glad to hear that!”", OCHRE, anchor="end", above=False)
    return svg(w, h, "\n".join(p))


def oscillation_legend():
    """Small legend shown beside the chart title."""
    p = [person_icon(22, 24, TEAL), f"<path d='M48 24 h44' stroke='{TEAL}' stroke-width='5'/>", text(102, 31, "Researcher", 22, anchor="start", weight="700"),
         ai_icon(262, 26, OCHRE), f"<path d='M288 24 h44' stroke='{OCHRE}' stroke-width='5' stroke-dasharray='12 9'/>", text(342, 31, "AI system", 22, anchor="start", weight="700")]
    return svg(470, 48, "\n".join(p))


# ------------------------------------------------------------------ metaphors
def cat():
    return svg(220, 200, "\n".join([
        f"<path d='M150 176 C196 176 204 130 178 112' fill='none' {S}/>",
        f"<path d='M72 178 C42 178 46 112 82 102 C94 92 128 92 140 102 C174 112 178 178 148 178 Z' fill='{PAPER}' {S}/>",
        f"<path d='M86 58 L84 24 L108 42 M114 42 L138 24 L136 58' fill='{PAPER}' {S}/>",
        f"<circle cx='111' cy='70' r='34' fill='{PAPER}' {S}/>",
        f"<circle cx='99' cy='66' r='4' fill='{INK}'/><circle cx='123' cy='66' r='4' fill='{INK}'/>",
        f"<path d='M106 78 l5 5 l5 -5' fill='none' stroke='{INK}' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>",
        f"<path d='M70 74 h-22 M72 84 l-22 6 M152 74 h22 M150 84 l22 6' stroke='{INK}' stroke-width='2.5' stroke-linecap='round'/>",
    ]))


def mirror():
    """A hand mirror; what goes in (a speech bubble) comes back reversed."""
    return svg(220, 200, "\n".join([
        f"<ellipse cx='110' cy='80' rx='58' ry='68' fill='{SKY}' {S}/>",
        f"<path d='M110 148 V188 M94 188 H126' fill='none' {S}/>",
        f"<path d='M82 62 H138 Q146 62 146 70 V92 Q146 100 138 100 H104 L94 112 L96 100 H82 Q74 100 74 92 V70 Q74 62 82 62 Z' fill='{PAPER}' stroke='{INK}' stroke-width='2.5' stroke-linejoin='round'/>",
        f"<path d='M86 76 H132 M86 87 H116' stroke='{GREY}' stroke-width='3' stroke-linecap='round'/>",
        f"<path d='M74 34 l14 -10' stroke='{PAPER}' stroke-width='6' stroke-linecap='round'/>",
    ]))


def parrot():
    return svg(220, 200, "\n".join([
        f"<path d='M28 170 H192' fill='none' {S}/>",
        f"<path d='M96 168 L84 196 M112 168 L120 196' fill='none' {S}/>",
        f"<path d='M104 34 C74 34 64 72 70 106 C74 134 90 160 110 168 C130 150 138 116 136 82 C134 52 122 34 104 34 Z' fill='{YELLOW}' {S}/>",
        f"<path d='M134 56 C152 50 166 62 160 82 C154 76 146 74 138 78 Z' fill='{PAPER}' {S}/>",
        f"<circle cx='116' cy='58' r='4.5' fill='{INK}'/>",
        f"<path d='M86 92 C92 118 104 136 120 146' fill='none' {S}/>",
        f"<path d='M164 30 q10 -9 20 0 M170 48 q10 -9 20 0' fill='none' stroke='{GREY}' stroke-width='3' stroke-linecap='round'/>",
    ]))


def depth():
    return svg(220, 200, "\n".join([
        f"<rect x='18' y='58' width='184' height='132' fill='{SKY}'/>",
        f"<path d='M18 58 q23 -14 46 0 t46 0 t46 0 t46 0' fill='none' {S}/>",
        f"<path d='M18 104 H202 M18 148 H202' stroke='{GREY}' stroke-width='3' stroke-dasharray='8 8'/>",
        f"<circle cx='110' cy='30' r='12' fill='{PAPER}' {S}/>",
        arrow(110, 50, 110, 182, INK, 4),
    ]))


def four_frames():
    """Four researchers at their laptops, each with a different picture of AI in mind,
    all connected to the same kind of system below."""
    w, h = 1180, 318
    s, oy = 0.58, 78
    pictures = [cat(), mirror(), parrot(), depth()]
    colours = [TEAL, BLUE, RED, OCHRE]
    p = ["<style>path,circle,line,rect,ellipse,polyline{vector-effect:non-scaling-stroke}</style>"]
    node_x, node_y = 590, 296
    for k, (pic, colour) in enumerate(zip(pictures, colours)):
        ox = 147 + k * 295 - 139
        # line from this researcher's laptop down to the shared system; drawn first so it sits behind
        x0, y0 = ox + 250 * s, oy + 207 * s
        end_x = node_x + (k - 1.5) * 9
        c2x = node_x + (x0 - node_x) * 0.35
        p.append(f"<path d='M{x0:.0f} {y0:.0f} C{x0:.0f} {y0 + 110:.0f} {c2x:.0f} {node_y - 70:.0f} {end_x:.0f} {node_y - 17}' fill='none' stroke='{colour}' stroke-width='4' stroke-linecap='round'/>")
        p.append(f"<g transform='translate({ox:.0f} {oy}) scale({s})'>" + "\n".join(seated_scene("typing")) + "</g>")
        # thought bubble with this researcher's picture of AI
        p.append(f"<rect x='{ox + 8:.0f}' y='4' width='120' height='100' rx='24' fill='{PAPER}' stroke='{colour}' stroke-width='3.5'/>")
        p.append(f"<circle cx='{ox + 56:.0f}' cy='116' r='5' fill='{PAPER}' stroke='{colour}' stroke-width='3'/>")
        p.append(f"<circle cx='{ox + 60:.0f}' cy='128' r='3' fill='{PAPER}' stroke='{colour}' stroke-width='3'/>")
        p.append(pic.replace("<svg xmlns='http://www.w3.org/2000/svg' ", f"<svg x='{ox + 14:.0f}' y='8' width='108' height='92' ", 1))
    p.append(ai_icon(node_x, node_y + 2, INK))
    p.append(text(node_x + 30, node_y + 10, "the same kind of system", 19, anchor="start", fill=GREY))
    return svg(w, h, "\n".join(p))


def icon_no_file():
    return svg(120, 120, "\n".join([
        f"<path d='M32 14 H72 L90 32 V106 H32 Z' fill='{PAPER}' {S} stroke-dasharray='8 7'/>",
        text(61, 80, "?", 44, weight="700")]))


def icon_memory():
    return svg(120, 120, "\n".join([
        f"<path d='M30 72 C12 70 12 42 32 40 C34 20 62 16 70 32 C84 22 106 32 100 52 C114 60 106 82 88 80 Z' fill='{SKY}' {S}/>",
        f"<circle cx='42' cy='94' r='7' fill='{SKY}' {S}/><circle cx='30' cy='108' r='4' fill='{SKY}' stroke='{INK}' stroke-width='2.5'/>",
        text(64, 66, "?", 30, weight="700")]))


def icon_fake_quote():
    q = lambda x, y: (f"<path d='M{x} {y} q-14 0 -14 16 v14 h16 v-16 h-8 q0 -8 8 -8 Z' fill='{INK}'/>")
    return svg(120, 120, "\n".join([
        f"<rect x='14' y='22' width='92' height='76' rx='12' fill='{PAPER}' {S}/>",
        q(46, 40), q(70, 40),
        f"<path d='M34 78 H86' stroke='{GREY}' stroke-width='3' stroke-linecap='round'/>",
        f"<circle cx='96' cy='94' r='16' fill='{RED}'/>",
        f"<path d='M89 87 L103 101 M103 87 L89 101' stroke='{PAPER}' stroke-width='4' stroke-linecap='round'/>"]))


# ------------------------------------------------------------------ asymmetry as a balance
def balance():
    w, h = 1000, 440
    tilt = math.radians(8)
    cx, cy, half = 500, 120, 300
    lx, ly = cx - half * math.cos(tilt), cy - half * math.sin(tilt)
    rx, ry = cx + half * math.cos(tilt), cy + half * math.sin(tilt)
    p = [f"<path d='M{cx} {cy} L{cx - 32} 340 H{cx + 32} Z' fill='{LIGHT}' {S}/>",
         line((cx - 90, 352), (cx + 90, 352)),
         f"<line x1='{lx:.0f}' y1='{ly:.0f}' x2='{rx:.0f}' y2='{ry:.0f}' stroke='{INK}' stroke-width='6' stroke-linecap='round'/>",
         f"<circle cx='{cx}' cy='{cy}' r='9' fill='{INK}'/>"]

    def pan(x, y, drop):
        bottom = y + drop
        return [line((x, y), (x - 100, bottom)), line((x, y), (x + 100, bottom)),
                f"<path d='M{x - 116:.0f} {bottom:.0f} H{x + 116:.0f} Q{x + 104:.0f} {bottom + 30:.0f} {x:.0f} {bottom + 30:.0f} Q{x - 104:.0f} {bottom + 30:.0f} {x - 116:.0f} {bottom:.0f} Z' fill='{PAPER}' {S}/>"], bottom
    left_parts, lb = pan(lx, ly, 160)
    right_parts, rb = pan(rx, ry, 160)
    p += left_parts + right_parts
    # left pan: a stack of pages, the long reply, sitting inside the pan
    for k in range(4):
        y = lb - 18 - k * 13
        p.append(f"<rect x='{lx - 50:.0f}' y='{y:.0f}' width='100' height='16' rx='3' fill='{PAPER}' stroke='{INK}' stroke-width='2.5'/>")
    p.append(text(lx, lb + 66, "AI reply: long", 24, weight="700"))
    p.append(text(lx, lb + 94, "no stakes of its own", 22, fill=GREY))
    # right pan: a standing researcher beside a weight
    fx = rx - 28
    p.append(f"<circle cx='{fx:.0f}' cy='{rb - 70:.0f}' r='13' fill='{PAPER}' {S}/>")
    p.append(line((fx, rb - 57), (fx, rb - 22)))
    p.append(line((fx, rb - 22), (fx - 12, rb)))
    p.append(line((fx, rb - 22), (fx + 12, rb)))
    p.append(line((fx, rb - 46), (fx + 22, rb - 34)))
    p.append(f"<path d='M{rx - 2:.0f} {rb:.0f} L{rx + 6:.0f} {rb - 40:.0f} H{rx + 58:.0f} L{rx + 66:.0f} {rb:.0f} Z' fill='{YELLOW}' {S}/>")
    p.append(text(rx + 32, rb - 13, "stakes", 16, weight="700"))
    p.append(text(rx, rb + 66, "Researcher", 24, weight="700"))
    p.append(text(rx, rb + 94, "answers for the work", 22, fill=GREY))
    return svg(w, h, "\n".join(p))


# ------------------------------------------------------------------ nested responsibility circles
def circles():
    w, h = 1180, 430
    cx, cy = 230, 215
    p = [f"<circle cx='{cx}' cy='{cy}' r='200' fill='{SKY}' stroke='{BLUE}' stroke-width='3'/>",
         f"<circle cx='{cx}' cy='{cy}' r='150' fill='#eef5fc' stroke='{BLUE}' stroke-width='3'/>",
         f"<circle cx='{cx}' cy='{cy}' r='100' fill='{PAPER}' stroke='{BLUE}' stroke-width='3'/>",
         person_icon(cx - 42, cy - 8, TEAL), ai_icon(cx + 42, cy - 6, BLUE),
         arrow(cx - 20, cy - 8, cx + 20, cy - 8, RED, 3), arrow(cx + 20, cy - 8, cx - 20, cy - 8, RED, 3),
         text(cx - 42, cy + 36, "Researcher", 16, weight="700"), text(cx + 42, cy + 36, "AI", 16, weight="700")]
    rows = [("Corporate control and regulation", "Who builds, owns and governs AI systems", 200, 60),
            ("Institutions and their rules", "Universities, journals and supervisors", 150, 205),
            ("Human–AI dyad", "The researcher and the AI in conversation", 100, 350)]
    for title, sub, r, ty in rows:
        a = math.radians({200: -40, 150: 0, 100: 40}[r])
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        p.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='6' fill='{BLUE}'/>")
        p.append(f"<path d='M{px:.0f} {py:.0f} L520 {ty - 10}' stroke='{BLUE}' stroke-width='2'/>")
        p.append(text(536, ty - 4, title, 30, anchor="start", weight="700", fill=BLUE))
        p.append(text(536, ty + 30, sub, 24, anchor="start", fill=GREY))
    return svg(w, h, "\n".join(p))


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    figures = {
        "person-laptop.svg": person_laptop(),
        "thinking-person.svg": thinking_person(),
        "oscillation.svg": oscillation(),
        "oscillation-legend.svg": oscillation_legend(),
        "metaphor-cat.svg": cat(),
        "metaphor-mirror.svg": mirror(),
        "metaphor-parrot.svg": parrot(),
        "metaphor-depth.svg": depth(),
        "four-frames.svg": four_frames(),
        "icon-no-file.svg": icon_no_file(),
        "icon-memory.svg": icon_memory(),
        "icon-fake-quote.svg": icon_fake_quote(),
        "balance.svg": balance(),
        "circles.svg": circles(),
    }
    for name, content in figures.items():
        (ASSETS / name).write_text(content, encoding="utf8")
    print("wrote", ", ".join(figures))
