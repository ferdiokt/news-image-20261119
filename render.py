"""Draws entry.png (1024x1024) and SOURCES.md from stories.py. Offline, deterministic.
Run: python3 render.py   (needs Pillow and the URW base35 fonts; only the PNG ships)."""
import math
from PIL import Image, ImageDraw, ImageFont
from stories import STORIES, REGIONS, TIMELINE, KEY_NUMBERS, DATE_CHECK, DATE_CHECK_URLS, OUTLETS, region_counts

S = 2  # draw at 2048, downsample to 1024
W = 1024
FONT_DIR = "/usr/share/fonts/opentype/urw-base35/"
INK, PAPER, PANEL, SAFFRON = "#18212E", "#E8ECF0", "#203A5C", "#F2B705"
CARD, MUTED, RULE, SEA, LAND = "#FFFFFF", "#465263", "#C3CBD5", "#D5DEE8", "#AEBBCB"
TAGS = {"REPORTED": "#23764F", "CLAIM": "#B4560B", "FORECAST": "#6A48A8"}
REGION_COL = {"Europe": "#2F62A8", "Asia-Pacific": "#C0392B", "N. America": "#7A4FA0",
              "Latin America": "#D07A1E", "Africa": "#2C8A57", "Middle East": "#9C7A12"}

img = Image.new("RGB", (W * S, W * S), PAPER)
d = ImageDraw.Draw(img)
_fonts = {}


def F(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_DIR + ("NimbusSansNarrow-Bold.otf" if bold else "NimbusSansNarrow-Regular.otf"), int(size * S))
    return _fonts[k]


def P(*xy):
    return [v * S for v in xy]


def width(s, f):
    return f.getlength(s) / S


def text(x, y, s, f, fill=INK, room=None, anchor="la"):
    """Draw text; room= asserts it fits (an overflow fails the render instead of clipping)."""
    if room is not None:
        assert width(s, f) <= room + 0.01, f"overflow {width(s, f):.0f}>{room}: {s}"
    d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)
    return width(s, f)


def wrap(s, f, room, max_lines):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if width(t, f) <= room:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    assert len(lines) <= max_lines, f"{len(lines)} lines > {max_lines}: {s}"
    return lines


def para(x, y, s, f, room, max_lines, lead, fill=INK):
    for i, ln in enumerate(wrap(s, f, room, max_lines)):
        text(x, y + i * lead, ln, f, fill, room)
    return y + len(wrap(s, f, room, max_lines)) * lead


def rect(x0, y0, x1, y1, fill=None, outline=None, r=0, w=1):
    d.rounded_rectangle(P(x0, y0, x1, y1), radius=r * S, fill=fill, outline=outline, width=int(w * S))


def tag_chip(x, y, tag, size=9):
    f = F(size)
    tw = width(tag, f)
    rect(x, y, x + tw + 8, y + size + 5, fill=TAGS[tag], r=2)
    text(x + 4, y + 2, tag, f, "#FFFFFF")
    return tw + 8


def pin(cx, cy, label, col, r=6.5):
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=col, outline="#FFFFFF", width=S)
    text(cx, cy + 0.5, label, F(8.5 if len(label) > 1 else 9.5), "#FFFFFF", anchor="mm")


# ---------- masthead ----------
rect(16, 14, 98, 92, fill=SAFFRON, r=4)
rect(16, 14, 98, 32, fill=INK, r=4)
d.rectangle(P(16, 26, 98, 32), fill=INK)
text(57, 23.5, "November", F(12), "#FFFFFF", anchor="mm")
text(57, 64, "19", F(50), INK, anchor="mm")
text(57, 86, "Thursday", F(10.5), INK, anchor="mm")
text(110, 12, "Thursday, 19 November 2026", F(66), INK, room=760)
text(1008, 20, "The world's news", F(15), MUTED, anchor="ra")
text(1008, 38, "in one day-sheet", F(15), MUTED, anchor="ra")
text(1008, 58, "All stories: 19 Nov, local dates", F(13), TAGS["REPORTED"], anchor="ra")
text(110, 82, "Trump, Xi and Putin meet in Shenzhen; the World Court finds Myanmar responsible for genocide; Anthropic soars as Wall Street slides",
     F(15.5, False), INK, room=898)

