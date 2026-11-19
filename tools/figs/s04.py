from diagrams import Svg, bitfield, box, dff, frame, gate, hv, mux, ripple


def instantiate(title="top_module instantiates mod_a as u0"):
    svg = Svg(380, 140)
    frame(svg, 60, 10, 260, 120)
    p = box(svg, 150, 34, 100, 80, "u0: mod_a", left=[("in1", .5), ("in2", .78)], right=[("o", .64)],
            title_y=48)
    for name, pin in (("a", "in1"), ("b", "in2")):
        svg.wire((60, p[pin][1]), p[pin])
        svg.pin(60, p[pin][1], name)
    svg.wire(p["o"], (320, p["o"][1]))
    svg.pin(320, p["o"][1], "y", "right", "t a b")
    return svg.render(title)


def positional_map():
    svg = Svg(400, 170)
    frame(svg, 60, 10, 280, 150)
    p = box(svg, 150, 35, 110, 110, "mod_b", left=["w", "x", "y", "z"], right=["o1", "o2"], title_y=48)
    for name, pin in zip("abcd", "wxyz"):
        svg.wire((60, p[pin][1]), p[pin])
        svg.pin(60, p[pin][1], name)
    for pin, name in (("o1", "out1"), ("o2", "out2")):
        svg.wire(p[pin], (340, p[pin][1]))
        svg.pin(340, p[pin][1], name, "right", "t a b")
    return svg.render("a, b, c, d connect to w, x, y, z of mod_b by position")


def three_dffs():
    svg = Svg(520, 160)
    frame(svg, 50, 10, 430, 140)
    regs = [dff(svg, 110 + 130 * k, 34, "my_dff") for k in range(3)]
    svg.wire((50, regs[0]["d"][1]), regs[0]["d"]); svg.pin(50, regs[0]["d"][1], "d")
    for k, nm in enumerate(["q1", "q2"]):
        a, b = regs[k]["q"], regs[k + 1]["d"]
        svg.wire(a, b)
        svg.text((a[0] + b[0]) / 2 - 8, a[1] - 10, nm, "middle", "t sm m")
    svg.wire(regs[2]["q"], (480, regs[2]["q"][1])); svg.pin(480, regs[2]["q"][1], "q", "right", "t a b")
    clock_bus(svg, regs, 50, 128)
    return svg.render("three my_dff instances chained: d -> q1 -> q2 -> q")


def clock_bus(svg, regs, x0, y):
    """clk enters at x0 along y and rises into every register's clock pin."""
    last = regs[-1][">"][0] - 14
    svg.wire((x0, y), (last, y)); svg.pin(x0, y, "clk")
    for k, r in enumerate(regs):
        cx, cky = r[">"]
        svg.wire((cx - 14, y), (cx - 14, cky), (cx, cky))
        if k < len(regs) - 1:
            svg.dot(cx - 14, y)


def tap_select():
    svg = Svg(580, 270)
    frame(svg, 40, 10, 500, 250)
    regs = [dff(svg, 110 + 120 * k, 30, "dff8") for k in range(3)]
    dy = regs[0]["d"][1]
    svg.wire((40, dy), regs[0]["d"], cls="s bus"); svg.pin(40, dy, "d")
    for k in range(2):
        svg.wire(regs[k]["q"], regs[k + 1]["d"], cls="s bus")
    clock_bus(svg, regs, 40, 118)
    ins, sel, out = mux(svg, 450, 195, 4, labels=["3", "2", "1", "0"])
    taps = [(70, "d"), (200, "q1"), (320, "q2"), (420, "q3")]
    svg.wire(regs[2]["q"], (420, dy), cls="s bus")
    for (tx, nm), (px, py) in zip(taps, reversed(ins)):
        svg.wire((tx, dy), (tx, py), (px, py), cls="s bus")
        if tx < 420:
            svg.dot(tx, dy)
        svg.text(tx + 6, py - 9, nm, "start", "t sm m")
    svg.wire(sel, (sel[0], 252)); svg.pin(sel[0] + 4, 246, "sel", "right")
    svg.wire(out, (540, out[1]), cls="s bus"); svg.pin(540, out[1], "q", "right", "t a b")
    return svg.render("three 8-bit registers in a chain; sel picks d, q1, q2 or q3")


