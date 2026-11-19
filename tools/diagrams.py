"""A small SVG kit for the problem diagrams (used by tools/figs/sNN.py).

Coordinates are pixels. Colours come from CSS classes inside each SVG, with a
prefers-color-scheme block, so one file reads well on light and dark pages.

  Svg            canvas with line/poly/rect/circle/text/arrow primitives
  gate()         and/or/xor/nand/nor/xnor/not/buf symbols
  mux()          trapezoid mux symbol
  box()          a block with named ports (prefix a port with '>' for a clock input)
  wave()         timing diagram from WaveDrom-like strings
  fsm()          state diagram (circles, curved edges, self loops)
  bitfield()     rows of bit fields, optionally linked field to field
"""
import math
from html import escape

STYLE = """
.s{stroke:#1d2125;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.thin{stroke-width:1}
.bus{stroke-width:3.5}
.dash{stroke-dasharray:4 4}
.t{fill:#1d2125;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}
.sm{font-size:11px}
.b{font-weight:700}
.m{fill:#6b7280}
.ms{stroke:#9aa0a8}
.a{fill:#2a5db0}
.as{stroke:#2a5db0}
.af{fill:#dbe6f7}
.bg{fill:#ffffff}
.xf{fill:#e5e7eb}
.k{fill:#1d2125}
.ak{fill:#2a5db0}
@media (prefers-color-scheme:dark){
.s{stroke:#e4e6e9}.t{fill:#e4e6e9}.m{fill:#9aa0a8}.ms{stroke:#6b7280}
.a{fill:#7aa7ff}.as{stroke:#7aa7ff}.af{fill:#2c3a52}.bg{fill:#17191c}
.xf{fill:#3a3f46}.k{fill:#e4e6e9}.ak{fill:#7aa7ff}}
"""

FONT_W = 7.8      # advance of one 13px monospace character
FONT_W_SM = 6.6   # ... and of an 11px one


def n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text_w(s, small=False):
    return len(s) * (FONT_W_SM if small else FONT_W)


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def line(self, x1, y1, x2, y2, cls="s"):
        self.add(f'<line class="{cls}" x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}"/>')

    def poly(self, pts, cls="s", closed=False):
        tag = "polygon" if closed else "polyline"
        p = " ".join(f"{n(x)},{n(y)}" for x, y in pts)
        self.add(f'<{tag} class="{cls}" points="{p}"/>')

    def path(self, d, cls="s"):
        self.add(f'<path class="{cls}" d="{d}"/>')

    def rect(self, x, y, w, h, cls="s", rx=0):
        r = f' rx="{n(rx)}"' if rx else ""
        self.add(f'<rect class="{cls}" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{r}/>')

    def circle(self, cx, cy, r, cls="s"):
        self.add(f'<circle class="{cls}" cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>')

    def text(self, x, y, s, anchor="middle", cls="t"):
        self.add(f'<text class="{cls}" x="{n(x)}" y="{n(y)}" text-anchor="{anchor}" '
                 f'dominant-baseline="central">{escape(str(s))}</text>')

    def label(self, x, y, s, anchor="middle", cls="t", small=False):
        """Text on a background patch, for labels that sit on top of lines."""
        w = text_w(s, small) + 6
        x0 = {"start": x - 3, "end": x - w + 3}.get(anchor, x - w / 2)
        self.rect(x0, y - (8 if small else 9), w, 16 if small else 18, "bg")
        self.text(x, y, s, anchor, cls + (" sm" if small else ""))

    def dot(self, x, y):
        self.circle(x, y, 3, "k")

    def wire(self, *pts, cls="s"):
        self.poly(pts, cls)

    def arrowhead(self, x, y, ang, cls="k", size=8):
        a = math.radians(ang)
        p1 = (x - size * math.cos(a - 0.4), y - size * math.sin(a - 0.4))
        p2 = (x - size * math.cos(a + 0.4), y - size * math.sin(a + 0.4))
        self.poly([(x, y), p1, p2], cls, closed=True)

    def arrow(self, *pts, cls="s", head="k"):
        self.poly(pts, cls)
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        self.arrowhead(x2, y2, math.degrees(math.atan2(y2 - y1, x2 - x1)), head)

    def pin(self, x, y, name, side="left", cls="t"):
        """A signal name at a wire end: side='left' puts the text left of (x, y)."""
        if side == "left":
            self.text(x - 6, y, name, "end", cls)
        elif side == "right":
            self.text(x + 6, y, name, "start", cls)
        elif side == "above":
            self.text(x, y - 10, name, "middle", cls)
        else:
            self.text(x, y + 11, name, "middle", cls)

    def render(self, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(self.w)}" height="{n(self.h)}" '
                f'viewBox="0 0 {n(self.w)} {n(self.h)}" role="img">\n'
                f'<title>{escape(title)}</title>\n<style>{STYLE}</style>\n'
                + "\n".join(self.parts) + "\n</svg>\n")