# ---------- count bar ----------
counts = region_counts()
total = sum(counts.values())
y = 106
x = 16 + text(16, y, f"{total} stories from {len(REGIONS)} regions", F(17), INK) + 14
for r in REGIONS:
    rect(x, y + 4, x + 10, y + 14, fill=REGION_COL[r], r=2)
    x += 14 + text(x + 14, y + 2, f"{r} {counts[r]}", F(13.5), INK) + 12
assert x < 1008
bx = 16
for r in REGIONS:  # proportional strip
    bw = 992 * counts[r] / total
    d.rectangle(P(bx, 127, bx + bw, 132), fill=REGION_COL[r])
    bx += bw

# ---------- leads ----------
leads = [s for s in STORIES if s["kind"] == "lead"]


def art_summit(x, y, w, h):
    cx, cy = x + w / 2, y + h * 0.62
    for i, col in enumerate(["#E0B04A", "#C9D4E2", "#D46A5A"]):  # three leaders, neutral colours
        px = cx + (i - 1) * 86
        d.ellipse(P(px - 15, cy - 50, px + 15, cy - 20), fill=col)
        d.pieslice(P(px - 30, cy - 18, px + 30, cy + 38), 180, 360, fill=col)
    d.ellipse(P(cx - 140, cy - 4, cx + 140, cy + 30), fill="#3E6189")
    d.polygon(P(cx - 22, cy + 2, cx + 18, cy - 2, cx + 24, cy + 18, cx - 16, cy + 22), fill="#F4F6F8")
    for k in range(3):
        d.line(P(cx - 14 + k, cy + 7 + k * 4, cx + 14 + k, cy + 5 + k * 4), fill="#8FA3BA", width=S)
    for k in range(3):  # 90-minute clock
        pass
    d.ellipse(P(x + w - 46, y + 8, x + w - 14, y + 40), outline="#F4F6F8", width=2 * S)
    d.pieslice(P(x + w - 44, y + 10, x + w - 16, y + 38), -90, 90, fill=SAFFRON)


def art_court(x, y, w, h):
    cx = x + w / 2
    for k in range(7):  # Peace Palace colonnade, faint
        px = x + 24 + k * 44
        d.rectangle(P(px, y + 34, px + 10, y + h - 8), fill="#2C4A70")
    d.polygon(P(x + 14, y + 34, x + w - 14, y + 34, cx, y + 10), fill="#2C4A70")
    d.rectangle(P(cx - 3, y + 22, cx + 3, y + h - 12), fill="#F4F6F8")
    d.rectangle(P(cx - 22, y + h - 14, cx + 22, y + h - 8), fill="#F4F6F8")
    d.line(P(cx - 70, y + 30, cx + 70, y + 24), fill="#F4F6F8", width=4 * S)
    for side, top in ((-70, 30), (70, 24)):
        px = cx + side
        d.line(P(px, y + top, px - 18, y + top + 32), fill="#F4F6F8", width=S)
        d.line(P(px, y + top, px + 18, y + top + 32), fill="#F4F6F8", width=S)
    d.chord(P(cx - 92, y + 50, cx - 48, y + 74), 0, 180, fill=SAFFRON)
    d.chord(P(cx + 48, y + 44, cx + 92, y + 68), 0, 180, fill=SAFFRON)
    d.ellipse(P(cx - 6, y + 16, cx + 6, y + 28), fill=SAFFRON)


def art_market(x, y, w, h):
    for k in range(4):
        d.line(P(x + 10, y + 14 + k * 20, x + w - 10, y + 14 + k * 20), fill="#2C4A70", width=S)
    pts = [(30, 18), (70, 24), (110, 22), (150, 36), (190, 44)]
    d.line([(v * S) for p in pts for v in (x + 14 + p[0], y + p[1])], fill="#E06A5E", width=3 * S, joint="curve")
    ex, ey = x + 14 + 190, y + 44
    d.polygon(P(ex + 8, ey + 4, ex - 6, ey + 4, ex + 4, ey - 10), fill="#E06A5E")
    text(x + 40, y + 56, "Dow -2.2%", F(15), "#E06A5E")
    gx = x + w - 54  # Anthropic: one up arrow, close vs IPO price
    d.rectangle(P(gx - 7, y + 30, gx + 7, y + 72), fill="#5FC08A")
    d.polygon(P(gx - 16, y + 32, gx + 16, y + 32, gx, y + 10), fill="#5FC08A")
    text(gx - 14, y + 76, "Anthropic +17% vs IPO", F(12), "#5FC08A", anchor="ra")