def add16_stack(svg, x, y, low_cin="'0'", hi_cout="(unused)", bsrc="b"):
    """Two add16 boxes, the upper half above the lower one, carry going up between them."""
    hi = box(svg, x, y, 120, 70, "add16", left=["a", "b"], right=["sum"], top=["cout"], bottom=["cin"])
    lo = box(svg, x, y + 120, 120, 70, "add16", left=["a", "b"], right=["sum"], top=["cout"],
             bottom=["cin"])
    svg.wire(lo["cout"], hi["cin"])
    svg.text(lo["cout"][0] + 6, (lo["cout"][1] + hi["cin"][1]) / 2, "carry", "start", "t sm m")
    for blk, rng in ((hi, "31:16"), (lo, "15:0")):
        for port, src in (("a", "a"), ("b", bsrc)):
            svg.wire((x - 70, blk[port][1]), blk[port], cls="s bus")
            svg.text(x - 74, blk[port][1], f"{src}({rng})", "end", "t sm")
        svg.wire(blk["sum"], (x + 170, blk["sum"][1]), cls="s bus")
        svg.text(x + 174, blk["sum"][1], f"sum({rng})", "start", "t sm a b")
    svg.wire(hi["cout"], (hi["cout"][0], y - 16))
    svg.text(hi["cout"][0], y - 22, hi_cout, "middle", "t sm m")
    svg.wire(lo["cin"], (lo["cin"][0], y + 120 + 70 + 16))
    svg.text(lo["cin"][0], y + 120 + 70 + 26, low_cin, "middle", "t sm")
    return hi, lo


def adder32():
    svg = Svg(440, 290)
    add16_stack(svg, 150, 40)
    return svg.render("a 32-bit adder from two add16: the lower half's carry-out feeds the upper half's cin")


def carry_select():
    svg = Svg(620, 380)
    x = 150
    u0 = box(svg, x, 20, 110, 64, "add16", left=["a", "b"], right=["sum"], bottom=["cin"])
    u1 = box(svg, x, 130, 110, 64, "add16", left=["a", "b"], right=["sum"], bottom=["cin"])
    lo = box(svg, x, 260, 110, 64, "add16", left=["a", "b"], right=["sum"], top=["cout"], bottom=["cin"])
    for blk, rng in ((u0, "31:16"), (u1, "31:16"), (lo, "15:0")):
        for port in ("a", "b"):
            svg.wire((x - 50, blk[port][1]), blk[port], cls="s bus")
            svg.text(x - 54, blk[port][1], f"{port}({rng})", "end", "t sm")
    for blk, v in ((u0, "'0'"), (u1, "'1'"), (lo, "'0'")):
        svg.wire(blk["cin"], (blk["cin"][0], blk["cin"][1] + 14))
        svg.text(blk["cin"][0], blk["cin"][1] + 24, v, "middle", "t sm")
    ins, sel, out = mux(svg, 380, 107, 2)
    svg.wire(*hv(u0["sum"], ins[0], 340), cls="s bus")
    svg.wire(*hv(u1["sum"], ins[1], 362), cls="s bus")
    svg.text(268, u0["sum"][1] - 9, "sum if c=0", "start", "t sm m")
    svg.text(268, u1["sum"][1] - 9, "sum if c=1", "start", "t sm m")
    svg.wire(lo["cout"], (lo["cout"][0], 235), (sel[0], 235), sel)
    svg.text(sel[0] + 6, 222, "c (lower carry-out)", "start", "t sm m")
    svg.wire(out, (470, out[1]), cls="s bus"); svg.pin(470, out[1], "sum(31:16)", "right", "t a b")
    svg.wire(lo["sum"], (470, lo["sum"][1]), cls="s bus"); svg.pin(470, lo["sum"][1], "sum(15:0)", "right",
                                                                   "t a b")
    return svg.render("carry-select adder: both upper sums are computed, the lower carry-out picks one")


def generic_map():
    svg = Svg(420, 190)
    frame(svg, 50, 10, 320, 170)
    r4 = dff(svg, 160, 26, "reg_n  N => 4", w=110, h=64)
    r12 = dff(svg, 160, 104, "reg_n  N => 12", w=110, h=64)
    for blk, dn, qn in ((r4, "d4", "q4"), (r12, "d12", "q12")):
        svg.wire((50, blk["d"][1]), blk["d"], cls="s bus"); svg.pin(50, blk["d"][1], dn)
        svg.wire(blk["q"], (370, blk["q"][1]), cls="s bus"); svg.pin(370, blk["q"][1], qn, "right", "t a b")
    svg.wire((50, 172), (130, 172), (130, r12[">"][1]), r12[">"]); svg.pin(50, 172, "clk")
    svg.wire((130, r12[">"][1]), (130, r4[">"][1]), r4[">"]); svg.dot(130, r12[">"][1])
    return svg.render("two copies of reg_n with different generic N")


def own_generic():
    return bitfield([
        ("din", [("din(W-1)", None, 2), ("din(W-2 downto 0)", None, 6)]),
        ("dout", [("din(W-2 downto 0)", None, 6, "a"), ("din(W-1)", None, 2, "a")]),
    ], bw=30, gap=50, numbers=False, links=[((0, 0), (1, 1)), ((0, 1), (1, 0))],
        title="rotate left by one: the MSB wraps around to bit 0")


