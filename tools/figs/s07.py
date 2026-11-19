from diagrams import Svg, mux, ripple, wave


def seven_seg():
    svg = Svg(380, 190)
    x, y, L, t = 70, 16, 66, 18      # top-left, segment length, thickness

    def seg_h(sx, sy, name):
        svg.poly([(sx, sy), (sx + t / 2, sy - t / 2), (sx + L - t / 2, sy - t / 2), (sx + L, sy),
                  (sx + L - t / 2, sy + t / 2), (sx + t / 2, sy + t / 2)], "s af", closed=True)
        svg.text(sx + L / 2, sy, name, "middle", "t sm b")

    def seg_v(sx, sy, name):
        svg.poly([(sx, sy), (sx + t / 2, sy + t / 2), (sx + t / 2, sy + L - t / 2), (sx, sy + L),
                  (sx - t / 2, sy + L - t / 2), (sx - t / 2, sy + t / 2)], "s af", closed=True)
        svg.text(sx, sy + L / 2, name, "middle", "t sm b")
    g = 4
    seg_h(x + g, y, "a")
    seg_v(x + L + 2 * g, y + g, "b")
    seg_v(x + L + 2 * g, y + L + 3 * g, "c")
    seg_h(x + g, y + 2 * L + 4 * g, "d")
    seg_v(x, y + L + 3 * g, "e")
    seg_v(x, y + g, "f")
    seg_h(x + g, y + L + 2 * g, "g")
    tx = 200
    svg.text(tx, 50, "seg(6 downto 0)", "start", "t sm m")
    for k, nm in enumerate("gfedcba"):
        svg.rect(tx + 22 * k, 62, 22, 24, "s bg")
        svg.text(tx + 22 * k + 11, 74, nm, "middle", "t sm")
        svg.text(tx + 22 * k + 11, 96, str(6 - k), "middle", "t sm m")
    svg.text(tx, 130, "active-low: 0 lights", "start", "t sm m")
    svg.text(tx, 146, "a segment", "start", "t sm m")
    return svg.render("seven-segment display: segments a to g, and their bit positions in seg")


def time_wave(rows, cols, data, step=10, slot=40, title="trace"):
    """A trace table as a waveform: rows = signal names, data = per-time tuples of values."""
    sigs = []
    for k, nm in enumerate(rows):
        vals = [d[k] for d in data]
        if all(v in "01" for v in vals):
            sigs.append((nm, "".join(vals)))
        else:
            sigs.append((nm, "=" * len(vals), vals))
    ticks = {i: f"{i * step}" for i in range(0, len(data), 2)}
    return wave(sigs, slot=slot, ticks=ticks, outputs=("q",), grid=False, title=title,
                note="time in ns")


def puzzle1():
    data = ["1011", "0000", "0111", "1100", "0010", "1111", "0100", "1001"]
    return time_wave("abcq", None, data, title="waveform of a, b, c and q")


def puzzle2():
    data = ["10011", "00100", "11100", "00000", "01111", "10111", "01000", "11010",
            "00010", "10001", "11110", "01101", "00110", "10101", "11001", "01011"]
    return time_wave("abcdq", None, data, slot=30, title="waveform of a, b, c, d and q")


def puzzle_vec():
    xs = "1001 0010 1110 0000 0111 1011 0100 1101 0001 1000 1111 0110 0011 1010 1100 0101".split()
    qs = "1111 0010 1101 0111 1011 0001 1110 0110 1100 0011 0100 0101 1001 1000 1010 0000".split()
    return wave([("x", "=" * 16, xs), ("q", "=" * 16, qs)], slot=42, outputs=("q",), grid=False,
                ticks={i: str(10 * i) for i in range(0, 16, 2)}, note="time in ns",
                title="waveform of x and q")


def mux2_wide():
    svg = Svg(280, 120)
    ins, sel, out = mux(svg, 120, 50)
    for nm, p in zip("ab", ins):
        svg.wire((60, p[1]), p, cls="s bus"); svg.pin(60, p[1], nm)
    svg.wire(sel, (sel[0], 100)); svg.pin(sel[0], 100, "sel", "below")
    svg.wire(out, (220, out[1]), cls="s bus"); svg.pin(220, out[1], "y", "right", "t a b")
    return svg.render("a 100-bit 2-to-1 mux")


FIGURES = {
    "adder4_loop": ripple([3, 2, 1, 0], carry=lambda i: f"c{i + 1}", out=lambda i: f"sum({i})",
                          title="a 4-bit ripple-carry adder: the loop computes one stage per iteration"),
    "seven_seg": seven_seg(),
    "mux2_wide": mux2_wide(),
    "wave_puzzle_comb1": puzzle1(),
    "wave_puzzle_comb2": puzzle2(),
    "wave_puzzle_vec": puzzle_vec(),
}