ARTS = [art_summit, art_court, art_market]
LX = [16, 349, 682]
LW = 326
LY0, LY1 = 140, 406
for i, s in enumerate(leads):
    x = LX[i]
    rect(x, LY0, x + LW, LY1, fill=PANEL, r=5)
    ARTS[i](x + 8, LY0 + 8, LW - 16, 92)
    pin(x + 20, LY0 + 20, s["key"], REGION_COL[s["region"]], r=9)
    yy = LY0 + 100
    lx = x + 12
    lx += text(lx, yy, s["city"], F(13), SAFFRON) + 6
    lx += text(lx, yy, f"{s['field']}, {s['time']}", F(13, False), "#C9D4E2") + 8
    tag_chip(x + LW - 12 - width(s["tag"], F(9)) - 8, yy + 1, s["tag"])
    yy = para(x + 12, yy + 20, s["head"], F(34), LW - 24, 3, 34, "#FFFFFF")
    yy = para(x + 12, yy + 4, s["fact"], F(13.5, False), LW - 24, 3, 15.5, "#E4EAF1")
    assert yy <= LY1 - 2, f"lead {s['key']} overflows its panel: {yy}"

# ---------- key numbers ----------
KY = 412
cw = 992 / len(KEY_NUMBERS)
for i, (num, cap) in enumerate(KEY_NUMBERS):
    x = 16 + i * cw
    if i:
        d.line(P(x, KY + 2, x, KY + 40), fill=RULE, width=S)
    text(x + 10, KY, num, F(25), INK, room=cw - 16)
    text(x + 10, KY + 28, cap, F(12, False), MUTED, room=cw - 16)

# ---------- cards ----------


def icon(kind, cx, cy, col):
    r = 11
    if kind == "leaf":
        d.chord(P(cx - r, cy - r, cx + r, cy + r), 200, 20, fill=col)
        d.line(P(cx - 9, cy + 7, cx + 8, cy - 6), fill="#FFFFFF", width=S)
    elif kind == "bridge":
        d.arc(P(cx - r, cy - 6, cx + r, cy + 16), 180, 360, fill=col, width=2 * S)
        d.line(P(cx - r - 2, cy - 1, cx + r + 2, cy - 1), fill=col, width=3 * S)
        d.line(P(cx - 2, cy - 6, cx + 3, cy + 3), fill=SAFFRON, width=2 * S)
    elif kind == "drone":
        d.rectangle(P(cx - 4, cy - 3, cx + 4, cy + 3), fill=col)
        for sx in (-1, 1):
            for sy in (-1, 1):
                d.line(P(cx, cy, cx + sx * 8, cy + sy * 7), fill=col, width=S)
                d.ellipse(P(cx + sx * 8 - 4, cy + sy * 7 - 2, cx + sx * 8 + 4, cy + sy * 7 + 2), fill=col)
    elif kind == "table":
        d.ellipse(P(cx - r, cy - 3, cx + r, cy + 5), fill=col)
        for px in (-7, 0, 7):
            d.ellipse(P(cx + px - 3, cy - 11, cx + px + 3, cy - 5), fill=col)
    elif kind == "tank":
        d.rounded_rectangle(P(cx - r, cy + 1, cx + r, cy + 8), radius=3 * S, fill=col)
        d.rectangle(P(cx - 6, cy - 5, cx + 4, cy + 1), fill=col)
        d.line(P(cx + 4, cy - 3, cx + 12, cy - 5), fill=col, width=2 * S)
    elif kind == "cyclone":
        for k in range(3):
            d.arc(P(cx - r + k * 3, cy - r + k * 3, cx + r - k * 3, cy + r - k * 3), k * 120, k * 120 + 220, fill=col, width=2 * S)
        d.ellipse(P(cx - 2, cy - 2, cx + 2, cy + 2), fill=col)
    elif kind == "envelope":
        d.rectangle(P(cx - r, cy - 7, cx + r, cy + 7), outline=col, width=2 * S)
        d.line(P(cx - r, cy - 7, cx, cy + 1, cx + r, cy - 7), fill=col, width=2 * S)
        d.line(P(cx + 4, cy + 3, cx + 12, cy + 11), fill=TAGS["CLAIM"], width=2 * S)
        d.line(P(cx + 12, cy + 3, cx + 4, cy + 11), fill=TAGS["CLAIM"], width=2 * S)
    elif kind == "gem":
        d.polygon(P(cx - r, cy - 3, cx - 5, cy - 9, cx + 5, cy - 9, cx + r, cy - 3, cx, cy + 10), fill=col)
        d.line(P(cx - r, cy - 3, cx + r, cy - 3), fill="#FFFFFF", width=S)
    elif kind == "shield":
        d.polygon(P(cx - 9, cy - 9, cx + 9, cy - 9, cx + 9, cy + 1, cx, cy + 10, cx - 9, cy + 1), fill=col)
        d.line(P(cx, cy - 9, cx, cy + 10), fill="#FFFFFF", width=S)
    elif kind == "link":
        d.ellipse(P(cx - 12, cy - 6, cx + 2, cy + 6), outline=col, width=2 * S)
        d.ellipse(P(cx - 2, cy - 6, cx + 12, cy + 6), outline=col, width=2 * S)
    elif kind == "chip":
        d.rectangle(P(cx - 7, cy - 7, cx + 7, cy + 7), fill=col)
        for k in (-4, 0, 4):
            for a, b, c, e in ((cx + k, cy - 11, cx + k, cy - 7), (cx + k, cy + 7, cx + k, cy + 11),
                               (cx - 11, cy + k, cx - 7, cy + k), (cx + 7, cy + k, cx + 11, cy + k)):
                d.line(P(a, b, c, e), fill=col, width=S)
        d.rectangle(P(cx - 3, cy - 3, cx + 3, cy + 3), fill="#FFFFFF")
    elif kind == "siren":
        d.pieslice(P(cx - 8, cy - 8, cx + 8, cy + 8), 180, 360, fill=col)
        d.rectangle(P(cx - 10, cy, cx + 10, cy + 5), fill=col)
        for a in (-40, 0, 40):
            t = math.radians(a - 90)
            d.line(P(cx + 11 * math.cos(t), cy - 2 + 11 * math.sin(t), cx + 15 * math.cos(t), cy - 2 + 15 * math.sin(t)), fill=col, width=S)


