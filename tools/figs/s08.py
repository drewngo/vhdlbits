from diagrams import Svg, clocked, dff, gate, hv, mux, wave

H = "{:02X}".format


def dff_wave():
    rows = clocked(8, [("d", [0, 1, 1, 0, 1, 0, 0, 1])],
                   step=lambda q, i: i["d"], out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=22, outputs=("q",), title="q takes d at each rising edge of clk")


def sync_reset():
    ds = ["A1", "B2", "C3", "D4", "E5", "F6", "17", "28"]
    rows = clocked(8, [("reset", [0, 0, 0, 1, 0, 0, 0, 0]), ("d", ds)],
                   step=lambda q, i: "00" if i["reset"] else i["d"], out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=24, outputs=("q",),
                note="reset only acts at a rising edge", title="synchronous reset to 00")


def async_reset():
    ds = ["A1", "B2", "C3", "D4", "E5", "F6", "17", "28"]
    ar = [0] * 32
    for k in range(13, 19):
        ar[k] = 1                      # rises mid-cycle, falls mid-cycle
    rows = clocked(8, [("areset", ar), ("d", ds)], sub=4,
                   step=lambda q, i: q if i["areset"] else i["d"],
                   always=lambda q, i: "00" if i["areset"] else q,
                   out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=12, outputs=("q",),
                note="areset clears q at once, without waiting for an edge", title="asynchronous reset to 00")


def dff_enable():
    svg = Svg(420, 160)
    ins, sel, out = mux(svg, 130, 60)
    svg.wire((60, ins[1][1]), ins[1], cls="s bus"); svg.pin(60, ins[1][1], "d")
    svg.wire(sel, (sel[0], 112)); svg.pin(sel[0], 112, "en", "below")
    r = dff(svg, 220, 60 - 70 * .45)
    svg.wire(out, r["d"], cls="s bus")
    svg.wire(r["q"], (360, r["q"][1]), cls="s bus"); svg.pin(360, r["q"][1], "q", "right", "t a b")
    svg.wire((320, 60), (320, 14), (100, 14), (100, ins[0][1]), ins[0], cls="s bus")
    svg.dot(320, 60)
    svg.wire((60, 140), (200, 140), (200, r[">"][1]), r[">"]); svg.pin(60, 140, "clk")
    svg.text(400, 150, "reset (not drawn) wins over en", "end", "t sm m")
    return svg.render("clock enable: when en = 0 the register reloads its own value")


def edge_wave(title, fn, outname, din, extra=None):
    rows = clocked(len(din), [("din(i)", din)], step=lambda st, i: (i["din(i)"], fn(st[0], i["din(i)"])),
                   out=lambda st, i: {outname: st[1]}, state=(0, 0))
    return wave(rows, slot=22, outputs=(outname,), title=title)


def sticky():
    din = [1, 1, 0, 0, 1, 0, 1, 1, 0, 1]
    rst = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]

    def step(st, i):
        prev, cap = st
        new = 0 if i["reset"] else (cap or (prev and not i["din(i)"]))
        return (i["din(i)"], int(bool(new)))
    rows = clocked(10, [("reset", rst), ("din(i)", din)], step=step, out=lambda st, i: {"cap(i)": st[1]},
                   state=(0, 0))
    return wave(rows, slot=22, outputs=("cap(i)",), title="cap(i) is set by a falling edge of din(i) and held until reset")


def negedge():
    ds = ["A1", "B2", "C3", "D4", "E5", "F6", "17"]
    # inputs change at the rising edge here, so they are stable at the falling edge
    rows = clocked(7, [("reset", shift(4, [0, 1, 0, 0, 0, 0, 0])), ("d", shift(4, ds))], sub=4, edge="fall",
                   step=lambda q, i: "5A" if i["reset"] else i["d"], out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=12, outputs=("q",), grid=False,
                title="q updates on the falling edge of clk")


def shift(sub, per_cycle, offset=None):
    """Per-cycle values as per-slot values that change at the rising edge (slot sub/2) instead."""
    offset = sub // 2 if offset is None else offset
    out = []
    for i in range(len(per_cycle) * sub):
        k = (i - offset) // sub
        out.append(per_cycle[k] if k >= 0 else None)
    return out


def latch():
    en = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0]
    d = [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1]
    q, qs = None, []
    for e, v in zip(en, d):
        q = v if e else q
        qs.append(q)
    from diagrams import to_row
    rows = [to_row("en", en), to_row("d", d), to_row("q", qs)]
    return wave(rows, slot=20, outputs=("q",), title="a latch: q follows d while en = 1 and holds while en = 0")


