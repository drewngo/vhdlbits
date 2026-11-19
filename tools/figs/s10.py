from diagrams import Svg, bitfield, clocked, dff, gate, mux, wave


def shift4():
    return bitfield([
        ("q", [(f"q({i})", i, i) for i in range(3, -1, -1)]),
        ("next q", [("0", 3, 3, "x")] + [(f"q({i + 1})", i, i, "a") for i in range(2, -1, -1)]),
    ], bw=48, gap=46, links=[((0, k), (1, k + 1)) for k in range(3)],
        note="en = 1: shift right, 0 enters at the top; q(0) falls off",
        title="shift right by one with a 0 shifted in")


def rotate(right):
    top = [(f"q{i}", i, i) for i in range(7, -1, -1)]
    if right:
        bot = [("q0", 7, 7, "a")] + [(f"q{i + 1}", i, i) for i in range(6, -1, -1)]
        links = [((0, k), (1, k + 1)) for k in range(7)] + [((0, 7), (1, 0))]
        return bitfield([("q", top), ("ena = 01", bot)], bw=36, gap=50, links=links, label_w=86,
                        title="ena = 01 rotates right: q0 wraps around to q7")
    bot = [(f"q{i - 1}", i, i) for i in range(7, 0, -1)] + [("q7", 0, 0, "a")]
    links = [((0, k + 1), (1, k)) for k in range(7)] + [((0, 0), (1, 7))]
    return bitfield([("q", top), ("ena = 10", bot)], bw=36, gap=50, links=links, label_w=86,
                    title="ena = 10 rotates left: q7 wraps around to q0")


def galois(cells, taps, title, w_cell=112, w_gap=56, note=None):
    """A right-shifting Galois LFSR, MSB on the left. cells: indices (None = a gap).
    taps: indices i whose next value is q(i+1) xor q(0). The MSB always gets q(0)."""
    xs, x = [], 60
    for i in cells:
        xs.append(x)
        x += w_gap if i is None else w_cell
    svg = Svg(x + 20, 190)
    regs = []
    for x, i in zip(xs, cells):
        if i is None:
            svg.text(x + w_gap / 2, 100, "· · ·", "middle", "t b m")
            regs.append(None)
        else:
            regs.append(dff(svg, x + w_cell - 60, 70, f"q({i})", w=50, h=64))
    yq = regs[0]["d"][1]
    yfb = 30
    q0 = regs[-1]["q"]
    xr = q0[0] + 16
    svg.wire(q0, (xr, yq), (xr, yfb), (40, yfb), (40, yq), regs[0]["d"])
    for k in range(1, len(cells)):
        a, b, i = regs[k - 1], regs[k], cells[k]
        if b is None:
            svg.wire(a["q"], (a["q"][0] + 16, yq), cls="s dash")
            continue
        start = a["q"] if a else (xs[k] - 16, yq)
        if a is None:
            svg.wire(start, (start[0] + 12, yq), cls="s dash")
            start = (start[0] + 12, yq)
        if i in taps:
            gx = b["d"][0] - 44
            gi, go = gate(svg, "xor", gx, yq, w=26)
            svg.wire(start, (gx - 12, yq), (gx - 12, gi[1][1]), gi[1])
            svg.wire((gx - 3, yfb), (gx - 3, gi[0][1]), gi[0])
            svg.dot(gx - 3, yfb)
            svg.wire(go, b["d"])
        else:
            svg.wire(start, b["d"])
    svg.text(svg.w / 2, 182, note or "shifts right; q(0) feeds the MSB and every XOR tap", "middle", "t sm m")
    return svg.render(title)


def sipo():
    bits = [0, 0, 1, 0, 1, 1, 0, 1]           # x"B4", LSB first
    sin = [None] + bits[:3] + [None] + bits[3:] + [1]
    en = [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1]

    def step(st, i):
        cnt, sr, dout, valid = st
        if not i["en"]:
            return (cnt, sr, dout, 0)
        sr = (sr >> 1) | ((i["sin"] or 0) << 7)
        if cnt == 7:
            return (0, sr, f"{sr:02X}", 1)
        return (cnt + 1, sr, dout, 0)
    rows = clocked(11, [("en", en), ("sin", sin)], step=step,
                   out=lambda st, i: {"valid": st[3], "dout": st[2]}, state=(0, 0, "00", 0))
    return wave(rows, slot=17, outputs=("valid", "dout"), note="the 8 accepted bits, LSB first, make x\"B4\"",
                title="serial in, parallel out: the 8th accepted bit completes a byte")