cards = [s for s in STORIES if s["kind"] == "card"]
CX0, CY0, CWD, CHT, GAP = 16, 462, 214, 86, 6
for i, s in enumerate(cards):
    col, row = i % 3, i // 3
    x, y = CX0 + col * (CWD + GAP), CY0 + row * (CHT + GAP)
    rect(x, y, x + CWD, y + CHT, fill=CARD, r=4)
    d.rectangle(P(x, y + 4, x + 3, y + CHT - 4), fill=REGION_COL[s["region"]])
    pin(x + 15, y + 13, s["key"], REGION_COL[s["region"]])
    lab = f"{s['city']}, {s['field']}"
    tx = x + CWD - 8 - width(s["tag"], F(9)) - 8
    text(x + 26, y + 6, lab, F(11), INK, room=tx - 30 - x - 26)
    tag_chip(tx, y + 6, s["tag"])
    icon(s["icon"], tx - 17, y + 15, REGION_COL[s["region"]])
    yy = para(x + 10, y + 26, s["head"], F(15), CWD - 18, 2, 15.5)
    para(x + 10, yy + 2, s["fact"], F(11.5, False), CWD - 18, 2, 12.5, MUTED)

# ---------- map ----------
LANDS = [
    [(-168, 66), (-140, 70), (-120, 70), (-95, 72), (-80, 68), (-62, 60), (-55, 52), (-66, 45), (-70, 42), (-76, 38), (-81, 31), (-80, 25), (-82, 27), (-84, 30), (-90, 29), (-97, 27), (-97, 22), (-92, 18), (-87, 21), (-88, 15), (-83, 10), (-78, 8), (-80, 7), (-86, 12), (-92, 14), (-105, 20), (-110, 24), (-112, 30), (-117, 33), (-124, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 62)],
    [(-55, 60), (-44, 60), (-20, 70), (-20, 78), (-60, 80), (-70, 77), (-55, 68)],
    [(-85, 22), (-74, 20), (-74.3, 20.3), (-80, 23), (-85, 22.5)],
    [(-74.5, 18.5), (-68.5, 18.5), (-68.5, 19.8), (-72, 20), (-74.5, 19.8)],
    [(-80, 9), (-72, 12), (-62, 10.5), (-52, 5), (-50, 0), (-35, -5), (-35, -9), (-39, -15), (-41, -22), (-48, -26), (-53, -34), (-58, -38), (-65, -41), (-70, -55), (-74, -50), (-74, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 0), (-78, 2), (-77, 7)],
    [(-9.5, 37), (-9, 43), (-1.5, 43.5), (-4.5, 48.5), (2, 51), (5, 53.5), (8.5, 57), (10.5, 58), (5, 58.5), (5, 62), (12, 66), (18, 70), (26, 71), (33, 69.5), (41, 67), (45, 68), (60, 69), (70, 73), (80, 73), (100, 77), (115, 73), (130, 71), (140, 72), (160, 70), (180, 68), (180, 65), (170, 60), (163, 58), (156, 51), (160, 58), (142, 59), (137, 54), (140, 48), (131, 43), (129, 35), (126, 37.5), (122, 40), (121, 37), (119, 35), (122, 31), (121, 28), (117, 23.5), (110, 21), (108, 16), (109, 12), (105, 9), (103, 10.5), (100, 13), (100, 7), (104, 1.3), (101, 3), (98, 8), (98, 16), (94, 17), (92, 22), (87, 22), (85, 19.5), (80, 15), (77.5, 8), (73, 17), (72.5, 21), (68, 23.5), (66, 25.5), (57, 25.7), (56.5, 27), (51, 24.5), (50, 26), (48, 29.5), (50, 30), (56, 27), (59, 22.5), (55, 17), (44, 12.7), (43, 14), (39, 21), (35, 28), (34.5, 29.5), (32.5, 30), (35, 32), (36, 34.5), (36, 36.8), (30, 36.2), (26.5, 38.5), (26.5, 40), (23, 40.5), (22.5, 37), (21, 38.5), (19.5, 41), (13.5, 45.5), (12.5, 44), (16, 41.5), (18.5, 40), (16, 38), (12, 41.5), (10, 44), (8.5, 44.3), (6, 43), (3.2, 43), (3, 42), (0, 39), (-0.5, 38), (-2, 36.7), (-5.5, 36)],
    [(-5.5, 50), (1.5, 51), (1.7, 52.8), (0, 53.5), (-2, 56), (-1.8, 57.6), (-5, 58.6), (-6, 56), (-4.8, 54.8), (-3, 53.5), (-4.5, 52), (-5, 51.5)],
    [(-10, 51.5), (-6, 52), (-6, 54), (-7.5, 55.3), (-10, 54)],
    [(130, 31), (132, 34), (135, 34), (140, 35), (141, 38), (142, 40), (141.5, 43), (145, 44), (141, 45.5), (139.5, 42), (140, 40), (139, 38), (136.5, 37), (133, 35.5), (130, 34)],
    [(120, 18.5), (122, 18.5), (124, 13), (126, 7), (122, 7), (120, 14)],
    [(95, 5.5), (98, 4), (106, -6), (103, -5), (95, 3)],
    [(109, 1.5), (117, 7), (119, 1), (116, -4), (110, -3)],
    [(105.5, -6), (114.5, -7.5), (114.5, -8.7), (106, -7.5)],
    [(131, -1), (141, -2.5), (150, -10), (141, -9), (137, -5)],
    [(114, -22), (114, -34), (117, -35), (123, -34), (129, -31.5), (135, -34.5), (138, -35.5), (140, -38), (146, -39), (150, -37), (153, -32), (153, -25), (146, -19), (142, -10.7), (141, -17), (136, -12), (130, -11.3), (126, -14), (122, -17)],
    [(-17, 21), (-17, 14.7), (-15, 11), (-13, 8), (-8, 4.5), (-2, 5), (4, 6.3), (9, 4), (9.5, 1), (12, -5), (13.5, -11), (12, -17), (15, -27), (18.5, -34.5), (22, -34), (27, -33.5), (32.5, -28.5), (35.5, -24), (35, -20), (40.5, -15), (40, -10), (39.5, -5), (41.5, -1.5), (46, 2), (51, 10.5), (51, 12), (44, 10.5), (43, 12), (39.5, 15.5), (37, 19), (34.5, 26), (32.5, 30), (32, 31.3), (29, 31), (25, 32), (20, 30.8), (19, 32), (15, 32.2), (11, 33.2), (10, 37), (8, 37), (-1, 35.7), (-6, 35.8), (-9.5, 32), (-10, 29), (-13, 27.5)],
    [(44, -25), (47, -25), (50, -15.5), (49, -12), (44, -17)],
]
WATERS = [
    [(28, 41.5), (28, 43.5), (30, 46), (33, 44.5), (36, 45.2), (38, 47), (40, 44), (41.5, 41.5), (37, 41), (31, 41.2)],
    [(47, 45), (50, 46.5), (53, 45), (53, 40), (54, 37), (51, 36.6), (49, 38), (50, 40.5), (47, 43)],
    [(10.5, 54), (14, 54), (19, 54.5), (21, 57), (24, 59.5), (30, 60), (23, 60.5), (21, 63), (25, 65.5), (21, 65.5), (17, 62), (19, 60), (16, 57), (12.5, 56)],
]


