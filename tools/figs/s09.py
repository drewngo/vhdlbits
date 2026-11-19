from diagrams import Svg, box, clocked, dff, gate, wave


def counter_wave(n, inputs, step, out, state, title, note=None, slot=17, outputs=("q",)):
    rows = clocked(n, inputs, step=step, out=out, state=state)
    return wave(rows, slot=slot, outputs=outputs, title=title, note=note)


def count16():
    return counter_wave(10, [("reset", [0, 0, 0, 0, 0, 0, 1, 0, 0, 0])],
                        step=lambda q, i: 0 if i["reset"] else (q + 1) % 16, out=lambda q, i: {"q": q},
                        state=12, title="a 4-bit counter wraps from 15 to 0; reset returns it to 0")


def decade():
    return counter_wave(10, [("reset", [0, 0, 0, 0, 0, 0, 0, 1, 0, 0])],
                        step=lambda q, i: 0 if i["reset"] else (q + 1) % 10, out=lambda q, i: {"q": q},
                        state=6, title="a decade counter: 0 to 9, then back to 0")


def count_en_tc():
    return counter_wave(8, [("en", [1, 1, 0, 1, 1, 1, 0, 1])],
                        step=lambda q, i: (q + i["en"]) % 256,
                        out=lambda q, i: {"q": q, "tc": int(q == 255 and i["en"] == 1)},
                        state=252, slot=20, outputs=("q", "tc"),
                        title="the counter advances only when en = 1; tc is high when q = 255 and en = 1")


def tick_gen():
    return counter_wave(12, [("reset", [1] + [0] * 11)],
                        step=lambda c, i: 0 if i["reset"] else (c + 1) % 5,
                        out=lambda c, i: {"count": c, "tick": int(c == 4)}, state=None, outputs=("tick",),
                        title="tick is high for one cycle in every five", note="count is internal")


def bcd_counter2():
    def step(st, i):
        t, o = st
        if i["reset"]:
            return (0, 0)
        if not i["en"]:
            return st
        return ((t + (o == 9)) % 10, (o + 1) % 10)
    return counter_wave(9, [("reset", [0] * 9), ("en", [1, 1, 1, 0, 1, 1, 1, 1, 1])], step=step,
                        out=lambda st, i: {"tens": st[0], "ones": st[1]}, state=(1, 7), outputs=("tens", "ones"),
                        title="two cascaded BCD digits: tens advances when ones rolls over from 9")


def clock_hms():
    def step(t, i):
        if not i["en"]:
            return t
        h, m, s = t
        s += 1
        if s == 60:
            s, m = 0, m + 1
        if m == 60:
            m, h = 0, h + 1
        if h == 24:
            h = 0
        return (h, m, s)
    rows = clocked(5, [("en", [1, 1, 1, 0, 1])], step=step,
                   out=lambda t, i: {"hh": f"{t[0]:02d}", "mm": f"{t[1]:02d}", "ss": f"{t[2]:02d}"},
                   state=(23, 59, 57))
    return wave(rows, slot=26, outputs=("hh", "mm", "ss"), note="values shown as decimal digits (BCD)",
                title="23:59:59 rolls over to 00:00:00")


def count_1_to_12():
    return counter_wave(9, [("reset", [0, 0, 0, 0, 0, 0, 1, 0, 0])],
                        step=lambda q, i: 1 if i["reset"] else q % 12 + 1, out=lambda q, i: {"q": q},
                        state=10, title="counts 1 to 12; reset goes to 1")


def updown():
    return counter_wave(8, [("en", [1, 1, 1, 1, 1, 0, 1, 1]), ("up", [1, 1, 0, 0, 0, 0, 0, 1])],
                        step=lambda q, i: (q + (1 if i["up"] else -1)) % 256 if i["en"] else q,
                        out=lambda q, i: {"q": q}, state=254, slot=20,
                        title="up/down counter wrapping both ways")


def countdown():
    def step(q, i):
        if i["reset"]:
            return 0
        if i["load"]:
            return i["d"]
        return max(q - 1, 0)
    return counter_wave(9, [("reset", [0] * 9), ("load", [0, 1, 0, 0, 0, 0, 0, 1, 0]),
                            ("d", [None, 3, None, None, None, None, None, 5, None])],
                        step=step, out=lambda q, i: {"q": q, "done": int(q == 0)}, state=0,
                        outputs=("q", "done"), title="load, count down to 0 and stop; done while q = 0")


def slowena():
    return counter_wave(10, [("slowena", [0, 1, 0, 0, 1, 0, 0, 1, 0, 0])],
                        step=lambda q, i: (q + i["slowena"]) % 10, out=lambda q, i: {"q": q}, state=8,
                        title="the counter advances only on edges where slowena = 1")


