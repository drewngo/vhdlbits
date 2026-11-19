from diagrams import Svg, dff, gate, hv, mux, wave


def clocked_process():
    svg = Svg(380, 170)
    gi, go = gate(svg, "xor", 70, 50)
    for nm, p in zip("ab", gi):
        svg.wire((30, p[1]), p); svg.pin(30, p[1], nm)
    svg.wire(go, (320, 50)); svg.pin(320, 50, "y_conc", "right", "t a b")
    svg.dot(150, 50)
    svg.wire((150, 50), (150, 80), (320, 80)); svg.pin(320, 80, "y_comb", "right", "t a b")
    svg.dot(150, 80)
    r = dff(svg, 210, 120 - 70 * .45, "", w=50, h=60)
    svg.wire((150, 80), (150, r["d"][1]), r["d"])
    svg.wire(r["q"], (320, r["q"][1])); svg.pin(320, r["q"][1], "y_ff", "right", "t a b")
    svg.wire((30, r[">"][1]), r[">"]); svg.pin(30, r[">"][1], "clk")
    return svg.render("a xor b drives y_conc and y_comb directly, and y_ff through a flip-flop")


def if_mux():
    svg = Svg(400, 160)
    ins, sel, out = mux(svg, 200, 50)
    svg.wire((40, ins[0][1]), ins[0]); svg.pin(40, ins[0][1], "a")
    svg.wire((40, ins[1][1]), ins[1]); svg.pin(40, ins[1][1], "b")
    gi, go = gate(svg, "and", 100, 120)
    for nm, p in zip(("sel1", "sel2"), gi):
        svg.wire((60, p[1]), p); svg.pin(60, p[1], nm)
    svg.wire(go, (sel[0], go[1]), sel)
    svg.wire(out, (290, out[1])); svg.pin(290, out[1], "y_when, y_if", "right", "t a b")
    return svg.render("b is selected only when sel1 and sel2 are both 1")


def wide_mux(nin, names, sel, out, title, bus=True, w=300):
    h = 20 * nin + 70
    svg = Svg(w, h)
    ins, s, o = mux(svg, 140, 10 + (20 * nin + 16) / 2, nin, w=40)
    cls = "s bus" if bus else "s"
    for nm, p in zip(names, ins):
        svg.wire((90, p[1]), p, cls=cls); svg.pin(90, p[1], nm)
    svg.wire(s, (s[0], h - 22), cls=cls); svg.pin(s[0], h - 22, sel, "below")
    svg.wire(o, (230, o[1]), cls=cls); svg.pin(230, o[1], out, "right", "t a b")
    return svg.render(title)


def variables_vs_signals():
    return wave([
        ("clk", "0pppp"),
        ("a xor b", "10111"),
        ("c", "11100"),
        ("t (signal)", "x1011"),
        ("y_var", "x1010"),
        ("y_sig", "xx100"),
    ], slot=56, outputs=("y_var", "y_sig"), ticks={1: "edge 1", 2: "edge 2", 3: "edge 3", 4: "edge 4"},
        note="y_sig uses t from the previous edge; y_var uses this edge's a xor b",
        title="y_var vs y_sig over four clock edges")


def procedure_swap():
    svg = Svg(420, 150)
    ys = {"x": 30, "y": 75, "z": 120}
    outs = {"x": "s0", "y": "s1", "z": "s2"}
    for nm, y in ys.items():
        svg.wire((60, y), (340, y))
        svg.pin(60, y, nm)
        svg.pin(340, y, outs[nm], "right", "t a b")
    for k, (a, b) in enumerate((("x", "y"), ("y", "z"), ("x", "y"))):
        cx = 130 + 80 * k
        svg.line(cx, ys[a], cx, ys[b])
        svg.dot(cx, ys[a]); svg.dot(cx, ys[b])
        svg.text(cx, 142, f"step {k + 1}", "middle", "t sm m")
    svg.text(200, 10, "each | is compare_swap: the smaller value goes up", "middle", "t sm m")
    return svg.render("a three-input sorting network made of three compare-and-swap steps")


FIGURES = {
    "clocked_process": clocked_process(),
    "if_mux": if_mux(),
    "case_mux": wide_mux(8, ["d0", "d1", "d2", "d3", "d4", "d5", '"0000"', '"0000"'], "sel", "y",
                         "a 6-to-1 mux; sel = 6 or 7 gives 0000"),
    "variables_vs_signals": variables_vs_signals(),
    "with_select": wide_mux(4, ["d0", "d1", "d2", "d3"], "sel", "y", "a 4-to-1 mux of 8-bit values"),
    "procedure_swap": procedure_swap(),
}