def draw_map(x0, y0, w, h, lon0, lon1, lat0, lat1):
    sx, sy = w / (lon1 - lon0), h / (lat1 - lat0)

    def pr(lon, lat):
        return x0 + (lon - lon0) * sx, y0 + (lat1 - lat) * sy
    sub = Image.new("RGB", (round(w * S), round(h * S)), SEA)  # own canvas = clipped to the box
    sd = ImageDraw.Draw(sub)
    for poly, col in [(p, LAND) for p in LANDS] + [(p, SEA) for p in WATERS]:
        sd.polygon([((lon - lon0) * sx * S, (lat1 - lat) * sy * S) for lon, lat in poly], fill=col)
    img.paste(sub, (round(x0 * S), round(y0 * S)))
    return pr


MX, MY, MW, MH = 684, 482, 324, 104
rect(MX - 4, MY - 20, 1008 + 4, MY + MH + 92, fill=CARD, r=4)
text(MX, MY - 16, "Where it happened", F(12), INK)
text(1008, MY - 16, "pins match the lettered and numbered stories", F(11, False), MUTED, anchor="ra")
d.rectangle(P(MX, MY, MX + MW, MY + MH), fill=SEA)
pr = draw_map(MX, MY, MW, MH, -105, 150, -14, 68)
NUDGE = {"B": (-7, -5), "11": (5, 5), "9": (-3, -6), "4": (3, 6), "5": (0, -6), "7": (6, -3), "8": (-4, 5)}  # close cities: offset pins so each stays readable
EU = (-2, 42, 29, 58)  # inset box lon0, lon1, lat0, lat1
a, b = pr(EU[0], EU[3]); c, e = pr(EU[1], EU[2])
d.rectangle(P(a, b, c, e), outline=INK, width=S)
inset = [s for s in STORIES if s["kind"] in ("lead", "card") and EU[0] <= s["lon"] <= EU[1] and EU[2] <= s["lat"] <= EU[3]]
for s in STORIES:
    if s["kind"] in ("lead", "card") and s not in inset:
        px, py = pr(s["lon"], s["lat"])
        pin(px + NUDGE.get(s["key"], (0, 0))[0], py + NUDGE.get(s["key"], (0, 0))[1], s["key"], REGION_COL[s["region"]])