def jk():
    rows = clocked(8, [("j", [1, 0, 0, 1, 1, 0, 1, 0]), ("k", [0, 0, 1, 1, 1, 0, 0, 1])],
                   step=lambda q, i: {(0, 0): q, (0, 1): 0, (1, 0): 1, (1, 1): 1 - q}[(i["j"], i["k"])],
                   out=lambda q, i: {"q": q}, state=0)
    return wave(rows, slot=22, outputs=("q",), title="JK flip-flop: hold, reset, set and toggle")


def tff():
    rows = clocked(9, [("reset", [1, 0, 0, 0, 0, 0, 0, 0, 0]), ("t", [0, 1, 0, 1, 1, 0, 1, 1, 1])],
                   step=lambda q, i: 0 if i["reset"] else q ^ i["t"], out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=22, outputs=("q",), title="T flip-flop: q inverts at each edge where t = 1")


def sync2():
    svg = Svg(470, 150)
    svg.rect(10, 10, 80, 100, "s thin ms dash", rx=4)
    svg.text(50, 26, "other", "middle", "t sm m")
    svg.text(50, 40, "clock", "middle", "t sm m")
    svg.text(50, 54, "domain", "middle", "t sm m")
    r1 = dff(svg, 160, 30, "")
    r2 = dff(svg, 280, 30, "")
    y = r1["d"][1]
    svg.wire((90, y), r1["d"]); svg.text(96, y - 10, "async_in", "start", "t sm")
    svg.wire(r1["q"], r2["d"]); svg.text(250, y - 10, "meta", "middle", "t sm m")
    svg.wire(r2["q"], (380, y)); svg.text(384, y, "sync_out", "start", "t a b")
    ck = 130
    svg.wire((140, ck), (266, ck))
    svg.text(136, ck, "clk", "end", "t sm")
    for r in (r1, r2):
        cx, cy = r[">"]
        svg.wire((cx - 14, ck), (cx - 14, cy), r[">"])
    return svg.render("two flip-flops in series on the receiving clock")


def dual_edge():
    halves = [0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0]
    d = [halves[(i - 1) // 2] if i else 0 for i in range(24)]    # changes between the edges
    rows = clocked(6, [("d", d)], sub=4, edge="both", step=lambda q, i: i["d"],
                   out=lambda q, i: {"q": q}, state=None)
    return wave(rows, slot=14, outputs=("q",), grid=False,
                title="q takes d at both the rising and the falling edge of clk")


def pipeline():
    svg = Svg(560, 215)
    add = (130, 60)
    svg.circle(*add, 18); svg.text(*add, "+", "middle", "t b")
    svg.wire((40, 50), (114, 50), cls="s bus"); svg.pin(40, 50, "a")
    svg.wire((40, 70), (114, 70), cls="s bus"); svg.pin(40, 70, "b")
    r1 = dff(svg, 180, 60 - 70 * .45, "stage 1", w=64)
    svg.wire((148, 60), r1["d"], cls="s bus")
    rc = dff(svg, 180, 150 - 70 * .45, "", w=64)
    svg.wire((40, 150), rc["d"], cls="s bus"); svg.pin(40, 150, "c")
    mul = (310, 95)
    svg.circle(*mul, 18); svg.text(*mul, "×", "middle", "t b")
    svg.wire(*hv(r1["q"], (293, 88), 272), cls="s bus")
    svg.wire(*hv(rc["q"], (293, 102), 272), cls="s bus")
    svg.text(258, 172, "c delayed to match", "start", "t sm m")
    r2 = dff(svg, 370, 95 - 70 * .45, "stage 2", w=64)
    svg.wire((328, 95), r2["d"], cls="s bus")
    svg.wire(r2["q"], (500, 95), cls="s bus"); svg.pin(500, 95, "y", "right", "t a b")
    svg.text(280, 204, "clk and reset go to every register", "middle", "t sm m")
    return svg.render("a two-stage pipeline: register after the add and after the multiply")


FIGURES = {
    "dff": dff_wave(),
    "dff8_sync_reset": sync_reset(),
    "dff8_async_reset": async_reset(),
    "dff_enable": dff_enable(),
    "rise_detect": edge_wave("pulse(i) is high for one cycle after din(i) rises",
                             lambda prev, d: int(d and not prev), "pulse(i)", [0, 1, 1, 1, 0, 0, 1, 0, 1, 1]),
    "any_edge": edge_wave("pulse(i) is high for one cycle after din(i) changes",
                          lambda prev, d: int(d != prev), "pulse(i)", [0, 1, 1, 1, 0, 0, 1, 0, 1, 1]),
    "sticky_capture": sticky(),
    "dff_negedge": negedge(),
    "d_latch": latch(),
    "jk_ff": jk(),
    "t_ff": tff(),
    "sync2": sync2(),
    "dual_edge": dual_edge(),
    "pipeline3": pipeline(),
}
