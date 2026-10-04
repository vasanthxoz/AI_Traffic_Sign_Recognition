"""
generate_signs.py
-----------------
Creates the 68 reference traffic-sign / traffic-signal images stored in
reference_images/.  The images are drawn with Pillow (shapes, lines, text) so
the project is fully self-contained - no internet or dataset download needed.

You can replace any file in reference_images/ with a real photo/clip-art of
the same name (e.g. stop.jpg) and the system will use it automatically.

Run:  python generate_signs.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

S = 512                       # drawing size (saved at 256x256)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_images")

RED, BLUE, YELLOW = (205, 0, 0), (0, 80, 170), (250, 200, 0)
WHITE, BLACK, GREEN, GREY = (255, 255, 255), (0, 0, 0), (0, 140, 60), (70, 70, 70)

FONT_FILES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def font(size):
    for f in FONT_FILES:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size=size)


# ---------------------------------------------------------------- helpers
def canvas():
    img = Image.new("RGB", (S, S), WHITE)
    return img, ImageDraw.Draw(img)


def txt(d, xy, s, size, fill):
    d.text(xy, s, font=font(size), fill=fill, anchor="mm")


def disc(d, fill, r=235, c=256):
    d.ellipse((c - r, c - r, c + r, c + r), fill=fill)


def P(cx, cy, s, *pts):
    return [(cx + x * s, cy + y * s) for x, y in pts]


def flip(pts):
    return [(S - x, y) for x, y in pts]


def arrow(d, p0, p1, col, w=30, head=60):
    pl_arrow(d, [p0, p1], col, w, head)


def pl_arrow(d, pts, col, w=30, head=60):
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    bx, by = x1 - ux * head, y1 - uy * head
    d.line(list(pts[:-1]) + [(bx + ux * 4, by + uy * 4)], fill=col, width=w, joint="curve")
    nx, ny = -uy, ux
    d.polygon([(x1, y1), (bx + nx * head * 0.62, by + ny * head * 0.62),
               (bx - nx * head * 0.62, by - ny * head * 0.62)], fill=col)


def person(d, cx, cy, h, col):
    lw = max(6, int(h * 0.09))
    r = h * 0.11
    d.ellipse((cx - r, cy - 0.45 * h - r, cx + r, cy - 0.45 * h + r), fill=col)
    d.line((cx, cy - 0.3 * h, cx, cy + 0.08 * h), fill=col, width=lw)
    d.line((cx - 0.22 * h, cy - 0.05 * h, cx, cy - 0.22 * h, cx + 0.22 * h, cy - 0.08 * h), fill=col, width=lw)
    d.line((cx - 0.2 * h, cy + 0.45 * h, cx, cy + 0.08 * h, cx + 0.18 * h, cy + 0.45 * h), fill=col, width=lw)


def car(d, cx, cy, w, col, bg=WHITE):
    h = w * 0.45
    d.rectangle((cx - w / 2, cy - h * 0.1, cx + w / 2, cy + h * 0.4), fill=col)
    d.polygon([(cx - w * .3, cy - h * .1), (cx - w * .17, cy - h * .55),
               (cx + w * .17, cy - h * .55), (cx + w * .3, cy - h * .1)], fill=col)
    r = w * 0.1
    for dx in (-0.27, 0.27):
        d.ellipse((cx + dx * w - r, cy + h * .4 - r, cx + dx * w + r, cy + h * .4 + r), fill=col, outline=bg, width=4)


def truck(d, cx, cy, w, col, bg=WHITE):
    h = w * 0.5
    d.rectangle((cx - w / 2, cy - h * .5, cx + w * .12, cy + h * .3), fill=col)
    d.polygon([(cx + w * .16, cy - h * .2), (cx + w * .36, cy - h * .2), (cx + w / 2, cy + h * .05),
               (cx + w / 2, cy + h * .3), (cx + w * .16, cy + h * .3)], fill=col)
    r = w * 0.075
    for dx in (-0.3, -0.05, 0.33):
        d.ellipse((cx + dx * w - r, cy + h * .3 - r, cx + dx * w + r, cy + h * .3 + r), fill=col, outline=bg, width=4)


def bike(d, cx, cy, w, col):
    r, lw = w * 0.22, max(5, int(w * 0.05))
    for dx in (-0.3, 0.3):
        d.ellipse((cx + dx * w - r, cy + r * .4 - r, cx + dx * w + r, cy + r * .4 + r), outline=col, width=lw)
    d.line([(cx - .3 * w, cy + .4 * r), (cx - .05 * w, cy - .7 * r), (cx + .3 * w, cy + .4 * r)], fill=col, width=lw)
    d.line([(cx - .05 * w, cy - .7 * r), (cx + .12 * w, cy - 1.0 * r), (cx + .2 * w, cy - 1.0 * r)], fill=col, width=lw)
    d.line([(cx - .12 * w, cy - .95 * r), (cx - .02 * w, cy - .95 * r)], fill=col, width=lw)


def horn(d, cx, cy, s, col):
    d.polygon([(cx - s * .5, cy - s * .12), (cx - s * .1, cy - s * .12), (cx + s * .5, cy - s * .45),
               (cx + s * .5, cy + s * .45), (cx - s * .1, cy + s * .12), (cx - s * .5, cy + s * .12)], fill=col)


def ring_arrows(d, cx, cy, r, col, lw):
    for k in range(3):
        a0 = k * 120 + 10
        d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 78, fill=col, width=lw)
        a = math.radians(a0 + 78)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        nx, ny = math.cos(a), math.sin(a)
        d.polygon([(px + tx * lw * 1.7, py + ty * lw * 1.7), (px + nx * lw * 1.3, py + ny * lw * 1.3),
                   (px - nx * lw * 1.3, py - ny * lw * 1.3)], fill=col)


def uturn(d, col, cx=256, cy=256, s=1.0, w=36):
    pts = P(cx, cy, 100 * s, (-0.55, 0.9), (-0.55, -0.25), (-0.3, -0.7), (0.3, -0.7), (0.55, -0.25), (0.55, 0.5))
    pl_arrow(d, pts, col, int(w * s), int(80 * s))


# -------------------------------------------------------- base sign shapes
def prohib(inner=WHITE):
    img, d = canvas()
    disc(d, RED)
    disc(d, inner, r=185)
    return img, d


def slash(d, w=38):
    d.line((105, 105, 407, 407), fill=RED, width=w)


def mand():
    img, d = canvas()
    disc(d, BLUE)
    d.ellipse((44, 44, 468, 468), outline=WHITE, width=8)
    return img, d


def warn():
    img, d = canvas()
    outer = [(256, 25), (25, 440), (487, 440)]
    cx, cy = 256, 302
    d.polygon(outer, fill=RED)
    d.polygon([(cx + .68 * (x - cx), cy + .68 * (y - cy)) for x, y in outer], fill=WHITE)
    return img, d


def info():
    img, d = canvas()
    d.rounded_rectangle((20, 20, 492, 492), radius=50, fill=BLUE)
    d.rounded_rectangle((40, 40, 472, 472), radius=38, outline=WHITE, width=8)
    return img, d


def scale_poly(pts, k, c=(256, 256)):
    return [(c[0] + k * (x - c[0]), c[1] + k * (y - c[1])) for x, y in pts]


# ---------------------------------------------------------------- registry
REG = []


def sign(sid):
    def deco(fn):
        REG.append((sid, fn))
        return fn
    return deco


# --------------------------------------------------------- PROHIBITORY (23)
@sign("no_entry")
def _():
    img, d = canvas(); disc(d, RED); d.rectangle((100, 218, 412, 294), fill=WHITE); return img


@sign("no_parking")
def _():
    img, d = prohib(BLUE); slash(d); return img


@sign("no_stopping")
def _():
    img, d = prohib(BLUE)
    d.line((120, 120, 392, 392), fill=RED, width=36); d.line((392, 120, 120, 392), fill=RED, width=36); return img


@sign("no_uturn")
def _():
    img, d = prohib(); uturn(d, BLACK, s=1.0); slash(d); return img


@sign("no_left_turn")
def _():
    img, d = prohib(); pl_arrow(d, P(256, 256, 150, (0.35, 0.9), (0.35, -0.3), (-0.7, -0.3)), BLACK, 38, 80); slash(d); return img


@sign("no_right_turn")
def _():
    img, d = prohib(); pl_arrow(d, flip(P(256, 256, 150, (0.35, 0.9), (0.35, -0.3), (-0.7, -0.3))), BLACK, 38, 80); slash(d); return img


@sign("no_overtaking")
def _():
    img, d = prohib(); car(d, 188, 262, 120, BLACK); car(d, 326, 262, 120, RED); return img


@sign("horn_prohibited")
def _():
    img, d = prohib(); horn(d, 256, 256, 230, BLACK); slash(d); return img


for _v in (20, 30, 40, 50, 60, 70, 80, 100):
    def _mk(v):
        @sign(f"speed_limit_{v}")
        def _():
            img, d = prohib(); txt(d, (256, 262), str(v), 190 if v < 100 else 135, BLACK); return img
    _mk(_v)


@sign("no_trucks")
def _():
    img, d = prohib(); truck(d, 256, 262, 250, BLACK); return img


@sign("no_pedestrians")
def _():
    img, d = prohib(); person(d, 256, 262, 270, BLACK); slash(d); return img


@sign("no_cycles")
def _():
    img, d = prohib(); bike(d, 256, 262, 250, BLACK); return img


@sign("no_vehicles")
def _():
    img, d = prohib(); return img


@sign("width_limit")
def _():
    img, d = prohib()
    d.rectangle((112, 165, 132, 325), fill=BLACK); d.rectangle((380, 165, 400, 325), fill=BLACK)
    arrow(d, (256, 245), (140, 245), BLACK, 22, 50); arrow(d, (256, 245), (372, 245), BLACK, 22, 50)
    txt(d, (256, 365), "2.5m", 78, BLACK); return img


@sign("height_limit")
def _():
    img, d = prohib()
    d.rectangle((165, 112, 347, 130), fill=BLACK); d.rectangle((165, 292, 347, 310), fill=BLACK)
    arrow(d, (256, 211), (256, 138), BLACK, 22, 50); arrow(d, (256, 211), (256, 284), BLACK, 22, 50)
    txt(d, (256, 365), "3.5m", 78, BLACK); return img


@sign("weight_limit")
def _():
    img, d = prohib(); txt(d, (256, 262), "10T", 140, BLACK); return img


for _v in (110, 120):
    def _mk2(v):
        @sign(f"speed_limit_{v}")
        def _():
            img, d = prohib(); txt(d, (256, 262), str(v), 115, BLACK); return img
    _mk2(_v)


@sign("no_motorbikes")
def _():
    """Motorcycle silhouette (simplified bike with engine block) + red cross-bar."""
    img, d = prohib()
    # wheels
    r = 48
    d.ellipse((140 - r, 296 - r, 140 + r, 296 + r), outline=BLACK, width=12)
    d.ellipse((372 - r, 296 - r, 372 + r, 296 + r), outline=BLACK, width=12)
    # frame
    d.line([(140, 296), (220, 210), (300, 210), (372, 296)], fill=BLACK, width=14)
    d.line([(220, 210), (256, 296), (140, 296)], fill=BLACK, width=14)
    # handlebar
    d.line([(290, 210), (290, 185), (320, 185)], fill=BLACK, width=10)
    slash(d)
    return img


@sign("no_animals")
def _():
    """Simple cow/horse profile + red cross-bar."""
    img, d = prohib()
    # body
    d.ellipse((175, 240, 340, 320), fill=BLACK)
    # head
    d.ellipse((320, 215, 375, 270), fill=BLACK)
    # legs
    for x in (200, 230, 285, 315):
        d.line([(x, 315), (x, 375)], fill=BLACK, width=12)
    # tail
    d.line([(175, 255), (145, 230)], fill=BLACK, width=8)
    # ear
    d.line([(345, 215), (335, 195)], fill=BLACK, width=7)
    slash(d)
    return img


@sign("no_heavy_vehicles")
def _():
    """Heavy truck + red cross-bar."""
    img, d = prohib()
    truck(d, 256, 255, 260, BLACK)
    slash(d)
    return img


@sign("end_speed_limit")
def _():
    """Grey circle with diagonal grey bar and '0' — end of all speed limits."""
    img, d = canvas()
    disc(d, GREY)
    disc(d, WHITE, r=185)
    txt(d, (256, 262), "0", 190, GREY)
    d.line((105, 105, 407, 407), fill=GREY, width=38)
    return img


# ---------------------------------------------------------- MANDATORY (10)
@sign("turn_left_ahead")
def _():
    img, d = mand(); pl_arrow(d, P(256, 256, 150, (0.35, 0.9), (0.35, -0.3), (-0.7, -0.3)), WHITE, 44, 96); return img


@sign("turn_right_ahead")
def _():
    img, d = mand(); pl_arrow(d, flip(P(256, 256, 150, (0.35, 0.9), (0.35, -0.3), (-0.7, -0.3))), WHITE, 44, 96); return img


@sign("ahead_only")
def _():
    img, d = mand(); arrow(d, (256, 390), (256, 120), WHITE, 48, 110); return img


@sign("keep_left")
def _():
    img, d = mand(); arrow(d, (345, 140), (175, 375), WHITE, 48, 110); return img


@sign("keep_right")
def _():
    img, d = mand(); arrow(d, (167, 140), (337, 375), WHITE, 48, 110); return img


@sign("roundabout")
def _():
    img, d = mand(); ring_arrows(d, 256, 256, 98, WHITE, 34); return img


@sign("compulsory_horn")
def _():
    img, d = mand(); horn(d, 256, 256, 250, WHITE); return img


@sign("cycle_track")
def _():
    img, d = mand(); bike(d, 256, 262, 270, WHITE); return img


@sign("pedestrians_only")
def _():
    img, d = mand(); person(d, 256, 262, 290, WHITE); return img


@sign("min_speed_30")
def _():
    img, d = mand(); txt(d, (256, 262), "30", 200, WHITE); return img


@sign("go_left")
def _():
    """Mandatory — bear left: upward-then-left curved arrow."""
    img, d = mand()
    pl_arrow(d, P(256, 256, 150, (0.35, 0.85), (0.35, -0.1), (-0.5, -0.7)), WHITE, 44, 96)
    return img


@sign("go_right")
def _():
    """Mandatory — bear right: upward-then-right curved arrow."""
    img, d = mand()
    pl_arrow(d, flip(P(256, 256, 150, (0.35, 0.85), (0.35, -0.1), (-0.5, -0.7))), WHITE, 44, 96)
    return img


@sign("pass_either_side")
def _():
    """Mandatory — two white arrows pointing left and right from centre."""
    img, d = mand()
    arrow(d, (256, 256), (120, 256), WHITE, 40, 90)
    arrow(d, (256, 256), (392, 256), WHITE, 40, 90)
    return img


# ----------------------------------------------------------- PRIORITY (4)
@sign("stop")
def _():
    img, d = canvas()
    pts = [(256 + 250 * math.cos(math.radians(22.5 + 45 * k)), 256 + 250 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    d.polygon(pts, fill=RED)
    d.polygon(scale_poly(pts, 0.9), outline=WHITE, width=9)
    txt(d, (256, 262), "STOP", 150, WHITE); return img


@sign("give_way")
def _():
    img, d = canvas()
    outer = [(25, 60), (487, 60), (256, 480)]
    cx, cy = 256, 200
    d.polygon(outer, fill=RED)
    d.polygon([(cx + .7 * (x - cx), cy + .7 * (y - cy)) for x, y in outer], fill=WHITE); return img


def diamond(d):
    pts = [(256, 8), (504, 256), (256, 504), (8, 256)]
    d.polygon(pts, fill=BLACK); d.polygon(scale_poly(pts, .95), fill=WHITE); d.polygon(scale_poly(pts, .8), fill=YELLOW)


@sign("priority_road")
def _():
    img, d = canvas(); diamond(d); return img


@sign("end_priority_road")
def _():
    img, d = canvas(); diamond(d)
    for o in (-70, 0, 70):
        d.line((110 + o, 400, 400 + o, 110), fill=GREY, width=12)
    return img


# ------------------------------------------------------------ WARNING (20)
@sign("pedestrian_crossing")
def _():
    img, d = warn(); person(d, 256, 322, 120, BLACK)
    for x in range(200, 320, 34):
        d.rectangle((x, 384, x + 20, 394), fill=BLACK)
    return img


@sign("school_ahead")
def _():
    img, d = warn(); person(d, 225, 325, 125, BLACK); person(d, 296, 348, 82, BLACK); return img


@sign("left_curve")
def _():
    img, d = warn(); pl_arrow(d, P(256, 325, 80, (0.4, 0.8), (0.4, 0.2), (0.1, -0.3), (-0.55, -0.55)), BLACK, 16, 40); return img


@sign("right_curve")
def _():
    img, d = warn(); pl_arrow(d, flip(P(256, 325, 80, (0.4, 0.8), (0.4, 0.2), (0.1, -0.3), (-0.55, -0.55))), BLACK, 16, 40); return img


@sign("hairpin_bend")
def _():
    img, d = warn()
    pl_arrow(d, P(256, 325, 75, (0.45, 0.8), (0.45, -0.2), (0.2, -0.5), (-0.2, -0.5), (-0.45, -0.2), (-0.45, 0.4)), BLACK, 15, 38); return img


@sign("road_narrows")
def _():
    img, d = warn()
    l = P(256, 330, 75, (-0.55, 0.7), (-0.25, 0.2), (-0.25, -0.3), (-0.55, -0.8))
    d.line(l, fill=BLACK, width=16, joint="curve"); d.line(flip(l), fill=BLACK, width=16, joint="curve"); return img


@sign("slippery_road")
def _():
    img, d = warn(); car(d, 256, 305, 105, BLACK)
    for y in (362, 386):
        d.line([(190 + 20 * i, y + (10 if i % 2 else -10)) for i in range(8)], fill=BLACK, width=8, joint="curve")
    return img


@sign("falling_rocks")
def _():
    img, d = warn()
    d.polygon([(185, 390), (330, 390), (330, 288)], fill=BLACK)
    d.ellipse((205, 280, 249, 324), fill=BLACK); d.ellipse((262, 288, 296, 322), fill=BLACK); return img


@sign("speed_breaker")
def _():
    img, d = warn(); d.pieslice((176, 300, 336, 430), 180, 360, fill=BLACK); d.rectangle((160, 365, 352, 380), fill=BLACK); return img


@sign("cross_road")
def _():
    img, d = warn(); d.rectangle((240, 262, 272, 392), fill=BLACK); d.rectangle((188, 310, 324, 342), fill=BLACK); return img


@sign("t_junction")
def _():
    img, d = warn(); d.rectangle((188, 288, 324, 320), fill=BLACK); d.rectangle((240, 288, 272, 392), fill=BLACK); return img


@sign("roundabout_ahead")
def _():
    img, d = warn(); ring_arrows(d, 256, 332, 52, BLACK, 14); return img


@sign("signals_ahead")
def _():
    img, d = warn(); d.rounded_rectangle((216, 252, 296, 392), radius=14, fill=BLACK)
    for y, c in ((284, RED), (322, YELLOW), (360, GREEN)):
        d.ellipse((256 - 20, y - 20, 256 + 20, y + 20), fill=c)
    return img


@sign("level_crossing")
def _():
    img, d = warn(); d.line((195, 268, 317, 392), fill=BLACK, width=30); d.line((317, 268, 195, 392), fill=BLACK, width=30); return img


@sign("men_at_work")
def _():
    img, d = warn(); person(d, 222, 325, 118, BLACK); d.polygon([(268, 388), (305, 330), (345, 388)], fill=BLACK); return img


@sign("steep_descent")
def _():
    img, d = warn(); d.polygon([(185, 288), (330, 390), (185, 390)], fill=BLACK); txt(d, (290, 318), "10%", 40, BLACK); return img


@sign("steep_ascent")
def _():
    img, d = warn(); d.polygon([(185, 390), (330, 390), (330, 288)], fill=BLACK); txt(d, (232, 318), "10%", 40, BLACK); return img


@sign("two_way_traffic")
def _():
    img, d = warn()
    arrow(d, (222, 390), (222, 275), BLACK, 16, 42); arrow(d, (292, 275), (292, 390), BLACK, 16, 42); return img


@sign("animals_crossing")
def _():
    img, d = warn()
    d.ellipse((195, 300, 305, 350), fill=BLACK); d.ellipse((292, 285, 330, 320), fill=BLACK)
    for x in (212, 228, 272, 290):
        d.line((x, 340, x, 388), fill=BLACK, width=9)
    d.line((300, 288, 292, 272), fill=BLACK, width=6); d.line((324, 288, 332, 272), fill=BLACK, width=6)
    d.line((196, 312, 180, 335), fill=BLACK, width=6); return img


@sign("general_danger")
def _():
    img, d = warn(); txt(d, (256, 335), "!", 190, BLACK); return img


@sign("uneven_road")
def _():
    """Warning — bumpy/uneven road surface."""
    img, d = warn()
    pts = [(200, 390), (220, 360), (240, 385), (260, 350), (280, 385), (300, 360), (320, 390)]
    d.line(pts, fill=BLACK, width=16, joint="curve")
    return img


@sign("loose_gravel")
def _():
    """Warning — stones/gravel on road."""
    img, d = warn()
    for cx, cy, r in [(210, 360, 16), (240, 380, 12), (265, 355, 14), (290, 375, 11), (315, 360, 15), (235, 345, 10)]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLACK)
    return img


@sign("flood_road")
def _():
    """Warning — wavy water lines."""
    img, d = warn()
    for y in (330, 358, 386):
        pts = [(200 + 20 * i, y + (10 if i % 2 else -10)) for i in range(7)]
        d.line(pts, fill=BLUE if y == 358 else BLACK, width=12, joint="curve")
    return img


@sign("side_road_left")
def _():
    """Warning — side road joining from the left."""
    img, d = warn()
    # main road (vertical)
    d.rectangle((240, 265, 272, 395), fill=BLACK)
    # side road (left branch)
    d.rectangle((188, 295, 240, 327), fill=BLACK)
    return img


@sign("side_road_right")
def _():
    """Warning — side road joining from the right."""
    img, d = warn()
    # main road (vertical)
    d.rectangle((240, 265, 272, 395), fill=BLACK)
    # side road (right branch)
    d.rectangle((272, 295, 324, 327), fill=BLACK)
    return img


@sign("staggered_junction")
def _():
    """Warning — staggered/offset crossroads."""
    img, d = warn()
    d.rectangle((240, 265, 272, 395), fill=BLACK)
    d.rectangle((188, 300, 240, 328), fill=BLACK)
    d.rectangle((272, 330, 324, 358), fill=BLACK)
    return img


@sign("narrow_bridge")
def _():
    """Warning — narrow bridge symbol (two parallel lines tapering)."""
    img, d = warn()
    # road deck
    d.rectangle((232, 275, 280, 395), fill=BLACK)
    # bridge rails
    d.line([(195, 270), (232, 290)], fill=BLACK, width=12)
    d.line([(317, 270), (280, 290)], fill=BLACK, width=12)
    d.line([(195, 270), (195, 395)], fill=BLACK, width=10)
    d.line([(317, 270), (317, 395)], fill=BLACK, width=10)
    return img


@sign("accident_zone")
def _():
    """Warning — two car collision symbol."""
    img, d = warn()
    car(d, 208, 318, 100, BLACK)
    car(d, 308, 318, 100, BLACK)
    # impact burst lines
    for a in range(0, 360, 45):
        r1, r2 = 28, 48
        ax, ay = 256 + r1 * math.cos(math.radians(a)), 318 + r1 * math.sin(math.radians(a))
        bx, by = 256 + r2 * math.cos(math.radians(a)), 318 + r2 * math.sin(math.radians(a))
        d.line([(ax, ay), (bx, by)], fill=RED, width=6)
    return img


@sign("double_bend")
def _():
    """Warning — S-shaped double bend arrow."""
    img, d = warn()
    pl_arrow(d, P(256, 325, 80,
                  (0.0, 0.85), (0.0, 0.4), (0.5, 0.1), (0.5, -0.3),
                  (0.0, -0.55), (-0.4, -0.7)), BLACK, 15, 38)
    return img


@sign("risk_grounding")
def _():
    """Warning — humped road with car scraping ground."""
    img, d = warn()
    # hump
    d.arc((190, 320, 320, 430), 180, 360, fill=BLACK, width=14)
    d.rectangle((160, 387, 352, 398), fill=BLACK)
    # sparks
    for dx in (-20, 0, 20):
        d.line([(256 + dx, 385), (256 + dx - 8, 400)], fill=RED, width=5)
    return img


# -------------------------------------------------------- INFORMATORY (8)
@sign("parking")
def _():
    img, d = info(); txt(d, (256, 268), "P", 330, WHITE); return img


@sign("hospital")
def _():
    img, d = info(); txt(d, (256, 268), "H", 330, WHITE); return img


@sign("fuel_station")
def _():
    img, d = info()
    d.rectangle((180, 130, 310, 370), fill=WHITE); d.rectangle((202, 155, 288, 230), fill=BLUE)
    d.rectangle((160, 370, 330, 392), fill=WHITE)
    d.line([(310, 190), (355, 190), (368, 260), (368, 330)], fill=WHITE, width=16, joint="curve"); return img


@sign("bus_stop")
def _():
    img, d = info()
    d.rounded_rectangle((130, 170, 382, 340), radius=22, fill=WHITE)
    for x in (150, 222, 294):
        d.rectangle((x, 192, x + 60, 255), fill=BLUE)
    d.rectangle((150, 275, 362, 290), fill=BLUE)
    for x in (190, 322):
        d.ellipse((x - 30, 315, x + 30, 375), fill=WHITE, outline=BLUE, width=9)
    return img


@sign("one_way")
def _():
    img, d = info(); arrow(d, (95, 256), (417, 256), WHITE, 64, 130); return img


@sign("dead_end")
def _():
    img, d = info(); d.rectangle((234, 150, 278, 380), fill=WHITE); d.rectangle((150, 150, 362, 190), fill=RED); return img


@sign("first_aid")
def _():
    img, d = info()
    d.rounded_rectangle((140, 140, 372, 372), radius=24, fill=WHITE)
    d.rectangle((234, 168, 278, 344), fill=GREEN); d.rectangle((168, 234, 344, 278), fill=GREEN); return img


@sign("telephone")
def _():
    img, d = info()
    d.line((185, 190, 328, 332), fill=WHITE, width=70)
    d.ellipse((150, 155, 220, 225), fill=WHITE); d.ellipse((293, 297, 363, 367), fill=WHITE)
    d.arc((220, 100, 400, 280), 270, 360, fill=WHITE, width=14); d.arc((260, 60, 440, 240), 270, 360, fill=WHITE, width=14)
    return img


@sign("tourist_info")
def _():
    """Informatory — blue square with white 'i'."""
    img, d = info(); txt(d, (256, 280), "i", 310, WHITE); return img


@sign("rest_area")
def _():
    """Informatory — picnic table + tree."""
    img, d = info()
    # table
    d.rectangle((148, 278, 310, 296), fill=WHITE)
    d.rectangle((162, 296, 190, 360), fill=WHITE)
    d.rectangle((268, 296, 296, 360), fill=WHITE)
    # tree trunk
    d.rectangle((340, 310, 362, 380), fill=WHITE)
    # tree crown
    d.ellipse((305, 220, 395, 320), fill=WHITE)
    return img


@sign("toll_ahead")
def _():
    """Informatory — toll barrier with TOLL text."""
    img, d = info()
    txt(d, (256, 210), "TOLL", 100, WHITE)
    # barrier arm
    d.rectangle((148, 295, 364, 315), fill=WHITE)
    # booth
    d.rectangle((140, 315, 200, 390), fill=WHITE)
    return img


@sign("petrol_ahead")
def _():
    """Informatory — fuel pump + right-pointing arrow."""
    img, d = info()
    # pump body
    d.rectangle((155, 160, 275, 380), fill=WHITE); d.rectangle((175, 180, 255, 245), fill=BLUE)
    d.rectangle((140, 375, 290, 395), fill=WHITE)
    # hose
    d.line([(275, 210), (310, 210), (320, 270), (320, 330)], fill=WHITE, width=14, joint="curve")
    # arrow
    arrow(d, (310, 330), (420, 330), WHITE, 28, 56)
    return img


@sign("no_through_road_right")
def _():
    """Informatory — main road straight, right branch dead-end (red bar)."""
    img, d = info()
    # main road (vertical)
    d.rectangle((234, 140, 278, 390), fill=WHITE)
    # right branch
    d.rectangle((278, 215, 390, 255), fill=WHITE)
    # dead-end bar (red)
    d.rectangle((378, 195, 406, 275), fill=RED)
    return img


# --------------------------------------------------------- TRAFFIC SIGNALS (3)
def light(active):
    img, d = canvas()
    d.rounded_rectangle((165, 20, 347, 492), radius=40, fill=(25, 25, 25))
    dark = {"red": (90, 20, 20), "amber": (95, 80, 15), "green": (15, 70, 30)}
    lit = {"red": (230, 20, 20), "amber": (255, 190, 0), "green": (20, 200, 80)}
    for y, n in ((120, "red"), (256, "amber"), (392, "green")):
        d.ellipse((256 - 62, y - 62, 256 + 62, y + 62), fill=lit[n] if n == active else dark[n])
    return img


@sign("red_light")
def _():
    return light("red")


@sign("amber_light")
def _():
    return light("amber")


@sign("green_light")
def _():
    return light("green")


def main():
    os.makedirs(OUT, exist_ok=True)
    for sid, fn in REG:
        fn().resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, sid + ".jpg"), quality=95)
    print(f"Generated {len(REG)} reference images in {OUT}")


if __name__ == "__main__":
    main()