IX, IY, IW, IH = MX, MY + MH + 6, 150, 82
pr2 = draw_map(IX, IY, IW, IH, *EU)
d.rectangle(P(IX, IY, IX + IW, IY + IH), outline=INK, width=S)
for s in inset:
    px, py = pr2(s["lon"], s["lat"])
    dx, dy = NUDGE.get(s["key"], (0, 0))
    pin(px + dx, py + dy, s["key"], REGION_COL[s["region"]])
text(IX + IW + 10, IY + 2, "Inset: Europe and", F(11.5), INK)
text(IX + IW + 10, IY + 16, "the Middle East", F(11.5), INK)
text(IX + IW + 10, IY + 34, "A-C leads, 1-12 cards.", F(11, False), MUTED, room=1008 - IX - IW - 10)
text(IX + IW + 10, IY + 48, "Pin colour = region,", F(11, False), MUTED, room=1008 - IX - IW - 10)
text(IX + IW + 10, IY + 62, "as in the count bar.", F(11, False), MUTED, room=1008 - IX - IW - 10)

# ---------- timeline ----------
TY = 698
rect(MX - 4, TY - 4, 1012, 818, fill=CARD, r=4)
text(MX, TY, "Selected events, local times (all on 19 Nov)", F(12), INK, room=324)
for i, (t, ev) in enumerate(TIMELINE):
    yy = TY + 20 + i * 13.5
    d.ellipse(P(MX + 3, yy + 3, MX + 9, yy + 9), fill=INK)
    if i < len(TIMELINE) - 1:
        d.line(P(MX + 6, yy + 9, MX + 6, yy + 16.5), fill=RULE, width=S)
    text(MX + 16, yy, t, F(11.5), INK)
    text(MX + 104, yy, ev, F(11.5, False), INK, room=1008 - MX - 104)