def hv(p, q, xm=None):
    """Points for an orthogonal route from p to q that turns at x = xm (default halfway)."""
    if p[1] == q[1]:
        return [p, q]
    xm = (p[0] + q[0]) / 2 if xm is None else xm
    return [p, (xm, p[1]), (xm, q[1]), q]


# ---------------------------------------------------------------- gates and blocks

def gate(svg, kind, x, y, nin=2, w=None):
    """Gate body starting at x, centred vertically on y. Returns (input points, output point)."""
    kind = kind.lower()
    if kind in ("not", "buf"):
        svg.poly([(x, y - 14), (x, y + 14), (x + 28, y)], "s", closed=True)
        out = x + 28
        if kind == "not":
            svg.circle(x + 32, y, 4)
            out = x + 36
        return [(x, y)], (out, y)
    h = 20 * nin if nin > 2 else 40
    top, bot = y - h / 2, y + h / 2
    pins_y = [y + 20 * (i - (nin - 1) / 2) for i in range(nin)]
    base = {"nand": "and", "nor": "or", "xnor": "xor"}.get(kind, kind)
    w = w or max(44, h / 2 + 26)
    if base == "and":
        r = h / 2
        svg.path(f"M{n(x)},{n(top)} H{n(x + w - r)} A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(bot)} "
                 f"H{n(x)} Z")
        ins = [(x, py) for py in pins_y]
        out = x + w
    else:
        bx = x + 7 if base == "xor" else x
        bw = w
        svg.path(f"M{n(bx)},{n(top)} Q{n(bx + .6 * bw)},{n(top)} {n(bx + bw)},{n(y)} "
                 f"Q{n(bx + .6 * bw)},{n(bot)} {n(bx)},{n(bot)} Q{n(bx + .25 * bw)},{n(y)} {n(bx)},{n(top)} Z")
        if base == "xor":
            svg.path(f"M{n(x)},{n(top)} Q{n(x + .25 * bw)},{n(y)} {n(x)},{n(bot)}")
        ins = []
        for py in pins_y:
            t = (py - top) / h
            ins.append((x + .5 * t * (1 - t) * bw, py))
        out = bx + bw
    if kind in ("nand", "nor", "xnor"):
        svg.circle(out + 4, y, 4)
        out += 8
    return ins, (out, y)


def mux(svg, x, y, nin=2, w=34, labels=None, sel_side="bottom"):
    """A mux with nin inputs spaced 20 apart, centred on y. Returns (inputs, select point, output)."""
    h = 20 * nin + 16
    top, bot = y - h / 2, y + h / 2
    svg.poly([(x, top), (x + w, top + 12), (x + w, bot - 12), (x, bot)], "s", closed=True)
    ins = []
    labels = labels or [str(i) for i in range(nin)]
    for i in range(nin):
        py = y + 20 * (i - (nin - 1) / 2)
        ins.append((x, py))
        svg.text(x + 5, py, labels[i], "start", "t sm m")
    sel = (x + w / 2, bot - 6) if sel_side == "bottom" else (x + w / 2, top + 6)
    return ins, sel, (x + w, y)