def if_generate():
    svg = Svg(560, 150)
    for k, (head, reg) in enumerate((("REGISTERED = true", True), ("REGISTERED = false", False))):
        ox = 280 * k
        svg.text(ox + 130, 16, head, "middle", "t sm m b")
        gi, go = gate(svg, "and", ox + 60, 60)
        for nm, p in zip("ab", gi):
            svg.wire((ox + 30, p[1]), p); svg.pin(ox + 30, p[1], nm)
        if reg:
            r = dff(svg, ox + 140, 60 - 70 * .45, "", w=50)
            svg.wire(go, r["d"])
            svg.wire(r["q"], (ox + 230, r["q"][1])); svg.pin(ox + 230, r["q"][1], "y", "right", "t a b")
            svg.wire((ox + 30, r[">"][1]), r[">"])
            svg.pin(ox + 30, r[">"][1], "clk")
        else:
            svg.wire(go, (ox + 230, go[1])); svg.pin(ox + 230, go[1], "y", "right", "t a b")
    return svg.render("the generic chooses between a registered and a combinational AND")


def two_level_hier():
    svg = Svg(470, 190)
    frame(svg, 50, 10, 370, 170)
    u1 = box(svg, 120, 30, 80, 70, "sum3", left=["a", "b", "c"], right=["y"])
    u2 = box(svg, 260, 90, 80, 70, "sum3", left=["a", "b", "c"], right=["y"])
    for nm, pin in zip("abc", "abc"):
        svg.wire((50, u1[pin][1]), u1[pin]); svg.pin(50, u1[pin][1], nm)
    svg.wire(u1["y"], (420, u1["y"][1])); svg.pin(420, u1["y"][1], "y1", "right", "t a b")
    svg.dot(230, u1["y"][1])
    svg.wire((230, u1["y"][1]), (230, u2["a"][1]), u2["a"])
    for nm, pin in (("d", "b"), ("e", "c")):
        svg.wire((50, u2[pin][1]), u2[pin]); svg.pin(50, u2[pin][1], nm)
    svg.wire(u2["y"], (420, u2["y"][1])); svg.pin(420, u2["y"][1], "y2", "right", "t a b")
    return svg.render("two sum3 instances: y1 = sum3(a, b, c), y2 = sum3(y1, d, e)")


def add_sub():
    svg = Svg(560, 335)
    hi, lo = add16_stack(svg, 300, 60, low_cin="sub", bsrc="b'")
    gi, go = gate(svg, "xor", 50, 290)
    svg.wire((14, gi[0][1]), gi[0], cls="s bus"); svg.text(14, gi[0][1] - 10, "b", "start", "t sm")
    svg.wire((14, gi[1][1]), gi[1]); svg.text(14, gi[1][1] + 11, "sub", "start", "t sm")
    svg.text(14, 322, "b' = b xor (sub, sub, ..., sub)", "start", "t sm m")
    svg.wire(go, (230, go[1]), (230, hi["b"][1]), cls="s bus")
    svg.dot(230, lo["b"][1])
    return svg.render("add/subtract: b is XORed with sub, and sub is the carry-in")


FIGURES = {
    "instantiate": instantiate(),
    "positional_map": positional_map(),
    "three_dffs": three_dffs(),
    "tap_select": tap_select(),
    "adder32": adder32(),
    "carry_select": carry_select(),
    "generic_map": generic_map(),
    "generate_adder": ripple([7, None, 1, 0], carry=lambda i: f"couts({i})", cout="couts(7)", gap=72,
                             out=lambda i: f"sum({i})",
                             title="8 full adders generated in a ripple chain; every carry is also an output"),
    "add_sub": add_sub(),
    "component_decl": instantiate("the same circuit as 4.1, instantiated through a component declaration"),
    "adder100_generate": ripple([99, 98, None, 1, 0], carry=lambda i: f"couts({i})", cout="couts(99)", gap=72,
                                out=lambda i: f"sum({i})", title="a 100-stage ripple-carry adder"),
    "bcd_ripple4": ripple([3, 2, 1, 0], bus=True, cell="bcd_fadd ", cw=96,
                          ins=lambda i: (f"a({4 * i + 3}:{4 * i})", f"b({4 * i + 3}:{4 * i})"),
                          out=lambda i: f"sum({4 * i + 3}:{4 * i})", gap=50,
                          title="four BCD digit adders in a ripple chain"),
    "own_generic": own_generic(),
    "if_generate": if_generate(),
    "two_level_hier": two_level_hier(),
}