def piso():
    def step(st, i):
        busy, n, sr, sout = st
        if busy:
            if n == 8:
                return (0, 0, sr, 0)
            return (1, n + 1, sr, (sr >> (7 - n)) & 1)
        if i["load"]:
            return (1, 1, i["d"], (i["d"] >> 7) & 1)
        return st
    load = [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1]
    d = [None, 0xA5, None, None, 0x33, None, None, None, None, None, None, None]
    rows = clocked(12, [("load", load), ("d", [f"{v:02X}" if v is not None else None for v in d])],
                   step=lambda st, i: step(st, {"load": i["load"], "d": int(i["d"], 16) if i["d"] else 0}),
                   out=lambda st, i: {"busy": st[0], "sout": st[3]}, state=(0, 0, 0, 0))
    return wave(rows, slot=17, outputs=("busy", "sout"), note="x\"A5\" = 1010 0101, sent MSB first; the second load is ignored",
                title="parallel in, serial out: load captures d, then 8 bits leave MSB first")


def shift_n():
    svg = Svg(520, 150)
    labels = ["q(0)", "q(1)", None, "q(N-1)"]
    regs = []
    for k, lab in enumerate(labels):
        x = 90 + 100 * k
        if lab is None:
            svg.text(x + 28, 72, "· · ·", "middle", "t b m")
            regs.append(None)
        else:
            regs.append(dff(svg, x, 40, lab, w=58, h=64))
    y = regs[0]["d"][1]
    svg.wire((40, y), regs[0]["d"]); svg.pin(40, y, "sin")
    svg.wire(regs[0]["q"], regs[1]["d"])
    svg.wire(regs[1]["q"], (regs[1]["q"][0] + 26, y), cls="s dash")
    svg.wire((regs[3]["d"][0] - 26, y), regs[3]["d"], cls="s dash")
    svg.wire(regs[3]["q"], (470, y)); svg.pin(470, y, "sout", "right", "t a b")
    svg.text(260, 135, "on each edge with en = 1, every bit moves one place up", "middle", "t sm m")
    return svg.render("an N-bit shift register: sin enters at q(0), sout is q(N-1)")


def tap_lut():
    svg = Svg(650, 330)
    regs = [dff(svg, 70 + 62 * k, 30, f"sr{k}", w=44, h=60) for k in range(8)]
    y = regs[0]["d"][1]
    svg.wire((30, y), regs[0]["d"]); svg.pin(30, y, "sin")
    for a, b in zip(regs, regs[1:]):
        svg.wire(a["q"], b["d"])
    ins, sel, out = mux(svg, 560, 210, 8, labels=[str(k) for k in range(7, -1, -1)])
    for k, r in enumerate(regs):
        qx = r["q"][0] + 6 if k < 7 else r["q"][0] + 8
        py = ins[7 - k][1]
        if k == 7:
            svg.wire(r["q"], (qx, y))
        svg.wire((qx, y), (qx, py), ins[7 - k])
        if k < 7:
            svg.dot(qx, y)
    svg.wire(sel, (sel[0], 318)); svg.pin(sel[0] + 4, 312, "addr", "right")
    svg.wire(out, (620, out[1])); svg.pin(620, out[1], "y", "right", "t a b")
    svg.text(30, 318, "shifts left when en = 1", "start", "t sm m")
    return svg.render("an 8-bit shift register whose taps feed an 8-to-1 mux")