def box(svg, x, y, w, h, title="", left=(), right=(), top=(), bottom=(), cls="s", title_y=None,
        title_cls="t b"):
    """A block with ports. Each port list is spread evenly along its side; a name that starts
    with '>' gets a clock triangle. Returns {name: (x, y)} of the pins on the box edge."""
    svg.rect(x, y, w, h, cls, rx=3)
    if title:
        lines = title.split("\n")
        ty = title_y if title_y is not None else y + h / 2 - 8 * (len(lines) - 1)
        for i, line in enumerate(lines):
            svg.text(x + w / 2, ty + 16 * i, line, "middle", title_cls)
    pins = {}

    def spread(names, a, b):
        """Even spacing, unless a port is given as (name, fraction along the side)."""
        k = len(names)
        return [a + (b - a) * (nm[1] if isinstance(nm, tuple) else (i + 1) / (k + 1))
                for i, nm in enumerate(names)]

    pos = [spread(left, y, y + h), spread(right, y, y + h), spread(top, x, x + w), spread(bottom, x, x + w)]
    left, right, top, bottom = ([nm[0] if isinstance(nm, tuple) else nm for nm in side]
                                for side in (left, right, top, bottom))

    for name, py in zip(left, pos[0]):
        clock = name.startswith(">")
        shown = name.lstrip(">")
        if clock:
            svg.poly([(x, py - 6), (x + 9, py), (x, py + 6)])
        if shown:
            svg.text(x + (13 if clock else 5), py, shown, "start", "t sm m")
        pins[name.lstrip(">") or ">"] = (x, py)
    for name, py in zip(right, pos[1]):
        if name:
            svg.text(x + w - 5, py, name, "end", "t sm m")
        pins[name] = (x + w, py)
    for name, px in zip(top, pos[2]):
        if name:
            svg.text(px, y + 10, name, "middle", "t sm m")
        pins[name] = (px, y)
    for name, px in zip(bottom, pos[3]):
        clock = name.startswith(">")
        shown = name.lstrip(">")
        if clock:
            svg.poly([(px - 6, y + h), (px, y + h - 9), (px + 6, y + h)])
        if shown:
            svg.text(px, y + h - (16 if clock else 10), shown, "middle", "t sm m")
        pins[shown or ">"] = (px, y + h)
    return pins


def dff(svg, x, y, label="", w=60, h=70, d="d", q="q", extra_left=()):
    """A register box: title at the top, d and q level with each other, clock lower left.
    extra_left: more (name, fraction) ports on the left (e.g. ("en", .6))."""
    left = [(d, .45)] + list(extra_left) + [(">", .8)]
    return box(svg, x, y, w, h, label, left=left, right=[(q, .45)], title_y=y + 13, title_cls="t sm b")


# ---------------------------------------------------------------- waveforms