# ---------- briefs ----------
BY = 828
briefs = [s for s in STORIES if s["kind"] == "brief"]
text(16, BY, f"In brief, by city ({len(briefs)} more; dot colour = tag)", F(13), INK)
half = (len(briefs) + 1) // 2
for i, s in enumerate(briefs):
    col, row = i // half, i % half
    x, yy = 16 + col * 334, BY + 19 + row * 13.0
    d.ellipse(P(x, yy + 3, x + 7, yy + 10), fill=TAGS[s["tag"]])
    cw2 = text(x + 11, yy, s["city"], F(11.5), REGION_COL[s["region"]])
    text(x + 11 + cw2 + 5, yy, s["head"], F(11.5, False), INK, room=322 - 16 - cw2)

# ---------- date check ----------
DX = 684
rect(DX - 4, BY - 4, 1012, 966, fill="#FFF6DA", outline=SAFFRON, r=4, w=1.5)
text(DX, BY, "Date check: earlier news, left out, not counted", F(13), INK, room=324)
for i, (dt, ev) in enumerate(DATE_CHECK):
    yy = BY + 18 + i * 12.0
    text(DX, yy, dt, F(11), TAGS["CLAIM"])
    text(DX + 40, yy, ev, F(11, False), INK, room=1008 - DX - 40)

# ---------- legend + footer ----------
FY = 972
x = 16
for tag, meaning in (("REPORTED", "confirmed by two or more named outlets"), ("CLAIM", "one side's statement, not verified"),
                     ("FORECAST", "expected or scheduled")):
    x += tag_chip(x, FY, tag) + 5
    x += text(x, FY + 1, meaning, F(11.5, False), INK) + 18
d.line(P(16, FY + 18, 1008, FY + 18), fill=RULE, width=S)
text(16, FY + 21, f"Sources: {OUTLETS}; full links in SOURCES.md.", F(11.5, False), MUTED, room=992)
text(16, FY + 35, "Every story here happened, or was first reported, on Thursday 19 November 2026 in local time. Drawn in code; no photos.",
     F(11.5), INK, room=992)

img.resize((W, W), Image.LANCZOS).save("entry.png", optimize=True)

# ---------- SOURCES.md ----------
out = ["# Sources: Thursday 19 November 2026", "",
       "Every story happened, or was first reported, on 19 November 2026 (local time). "
       "Tags: REPORTED = confirmed by two or more named outlets; CLAIM = one side's statement, not independently verified; "
       "FORECAST = expected or scheduled.", ""]
for kind, title in (("lead", "Leads"), ("card", "Cards"), ("brief", "Briefs")):
    out += [f"## {title}", ""]
    for s in STORIES:
        if s["kind"] != kind:
            continue
        key = f"{s.get('key', '-')}. " if kind != "brief" else ""
        out.append(f"- **{key}{s['head']}** ({s['city']}, {s['region']}; {s['field']}; {s['tag']}; {s['time']})")
        if s.get("fact"):
            out.append(f"  - {s['fact']}")
        out += [f"  - <{u}>" for u in s["urls"]]
    out.append("")
out += ["## Date check: big stories left out because they belong to other days", ""]
out += [f"- {dt}: {ev} <{u}>" for (dt, ev), u in zip(DATE_CHECK, DATE_CHECK_URLS)]
open("SOURCES.md", "w").write("\n".join(out) + "\n")
print("ok", len(STORIES), "stories")
