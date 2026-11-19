from diagrams import Svg, gate, hv


def one_gate(kind, ins, out, title):
    """Inputs on the left, one gate, the output on the right."""
    h = 70 if len(ins) < 3 else 90
    svg = Svg(240, h)
    gi, go = gate(svg, kind, 90, h / 2, len(ins))
    for name, (px, py) in zip(ins, gi):
        svg.wire((40, py), (px, py))
        svg.pin(40, py, name)
    svg.wire(go, (200, go[1]))
    svg.pin(200, go[1], out, "right", "t a b")
    return svg.render(title)


def wire_fig():
    svg = Svg(200, 50)
    svg.wire((40, 25), (160, 25))
    svg.pin(40, 25, "a")
    svg.pin(160, 25, "y", "right", "t a b")
    return svg.render("a wire from a to y")


def fanout():
    svg = Svg(230, 150)
    ys = {"p": 25, "q": 55, "r": 85, "s": 120}
    # c -> p, a -> q and r, b -> s
    svg.wire((40, 25), (180, 25)); svg.pin(40, 25, "c")
    svg.wire((40, 70), (100, 70)); svg.pin(40, 70, "a")
    svg.wire((100, 55), (100, 85))
    svg.wire((100, 55), (180, 55)); svg.wire((100, 85), (180, 85)); svg.dot(100, 70)
    svg.wire((40, 120), (180, 120)); svg.pin(40, 120, "b")
    for k, y in ys.items():
        svg.pin(180, y, k, "right", "t a b")
    return svg.render("c drives p, a drives q and r, b drives s")


def internal_signals():
    svg = Svg(400, 150)
    a1, ao = gate(svg, "and", 80, 40)
    b1, bo = gate(svg, "and", 80, 110)
    o1, oo = gate(svg, "or", 190, 75)
    for name, p in zip("ab", a1):
        svg.wire((40, p[1]), p); svg.pin(40, p[1], name)
    for name, p in zip("cd", b1):
        svg.wire((40, p[1]), p); svg.pin(40, p[1], name)
    svg.wire(*hv(ao, o1[0], 160))
    svg.wire(*hv(bo, o1[1], 160))
    svg.wire(oo, (360, oo[1]))
    svg.dot(260, 75)
    svg.text(250, 62, "or_out", "middle", "t sm m")
    svg.wire((260, 75), (260, 120), (290, 120))
    n1, no = gate(svg, "not", 290, 120)
    svg.wire(no, (360, 120))
    svg.pin(360, 75, "y", "right", "t a b")
    svg.pin(360, 120, "y_n", "right", "t a b")
    return svg.render("y = (a and b) or (c and d), and y_n = not y")


def two_gate_chip():
    svg = Svg(420, 300)
    g1, o1 = gate(svg, "and", 100, 45, 3)
    g2, o2 = gate(svg, "and", 100, 115, 3)
    g3, o3 = gate(svg, "and", 100, 195)
    g4, o4 = gate(svg, "and", 100, 255)
    names = [["p1a", "p1b", "p1c"], ["p1d", "p1e", "p1f"], ["p2a", "p2b"], ["p2c", "p2d"]]
    for ns, gi in zip(names, [g1, g2, g3, g4]):
        for nm, p in zip(ns, gi):
            svg.wire((50, p[1]), p); svg.pin(50, p[1], nm)
    r1, ro1 = gate(svg, "or", 230, 80)
    r2, ro2 = gate(svg, "or", 230, 225)
    svg.wire(*hv(o1, r1[0], 200)); svg.wire(*hv(o2, r1[1], 200))
    svg.wire(*hv(o3, r2[0], 200)); svg.wire(*hv(o4, r2[1], 200))
    svg.wire(ro1, (360, 80)); svg.pin(360, 80, "p1y", "right", "t a b")
    svg.wire(ro2, (360, 225)); svg.pin(360, 225, "p2y", "right", "t a b")
    return svg.render("two AND-OR halves: p1y from three-input ANDs, p2y from two-input ANDs")


def mux2():
    from diagrams import mux
    svg = Svg(240, 120)
    ins, sel, out = mux(svg, 100, 50)
    svg.wire((50, ins[0][1]), ins[0]); svg.pin(50, ins[0][1], "a")
    svg.wire((50, ins[1][1]), ins[1]); svg.pin(50, ins[1][1], "b")
    svg.wire(sel, (sel[0], 100)); svg.pin(sel[0], 100, "s", "below")
    svg.wire(out, (190, out[1])); svg.pin(190, out[1], "y", "right", "t a b")
    return svg.render("2-to-1 mux: y = a when s = 0, b when s = 1")


def tristate():
    svg = Svg(240, 100)
    gi, go = gate(svg, "buf", 100, 40)
    svg.wire((50, 40), gi[0]); svg.pin(50, 40, "a")
    svg.wire((114, 47), (114, 80)); svg.pin(114, 80, "en", "below")
    svg.wire(go, (190, 40)); svg.pin(190, 40, "y", "right", "t a b")
    return svg.render("tri-state buffer: y = a when en = 1, otherwise Z")


FIGURES = {
    "wire": wire_fig(),
    "fanout": fanout(),
    "notgate": one_gate("not", ["a"], "y", "NOT gate"),
    "andgate": one_gate("and", ["a", "b"], "y", "AND gate"),
    "norgate": one_gate("nor", ["a", "b"], "y", "NOR gate"),
    "xnorgate": one_gate("xnor", ["a", "b"], "y", "XNOR gate"),
    "internal_signals": internal_signals(),
    "two_gate_chip": two_gate_chip(),
    "xor3": one_gate("xor", ["a", "b", "c"], "y", "three-input XOR"),
    "mux2_gates": mux2(),
    "tristate": tristate(),
}