def wave(signals, slot=34, header=None, outputs=(), title="", marks=(), grid=True, names_w=None,
         row=30, note=None, ticks=None):
    """Timing diagram. signals: list of (name, spec) or (name, spec, [labels]).

    One spec character per slot:
      p / n   a clock period starting with a rising / falling edge
      0 1     levels (also l h)     z  high impedance     x  unknown
      =       a bus value (the next label)     .  continue the previous slot
      |       (ignored, for readability)
    header: labels centred over the slots (e.g. cycle numbers or times).
    ticks: {slot index: label} drawn above the slot's left edge (e.g. times at clock edges).
    marks: slot indices where a dashed vertical marker is drawn (at the slot's left edge).
    outputs: names drawn in the accent colour.
    """
    sigs = []
    for s in signals:
        name, spec = s[0], s[1].replace("|", "")
        data = list(s[2]) if len(s) > 2 else []
        sigs.append((name, spec, data))
    nslots = max(len(spec) for _, spec, _ in sigs)
    names_w = names_w or max(text_w(nm) for nm, _, _ in sigs) + 22
    top = 26 if header or ticks else 8
    H = top + row * len(sigs) + (22 if note else 6)
    W = max(names_w + nslots * slot + 12, names_w + text_w(note or "", True) + 12)
    svg = Svg(W, H)
    x0 = names_w
    if header:
        for i, h in enumerate(header):
            if h != "":
                svg.text(x0 + (i + .5) * slot, 12, h, "middle", "t sm m")
    if ticks:
        for i, t in ticks.items():
            svg.text(x0 + i * slot, top - 8, t, "middle", "t sm m")
    # grid at the rising edges of the clock ('p' slots, or 0 -> 1 steps of a signal named clk)
    clock_spec = next((spec for nm, spec, _ in sigs if nm == "clk" or "p" in spec or "n" in spec), None)
    if grid and clock_spec:
        if spec_is_clock(clock_spec):
            clock_spec = clock_spec[0] * len(clock_spec)
        edges = [i + (.5 if c == "n" else 0) for i, c in enumerate(clock_spec) if c in "pn"]
        edges += [i for i in range(1, len(clock_spec)) if clock_spec[i - 1:i + 1] == "01"]
        for e in edges:
            svg.line(x0 + e * slot, top, x0 + e * slot, top + row * len(sigs), "s thin ms dash")
    for m in marks:
        svg.line(x0 + m * slot, top - 4, x0 + m * slot, top + row * len(sigs), "s as dash")
    for r, (name, spec, data) in enumerate(sigs):
        y_hi = top + r * row + 6
        y_lo = y_hi + row - 12
        y_mid = (y_hi + y_lo) / 2
        svg.text(x0 - 12, y_mid, name, "end", "t a b" if name in outputs else "t")
        # expand to half-slot segments: (x_start, x_end, state)
        segs = []
        if spec_is_clock(spec):
            spec = spec[0] * len(spec)      # "p...." is a free-running clock
        for i, c in enumerate(spec.ljust(nslots, ".")):
            xa, xm, xb = x0 + i * slot, x0 + (i + .5) * slot, x0 + (i + 1) * slot
            if c in "pn":
                a, b = ("1", "0") if c == "p" else ("0", "1")
                segs += [[xa, xm, a, None], [xm, xb, b, None]]
            elif c == ".":
                if segs:
                    segs[-1][1] = xb
            elif c in "01lhzx":
                st = {"l": "0", "h": "1"}.get(c, c)
                if segs and segs[-1][2] == st and st != "=":
                    segs[-1][1] = xb
                else:
                    segs.append([xa, xb, st, None])
            elif c == "=":
                segs.append([xa, xb, "=", data.pop(0) if data else ""])
        prev = None
        for xa, xb, st, lab in segs:
            lvl = {"0": y_lo, "1": y_hi, "z": y_mid}
            if st in lvl:
                y = lvl[st]
                if prev is not None and prev[2] in lvl and lvl[prev[2]] != y:
                    svg.line(xa, lvl[prev[2]], xa, y)
                cls = "s as" if st == "z" else "s"
                svg.line(xa, y, xb, y, cls)
            else:
                e = min(4, (xb - xa) / 4)
                pts = [(xa, y_mid), (xa + e, y_hi), (xb - e, y_hi), (xb, y_mid), (xb - e, y_lo), (xa + e, y_lo)]
                svg.poly(pts, "s af" if st == "=" else "s xf", closed=True)
                if st == "=" and lab != "" and text_w(str(lab), True) <= xb - xa - 4:
                    small = text_w(str(lab)) > xb - xa - 6
                    svg.text((xa + xb) / 2, y_mid, lab, "middle", "t sm" if small else "t")
            prev = (xa, xb, st)
    if note:
        svg.text(x0, H - 11, note, "start", "t sm m")
    return svg.render(title or "timing diagram")


def spec_is_clock(spec):
    return bool(spec) and spec[0] in "pn" and set(spec) <= set("pn.")


# ---------------------------------------------------------------- state diagrams