def rule90():
    svg = Svg(520, 170)
    bw, x0 = 30, 80
    idx = ["0", 63, 62, 61, None, 32, 31, 30, None, 2, 1, 0, "0"]
    for k, i in enumerate(idx):
        x = x0 + k * bw
        if i is None:
            svg.text(x + bw / 2, 45, "…", "middle", "t m")
            continue
        edge = isinstance(i, str)
        svg.rect(x, 30, bw, 30, "s xf" if edge else ("s af" if i in (32, 30) else "s bg"))
        svg.text(x + bw / 2, 45, i, "middle", "t sm m" if edge else "t sm")
    svg.text(x0 - 10, 45, "q", "end")
    cx = x0 + 6 * bw + bw / 2
    svg.rect(cx - bw / 2, 110, bw, 30, "s af")
    svg.text(cx, 125, "31", "middle", "t sm b")
    svg.text(x0 - 10, 125, "next q", "end")
    svg.arrow((cx - bw, 60), (cx - 4, 108), cls="s thin")
    svg.arrow((cx + bw, 60), (cx + 4, 108), cls="s thin")
    svg.text(cx + 30, 92, "next q(31) = q(32) xor q(30)", "start", "t sm a")
    svg.text(x0, 160, "grey cells outside the ends always count as 0", "start", "t sm m")
    return svg.render("rule 90: each cell becomes the XOR of its two neighbours")


def rule30():
    svg = Svg(520, 130)
    for k in range(8):
        pat = 7 - k
        l, c, r = (pat >> 2) & 1, (pat >> 1) & 1, pat & 1
        nxt = l ^ (c | r)
        x = 20 + k * 62
        for j, v in enumerate((l, c, r)):
            svg.rect(x + j * 16, 20, 16, 16, "s k" if v else "s bg")
        svg.rect(x + 16, 54, 16, 16, "s k" if nxt else "s bg")
        svg.text(x + 24, 86, str(nxt), "middle", "t sm")
        svg.text(x + 24, 10, f"{l}{c}{r}", "middle", "t sm m")
    svg.text(20, 112, "top: left, center, right now; below: the center's next value (dark = 1)", "start", "t sm m")
    return svg.render("rule 30: the next value of a cell for each neighbourhood")


def life16():
    svg = Svg(540, 330)
    c, x0, y0 = 16, 40, 30
    hl = {(r % 16, cc % 16) for r in (-1, 0, 1) for cc in (-1, 0, 1)} - {(0, 0)}
    for r in range(16):
        for cc in range(16):
            cls = "s thin af" if (r, cc) in hl else ("s thin k" if (r, cc) == (0, 0) else "s thin bg")
            svg.rect(x0 + (15 - cc) * c, y0 + r * c, c, c, cls)
    for cc in (0, 15):
        svg.text(x0 + (15 - cc) * c + c / 2, y0 - 8, str(cc), "middle", "t sm m")
    for r in (0, 15):
        svg.text(x0 - 6, y0 + r * c + c / 2, str(r), "end", "t sm m")
    svg.text(x0 + 8 * c, 12, "column c (bit 0 on the right)", "middle", "t sm m")
    tx = x0 + 16 * c + 18
    for k, line in enumerate(["cell (r, c) is q(r*16 + c)", "", "dark: cell (0, 0) = q(0)",
                              "blue: its 8 neighbours,", "wrapping across both", "edges of the torus"]):
        svg.text(tx, 60 + 16 * k, line, "start", "t sm" if k == 0 else "t sm m")
    return svg.render("the 16 by 16 Life grid as a torus: neighbours wrap around both edges")


FIGURES = {
    "shift4": shift4(),
    "rotate8": [rotate(True), rotate(False)],
    "lfsr5": galois([4, 3, 2, 1, 0], {2}, "5-bit Galois LFSR with taps at 5 and 3", w_cell=130),
    "sipo8": sipo(),
    "piso8": piso(),
    "shift_n_generic": shift_n(),
    "lfsr32": galois([31, 30, None, 22, 21, 20, None, 2, 1, 0], {21, 1, 0},
                     w_cell=120, w_gap=50, title="32-bit Galois LFSR with taps at 32, 22, 2 and 1"),
    "tap_lut": tap_lut(),
    "rule90": rule90(),
    "rule30": rule30(),
    "life16": life16(),
}