def div1000():
    svg = Svg(650, 220)
    pins = [box(svg, 90 + 180 * k, 40, 90, 70, f"c{k}", left=[("en", .65)], right=[("=9", .65)],
                title_y=56) for k in range(3)]
    for k in range(3):
        svg.text(135 + 180 * k, 76, "0 to 9", "middle", "t sm m")
    y = pins[0]["en"][1]
    svg.wire((30, y), pins[0]["en"]); svg.text(26, y, "'1'", "end", "t sm")
    svg.text(60, y - 12, "enables(0)", "middle", "t sm a")
    svg.wire(pins[0]["=9"], pins[1]["en"]); svg.text(225, y - 12, "enables(1)", "middle", "t sm a")
    g1, o1 = gate(svg, "and", 390, 170)
    svg.dot(200, y); svg.wire((200, y), (200, g1[1][1]), g1[1])
    svg.wire(pins[1]["=9"], (375, y), (375, g1[0][1]), g1[0])
    svg.wire(o1, (440, o1[1]), (440, y), pins[2]["en"])
    svg.text(440, 205, "enables(2)", "middle", "t sm a")
    g2, o2 = gate(svg, "and", 570, 170)
    svg.dot(440, o1[1]); svg.wire((440, o1[1]), (440, g2[1][1]), g2[1])
    svg.wire(pins[2]["=9"], (555, y), (555, g2[0][1]), g2[0])
    svg.wire(o2, (640, o2[1])); svg.text(640, o2[1] - 12, "tick", "end", "t sm a b")
    return svg.render("three cascaded decade counters; each stage is enabled when all lower stages are at 9")


def johnson():
    svg = Svg(470, 170)
    regs = [dff(svg, 60 + 95 * k, 60, f"q({k})", w=52, h=64) for k in range(4)]
    for a, b in zip(regs, regs[1:]):
        svg.wire(a["q"], b["d"])
    last, first = regs[-1]["q"], regs[0]["d"]
    xr, xl, yt = last[0] + 22, first[0] - 22, 24
    svg.wire(last, (xr, last[1]), (xr, yt), (270, yt))
    # a NOT gate pointing left
    svg.poly([(270, yt - 12), (270, yt + 12), (246, yt)], closed=True)
    svg.circle(242, yt, 4)
    svg.wire((238, yt), (xl, yt), (xl, first[1]), first)
    svg.text(260, 50, "not q(3)", "middle", "t sm m")
    svg.text(235, 158, "q(0) gets not q(3); q(i) gets q(i-1)", "middle", "t sm m")
    return svg.render("4-bit Johnson counter: a shift register with an inverted feedback")


def onehot_ring():
    svg = Svg(560, 170)
    labels = ["q(0)", "q(1)", "q(2)", None, "q(7)"]
    regs = []
    for k, lab in enumerate(labels):
        x = 60 + 95 * k
        if lab is None:
            svg.text(x + 26, 87, "· · ·", "middle", "t b m")
            regs.append(None)
        else:
            regs.append(dff(svg, x, 60, lab, w=52, h=64))
    for a, b in zip(regs, regs[1:]):
        if a and b:
            svg.wire(a["q"], b["d"])
        elif a:
            svg.wire(a["q"], (a["q"][0] + 30, a["q"][1]), cls="s dash")
        else:
            svg.wire((b["d"][0] - 30, b["d"][1]), b["d"], cls="s dash")
    last, first = regs[-1]["q"], regs[0]["d"]
    xr, xl, yt = last[0] + 22, first[0] - 22, 24
    svg.wire(last, (xr, last[1]), (xr, yt), (xl, yt), (xl, first[1]), first)
    svg.text(280, 160, "rotate left when en = 1; reset loads 00000001", "middle", "t sm m")
    return svg.render("8-bit one-hot ring: q(7) wraps around to q(0)")


def pwm8():
    return counter_wave(10, [("reset", [0] * 10)], step=lambda c, i: (c + 1) % 256,
                        out=lambda c, i: {"counter": c, "duty": 3, "pwm": int(c < 3)}, state=252, slot=19,
                        outputs=("pwm",), title="pwm is high while the free-running counter is below duty",
                        note="duty = 3: pwm is high for 3 of every 256 cycles")


FIGURES = {
    "count16": count16(),
    "decade": decade(),
    "count_en_tc": count_en_tc(),
    "tick_gen": tick_gen(),
    "bcd_counter2": bcd_counter2(),
    "clock_hms": clock_hms(),
    "count_1_to_12": count_1_to_12(),
    "updown": updown(),
    "countdown_timer": countdown(),
    "decade_slowena": slowena(),
    "div1000_enables": div1000(),
    "johnson4": johnson(),
    "onehot_ring": onehot_ring(),
    "pwm8": pwm8(),
}