def fsm(w, h, states, edges, r=30, reset=None, title="state diagram", note=None):
    """states: {name: (x, y)} or {name: (x, y, "out")}; edges: (a, b, label[, bend]).
    For a == b the 4th item is the self-loop direction in degrees (default -90 = above).
    For a != b, bend > 0 curves the edge to the left of travel (0 = straight).
    reset: (state, angle_degrees) draws a 'reset' arrow into that state."""
    svg = Svg(w, h)
    pos = {k: (v[0], v[1]) for k, v in states.items()}
    labels = []
    for e in edges:
        a, b, lab = e[0], e[1], e[2]
        extra = e[3] if len(e) > 3 else None
        if a == b:
            ang = math.radians(-90 if extra is None else extra)
            cx, cy = pos[a]
            s1, s2 = ang - .45, ang + .45
            p0 = (cx + r * math.cos(s1), cy + r * math.sin(s1))
            p3 = (cx + r * math.cos(s2), cy + r * math.sin(s2))
            c1 = (cx + (r + 44) * math.cos(ang - .55), cy + (r + 44) * math.sin(ang - .55))
            c2 = (cx + (r + 44) * math.cos(ang + .55), cy + (r + 44) * math.sin(ang + .55))
            svg.path(f"M{n(p0[0])},{n(p0[1])} C{n(c1[0])},{n(c1[1])} {n(c2[0])},{n(c2[1])} "
                     f"{n(p3[0])},{n(p3[1])}")
            svg.arrowhead(p3[0], p3[1], math.degrees(math.atan2(p3[1] - c2[1], p3[0] - c2[0])))
            c, sn = math.cos(ang), math.sin(ang)
            # beside the loop, reading away from the state
            anchor = "start" if c > .3 else "end" if c < -.3 else "middle"
            dist = r + (38 if anchor != "middle" else 44)
            labels.append((cx + dist * c, cy + dist * sn, lab, anchor))
            continue
        bend = extra or 0
        (x1, y1), (x2, y2) = pos[a], pos[b]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        nx, ny = dy / d, -dx / d          # left of travel (screen coordinates)
        cx, cy = (x1 + x2) / 2 + nx * bend * d, (y1 + y2) / 2 + ny * bend * d

        def edge_pt(px, py, tx, ty):
            vx, vy = tx - px, ty - py
            m = math.hypot(vx, vy)
            return px + r * vx / m, py + r * vy / m
        sx, sy = edge_pt(x1, y1, cx, cy)
        ex, ey = edge_pt(x2, y2, cx, cy)
        svg.path(f"M{n(sx)},{n(sy)} Q{n(cx)},{n(cy)} {n(ex)},{n(ey)}")
        svg.arrowhead(ex, ey, math.degrees(math.atan2(ey - cy, ex - cx)))
        mx, my = .25 * sx + .5 * cx + .25 * ex, .25 * sy + .5 * cy + .25 * ey
        if bend and lab:
            # sit the label just outside a curved edge instead of on top of it
            side = 1 if bend > 0 else -1
            lw = max(text_w(line, True) for line in lab.split("\n"))
            off = abs(nx) * (lw / 2 + 4) + abs(ny) * (8 + 7 * lab.count("\n")) + 2
            mx, my = mx + side * nx * off, my + side * ny * off
        labels.append((mx, my, lab, "middle"))
    if reset:
        st, ang = reset
        cx, cy = pos[st]
        a = math.radians(ang)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        sx, sy = cx + (r + 36) * math.cos(a), cy + (r + 36) * math.sin(a)
        svg.arrow((sx, sy), (ex, ey), cls="s as", head="ak")
        tx, ty = cx + (r + 46) * math.cos(a), cy + (r + 46) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < .3 else ("start" if math.cos(a) > 0 else "end")
        svg.text(tx, ty, "reset", anchor, "t sm a")
    for name, v in states.items():
        x, y = v[0], v[1]
        out = v[2] if len(v) > 2 else None
        svg.circle(x, y, r, "s bg")
        svg.circle(x, y, r, "s")
        if out:
            svg.text(x, y - 7, name, "middle", "t b" if text_w(name) < 2 * r - 6 else "t sm b")
            svg.text(x, y + 9, out, "middle", "t sm a")
        else:
            svg.text(x, y, name, "middle", "t b" if text_w(name) < 2 * r - 6 else "t sm b")
    for x, y, lab, anchor in labels:
        if lab:
            for i, line in enumerate(lab.split("\n")):
                svg.label(x, y + 14 * i - 7 * (lab.count("\n")), line, anchor, small=True)
    if note:
        svg.text(10, h - 10, note, "start", "t sm m")
    return svg.render(title)


