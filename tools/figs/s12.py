from diagrams import Svg, bitfield, box, clocked, gate, hv, mux, wave


def rom_sync():
    addrs = [3, 7, 7, 10, 2, 15, 0]
    rom = lambda a: f"{a * a % 256:02X}"
    rows = clocked(len(addrs), [("addr", addrs)], step=lambda d, i: rom(i["addr"]),
                   out=lambda d, i: {"12.1 data": rom(i["addr"]), "data": d}, state=None)
    return wave(rows, slot=22, outputs=("data",), note="12.1 reads combinationally; here data lags addr by a clock",
                title="a registered ROM read: data is the word at the addr sampled at the last edge")


def ram_wave(write_first):
    we = [0, 1, 0, 1, 0, 0]
    addr = [5, 5, 5, 9, 9, 5]
    din = [None, "AA", None, "BB", None, None]

    def step(st, i):
        mem, dout = st
        old = mem.get(i["addr"], "00")
        if i["we"]:
            mem = {**mem, i["addr"]: i["din"]}
        return (mem, i["din"] if (i["we"] and write_first) else old)
    rows = clocked(6, [("we", we), ("addr", addr), ("din", din)], step=step,
                   out=lambda st, i: {"dout": st[1]}, state=({5: "11", 9: "22"}, None))
    kind = "write-first: during a write, dout shows the new data" if write_first else \
        "read-first: during a write, dout shows the old contents"
    return wave(rows, slot=26, outputs=("dout",), note="ram(5) starts as 11 and ram(9) as 22",
                title=kind)


def ram_dp():
    svg = Svg(460, 170)
    p = box(svg, 150, 20, 190, 130, "ram\n64 × 16", left=[("we", .2), ("waddr", .4), ("din", .6), (">", .85)],
            right=[("dout", .5)], bottom=[], title_y=60)
    svg.text(140, 12, "write port", "end", "t sm m")
    for nm, cls in (("we", "s"), ("waddr", "s bus"), ("din", "s bus")):
        svg.wire((70, p[nm][1]), p[nm], cls=cls); svg.pin(70, p[nm][1], nm)
    svg.wire((70, p[">"][1]), p[">"]); svg.pin(70, p[">"][1], "clk")
    svg.wire((245, 170), (245, 150), cls="s bus"); svg.text(253, 162, "raddr", "start", "t sm")
    svg.wire(p["dout"], (400, p["dout"][1]), cls="s bus"); svg.pin(400, p["dout"][1], "dout", "right", "t a b")
    svg.text(350, 112, "read port", "start", "t sm m")
    return svg.render("simple dual-port RAM: one write port and one read port, both clocked")


def regfile(bypass):
    h = 200 if bypass else 160
    svg = Svg(580 if bypass else 460, h + 50)
    p = box(svg, 140, 30, 160, h, "registers\nx0 .. x31", left=[("we", .15), ("wa", .3), ("wd", .45),
                                                              ("ra1", .65), ("ra2", .8), (">", .93)],
            right=[("rd1", .3), ("rd2", .75)], title_y=30 + h * .3 - 8)
    for nm in ("we", "wa", "wd", "ra1", "ra2"):
        svg.wire((70, p[nm][1]), p[nm], cls="s" if nm == "we" else "s bus"); svg.pin(70, p[nm][1], nm)
    svg.wire((70, p[">"][1]), p[">"]); svg.pin(70, p[">"][1], "clk")
    svg.text(220, 30 + h * .55, "x0 reads 0", "middle", "t sm m")
    if not bypass:
        for nm in ("rd1", "rd2"):
            svg.wire(p[nm], (390, p[nm][1]), cls="s bus"); svg.pin(390, p[nm][1], nm, "right", "t a b")
        return svg.render("register file: two combinational read ports and one clocked write port")
    svg.wire((110, p["wd"][1]), (110, 14), (350, 14), cls="s bus"); svg.dot(110, p["wd"][1])
    for k, nm in enumerate(("rd1", "rd2")):
        ins, sel, out = mux(svg, 390, p[nm][1] + 10, 2)
        svg.wire(p[nm], ins[0], cls="s bus")
        svg.wire((350, 14), (350, ins[1][1]), ins[1], cls="s bus")
        svg.wire(out, (480, out[1]), cls="s bus"); svg.pin(480, out[1], nm, "right", "t a b")
        svg.wire(sel, (sel[0], sel[1] + 14)); svg.text(sel[0] + 6, sel[1] + 16, f"hit{k + 1}", "start", "t sm m")
    svg.dot(350, p["rd1"][1] + 20)
    svg.text(300, h + 70, "hitN = we and wa /= 0 and raN = wa", "middle", "t sm m")
    return svg.render("write-through bypass: a read of the register being written returns wd")


def cam4():
    svg = Svg(560, 252)
    ys = [30, 75, 120, 165]
    for k, y in enumerate(ys):
        box(svg, 120, y - 18, 90, 36, "")
        svg.text(165, y, f"entry {k}", "middle", "t sm")
        svg.rect(212, y - 18, 22, 36, "s xf")
        svg.text(223, y, "v", "middle", "t sm m")
        svg.circle(290, y, 16); svg.text(290, y, "=", "middle", "t b")
        svg.wire((234, y), (274, y), cls="s bus")
        svg.wire((306, y), (380, y))
        svg.text(340, y - 9, f"m{k}", "middle", "t sm m")
    svg.wire((256, 222), (256, ys[0] + 26))
    for y in ys:
        svg.wire((256, y + 26), (290, y + 26), (290, y + 16))
        if y != ys[0]:
            svg.dot(256, y + 26)
    svg.text(262, 222, "key", "start", "t sm")
    p = box(svg, 380, 30, 100, 160, "lowest\nmatch", right=[("hit", .35), ("hit_idx", .65)])
    for nm in ("hit", "hit_idx"):
        svg.wire(p[nm], (540, p[nm][1]), cls="s bus" if nm == "hit_idx" else "s")
        svg.text(536, p[nm][1] - 10, nm, "end", "t sm a b")
    svg.text(20, 40, "we, widx,", "start", "t sm m")
    svg.text(20, 54, "din write", "start", "t sm m")
    svg.text(20, 68, "one entry", "start", "t sm m")
    svg.text(20, 240, "m(k): entry k is valid and equals key", "start", "t sm m")
    return svg.render("a 4-entry CAM: every valid entry is compared with key at once")


FIGURES = {
    "rom_sync": rom_sync(),
    "ram_sp": ram_wave(False),
    "ram_write_first": ram_wave(True),
    "ram_dp": ram_dp(),
    "regfile_rv": regfile(False),
    "regfile_bypass": regfile(True),
    "cam4": cam4(),
}