# ---------------------------------------------------------------- bit fields

def bitfield(rows, bw=14, links=(), gap=64, title="bit fields", label_w=None, numbers=True, note=None):
    """rows: list of (row_label, [(field_label, hi, lo[, cls]), ...]) drawn MSB on the left.
    cls: '' (plain), 'a' (accent fill), 'x' (grey fill).
    A field's width is (hi - lo + 1) * bw, or give hi=None and lo=width-in-bits for an unnumbered field.
    links: ((row, field_index), (row, field_index)) lines from the upper field to the lower one."""
    label_w = label_w if label_w is not None else max((text_w(r[0]) for r in rows), default=0) + 18
    widths = []
    for _, fields in rows:
        widths.append(sum(bits(f) for f in fields) * bw)
    W = max(label_w + max(widths) + 14, label_w + text_w(note or "", True) + 10)
    rowh = 30
    H = 18 + len(rows) * rowh + (len(rows) - 1) * gap + (24 if note else 8)
    svg = Svg(W, H)
    geo = []
    for ri, (rl, fields) in enumerate(rows):
        y = 18 + ri * (rowh + gap)
        svg.text(label_w - 10, y + rowh / 2, rl, "end", "t")
        x = label_w
        g = []
        for f in fields:
            fw = bits(f) * bw
            cls = f[3] if len(f) > 3 else ""
            fill = {"a": "s af", "x": "s xf"}.get(cls, "s bg")
            svg.rect(x, y, fw, rowh, fill)
            lab = f[0]
            small = text_w(lab) > fw - 10
            if lab:
                svg.text(x + fw / 2, y + rowh / 2, lab, "middle", "t sm" if small else "t")
            if numbers and f[1] is not None:
                hi, lo = f[1], f[2]
                if hi == lo:
                    svg.text(x + fw / 2, y - 7, str(hi), "middle", "t sm m")
                else:
                    svg.text(x + 2, y - 7, str(hi), "start", "t sm m")
                    svg.text(x + fw - 2, y - 7, str(lo), "end", "t sm m")
            g.append((x, y, fw))
            x += fw
        geo.append(g)
    for (ra, fa), (rb, fb) in links:
        xa, ya, wa = geo[ra][fa]
        xb, yb, wb = geo[rb][fb]
        p, q = (xa + wa / 2, ya + rowh), (xb + wb / 2, yb - (14 if numbers else 0))
        svg.arrow(p, q, cls="s thin ms", head="k")
    if note:
        svg.text(label_w, H - 12, note, "start", "t sm m")
    return svg.render(title)


def bits(f):
    return f[2] if f[1] is None else f[1] - f[2] + 1


def frame(svg, x, y, w, h, label="top_module"):
    """The dashed outline of the module being written, labelled at its top-left corner."""
    svg.rect(x, y, w, h, "s thin ms dash", rx=4)
    svg.text(x + 8, y + 12, label, "start", "t sm m")


def ripple(cells, x0=120, y0=62, cw=74, ch=56, gap=56, bus=False, cin="cin", cout="cout",
           carry=lambda i: "", ins=lambda i: (f"a({i})", f"b({i})"), out=lambda i: f"s({i})",
           cell="FA", title="ripple-carry chain"):
    """A carry chain drawn MSB-left: cells is a list of stage indices (None = a '...' gap).
    Carries flow right to left; carry(i) labels the wire leaving stage i."""
    x0 = max(x0, gap + text_w(cout, True) + 16)
    W = x0 + len(cells) * (cw + gap) + 40
    H = y0 + ch + 50
    svg = Svg(W, H)
    wcls = "s bus" if bus else "s"
    cy = y0 + ch / 2

    def left(k):
        return x0 + k * (cw + gap)

    for k, i in enumerate(cells):
        x = left(k)
        if i is None:
            svg.text(x + cw / 2, cy, "· · ·", "middle", "t b m")
            continue
        box(svg, x, y0, cw, ch, f"{cell}{i}")
        for px, lab, up in zip((x + cw / 3, x + 2 * cw / 3), ins(i), (38, 20)):
            svg.wire((px, y0 - up), (px, y0), cls=wcls)
            svg.text(px, y0 - up - 9, lab, "middle", "t sm")
        svg.wire((x + cw / 2, y0 + ch), (x + cw / 2, y0 + ch + 22), cls=wcls)
        svg.text(x + cw / 2, y0 + ch + 32, out(i), "middle", "t sm a b")
        if k + 1 == len(cells):
            svg.arrow((x + cw + gap - 8, cy), (x + cw, cy))
            svg.text(x + cw + gap - 4, cy, cin, "start", "t sm")
        elif cells[k + 1] is None:
            svg.arrow((left(k + 1) + cw / 2 - 18, cy), (x + cw, cy), cls="s dash")
        else:
            svg.arrow((left(k + 1), cy), (x + cw, cy))
            if carry(cells[k + 1]):
                svg.text(x + cw + gap / 2, cy - 10, carry(cells[k + 1]), "middle", "t sm m")
        if k > 0 and cells[k - 1] is None:
            svg.wire((x, cy), (left(k - 1) + cw / 2 + 18, cy), cls="s dash")
        if k == 0:
            svg.wire((x, cy), (x - gap + 12, cy))
            svg.text(x - gap + 8, cy, cout, "end", "t sm a b")
    return svg.render(title)


def clocked(n, inputs, step, out, state, sub=2, edge="rise", always=None, clk=True):
    """Simulate a spec cycle by cycle and return wave() signal rows.

    n cycles of `sub` slots each; the clock is low for the first half of a cycle and high for
    the second, so the rising edge is at slot sub/2 of each cycle.
    inputs: [(name, values)], with one value per cycle (it changes at the falling edge that
            starts the cycle) or one per slot. Values are 0/1, None (unknown) or labels.
    step(state, inp) -> new state, called at each active edge ('rise', 'fall' or 'both').
    out(state, inp) -> {name: value}, evaluated in every slot.
    always(state, inp) -> state, applied in every slot before out (for asynchronous resets).
    """
    total = n * sub
    rows = {}
    order = []
    if clk:
        rows["clk"] = ["0"] * total
        for i in range(total):
            rows["clk"][i] = "1" if i % sub >= sub // 2 else "0"
        order.append("clk")
    vals = {}
    for name, v in inputs:
        v = list(v)
        vals[name] = [v[i // sub] for i in range(total)] if len(v) == n else v
        order.append(name)
    outs = {}
    for i in range(total):
        inp = {k: v[i] for k, v in vals.items()}
        rise = i % sub == sub // 2
        fall = i % sub == 0 and i > 0
        if (edge in ("rise", "both") and rise) or (edge in ("fall", "both") and fall):
            state = step(state, inp)
        if always:
            state = always(state, inp)
        for k, v in out(state, inp).items():
            outs.setdefault(k, []).append(v)
    order += list(outs)
    vals.update(outs)
    result = []
    for name in order:
        seq = rows.get(name) or vals[name]
        result.append(to_row(name, seq))
    return result


def to_row(name, seq):
    """Values per slot -> (name, spec, labels). A row whose values are all 0/1/None/'z' is drawn
    as a level; any other row is a bus with each value as a label. None is unknown."""
    levels = {0: "0", 1: "1", "0": "0", "1": "1", "z": "z"}
    bus = any(v is not None and v not in levels for v in seq)
    spec, labels, prev = "", [], object()
    for v in seq:
        if v == prev and spec:
            spec += "."
        elif v is None:
            spec += "x"
        elif bus:
            spec += "="
            labels.append(str(v))
        else:
            spec += levels[v]
        prev = v
    return (name, spec, labels)
