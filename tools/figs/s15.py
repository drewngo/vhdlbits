from diagrams import Svg, bitfield, box, clocked, dff, wave


def fifo():
    svg = Svg(520, 170)
    cw, x0 = 50, 50
    entries = {2: "A", 3: "B", 4: "C"}
    for k in range(8):
        x = x0 + k * cw
        svg.rect(x, 60, cw, 40, "s af" if k in entries else "s bg")
        svg.text(x + cw / 2, 80, entries.get(k, ""), "middle", "t b")
        svg.text(x + cw / 2, 112, str(k), "middle", "t sm m")
    hx, tx = x0 + 2.5 * cw, x0 + 5.5 * cw
    svg.arrow((hx, 24), (hx, 58), cls="s as", head="ak")
    svg.text(hx, 16, "head: dout = A", "middle", "t sm a")
    svg.arrow((tx, 24), (tx, 58))
    svg.text(tx, 16, "tail: the next push", "middle", "t sm")
    svg.arrow((x0 + 8 * cw, 92), (x0 + 8 * cw + 16, 92), (x0 + 8 * cw + 16, 140), (x0 - 16, 140),
              (x0 - 16, 92), (x0, 92), cls="s thin dash")
    svg.text(x0 + 4 * cw, 152, "pointers wrap from 7 to 0; count = 3", "middle", "t sm m")
    return svg.render("an 8-entry FIFO as a circular buffer with head and tail pointers")


def uart_tx(cpb):
    data = 0x4B
    frame_bits = [0] + [(data >> k) & 1 for k in range(8)] + [1]

    def step(st, i):
        busy, n = st
        if busy:
            return (0, 0) if n == 10 * cpb else (1, n + 1)
        return (1, 1) if i["start"] else (0, 0)
    ncyc = 10 * cpb + 4
    start = [0, 1] + [0] * (ncyc - 2)
    start[4 * cpb] = 1                      # ignored while busy
    rows = clocked(ncyc, [("start", start), ("data", [None, "4B"] + [None] * (ncyc - 2))], step=step,
                   out=lambda st, i: {"txd": frame_bits[(st[1] - 1) // cpb] if st[0] else 1, "busy": st[0]},
                   state=(0, 0))
    names = ["start"] + [f"d{k}" for k in range(8)] + ["stop"]
    ticks = {2 * (2 + cpb * k) + cpb - 1: nm for k, nm in enumerate(names)} if cpb > 1 else \
        {2 * (2 + k) + 1: nm for k, nm in enumerate(names)}
    return wave(rows, slot=16 if cpb == 1 else 6, outputs=("txd", "busy"), ticks=ticks,
                grid=cpb == 1, note=f"x\"4B\" sent LSB first{'' if cpb == 1 else f'; each bit lasts {cpb} clocks'};"
                                    " the second start is ignored",
                title=f"UART transmit, {cpb} clock{'s' if cpb > 1 else ''} per bit")


def spi():
    tx, slave = 0xA5, 0x3C

    def step(st, i):
        c, sr, rx, done = st
        if c is None:
            return (0, 0, rx, 0) if i["start"] else (None, 0, rx, 0)
        if c % 4 == 1:
            sr = (sr << 1) | i["miso"]
        if c == 31:
            return (None, 0, f"{sr:02X}", 1)
        return (c + 1, sr, rx, 0)

    def miso(k):                                 # the slave puts bit 7-j out for transfer bit j
        return (slave >> (7 - k // 4)) & 1 if 0 <= k < 32 else 0
    n = 36
    rows = clocked(n, [("start", [0, 1] + [0] * (n - 2)), ("miso", [miso(k - 2) for k in range(n)])], step=step,
                   out=lambda st, i: {"cs_n": int(st[0] is None), "sclk": int(st[0] is not None and st[0] % 4 >= 2),
                                      "mosi": (tx >> (7 - st[0] // 4)) & 1 if st[0] is not None else 0,
                                      "done": st[3], "rx": st[2]},
                   state=(None, 0, "00", 0))
    return wave(rows, slot=7, outputs=("cs_n", "sclk", "mosi", "done", "rx"), grid=False,
                note="tx = A5 goes out on mosi; the slave answers 3C on miso; one sclk period = 4 clocks",
                title="an 8-bit SPI transfer: sclk is clk / 4, data changes while sclk is low")


def debounce_edge():
    btn = [0, 1, 0, 1, 1, 0, 1] + [1] * 10 + [0, 1, 1]

    def step(st, i):
        clean, cnt, press = st
        if i["btn"] == clean:
            return (clean, 0, 0)
        if cnt + 1 == 8:
            return (i["btn"], 0, int(i["btn"] == 1))
        return (clean, cnt + 1, 0)
    rows = clocked(len(btn), [("btn", btn)], step=step,
                   out=lambda st, i: {"clean": st[0], "press": st[2]}, state=(0, 0, 0))
    return wave(rows, slot=11, outputs=("press",), note="clean is internal: it changes after 8 edges in a row that disagree",
                title="a debounced button and a one-cycle press pulse")


def seven_seg_mux():
    rows = clocked(17, [("reset", [1] + [0] * 16)],
                   step=lambda st, i: 0 if i["reset"] else (st + 1) % 16,
                   out=lambda st, i: {"k": st // 4 if st is not None else None,
                                      "an": ["1110", "1101", "1011", "0111"][st // 4] if st is not None else None,
                                      "seg": f"digit {st // 4}" if st is not None else None},
                   state=None)
    return wave(rows, slot=12, outputs=("an", "seg"),
                note="k is internal; seg shows the 7.5 pattern of value(4k+3 downto 4k)",
                title="the four digits take turns, four clocks each")


def chain_sum(title, labels, coeffs=None, reg_out=False, note=""):
    """A delay line of registers whose taps (scaled by coeffs, if any) feed one adder."""
    svg = Svg(680, 250)
    svg.text(40, 60, "x", "end", "t")
    prev, taps, x = (44, 60), [(70, 60)], 110
    for lab in labels:
        r = dff(svg, x, 60 - 64 * .45, lab, w=56, h=64, extra_left=[("en", .65)])
        svg.wire(prev, r["d"], cls="s bus")
        prev = r["q"]
        taps.append((r["q"][0] + 18, r["q"][1]))
        x += 110
    svg.wire(prev, taps[-1], cls="s bus")
    taps = taps if coeffs else taps[1:]
    ay = 168
    ax0, ax1 = taps[0][0] - 24, taps[-1][0] + 24
    svg.rect(ax0, ay, ax1 - ax0, 30, "s bg", rx=3)
    svg.text((ax0 + ax1) / 2, ay + 15, "+", "middle", "t b")
    for k, (tx, ty) in enumerate(taps):
        if tx != taps[-1][0] or coeffs is None or k < len(taps) - 1:
            svg.dot(tx, ty)
        if coeffs:
            svg.wire((tx, ty), (tx, 116), cls="s bus")
            svg.circle(tx, 130, 14)
            svg.text(tx, 130, f"×{coeffs[k]}", "middle", "t sm")
            svg.arrow((tx, 144), (tx, ay), cls="s bus")
        else:
            svg.arrow((tx, ty), (tx, ay), cls="s bus")
    oy = ay + 15
    if reg_out:
        r = dff(svg, ax1 + 30, oy - 64 * .45, "", w=50, h=64)
        svg.wire((ax1, oy), r["d"], cls="s bus")
        svg.wire(r["q"], (r["q"][0] + 30, oy), cls="s bus"); svg.pin(r["q"][0] + 30, oy, "y", "right", "t a b")
    else:
        svg.wire((ax1, oy), (ax1 + 24, oy), cls="s bus")
        svg.text(ax1 + 42, oy, "/ 4", "middle", "t b")
        svg.wire((ax1 + 60, oy), (ax1 + 90, oy), cls="s bus"); svg.pin(ax1 + 90, oy, "y", "right", "t a b")
    svg.text(320, 238, note, "middle", "t sm m")
    return svg.render(title)


def iterative(n, a, result, title):
    def step(st, i):
        busy, cnt, done, res = st
        if busy:
            if cnt == n:
                return (0, 0, 1, result)
            return (1, cnt + 1, 0, res)
        if i["start"]:
            return (1, 1, 0, res)
        return (0, 0, 0, res)
    ncyc = n + 5
    start = [0, 1, 0, 0, 1] + [0] * (ncyc - 5)
    ops = [None, a] + [None] * (ncyc - 2)
    rows = clocked(ncyc, [("start", start), ("operands", ops)], step=step,
                   out=lambda st, i: {"busy": st[0], "done": st[2], "result": st[3]}, state=(0, 0, 0, "0"))
    return wave(rows, slot=9 if n > 8 else 12, outputs=("busy", "done", "result"),
                note=f"busy for exactly {n} cycles; a start while busy is ignored", title=title)


def imm_gen():
    def f(name, hi, lo, imm=False):
        return (name, hi, lo, "a" if imm else "")
    rows = [
        ("I", [f("imm[11:0]", 31, 20, 1), f("rs1", 19, 15), f("f3", 14, 12), f("rd", 11, 7), f("opcode", 6, 0)]),
        ("S", [f("imm[11:5]", 31, 25, 1), f("rs2", 24, 20), f("rs1", 19, 15), f("f3", 14, 12),
               f("imm[4:0]", 11, 7, 1), f("opcode", 6, 0)]),
        ("B", [f("12", 31, 31, 1), f("imm[10:5]", 30, 25, 1), f("rs2", 24, 20), f("rs1", 19, 15),
               f("f3", 14, 12), f("imm[4:1]", 11, 8, 1), f("11", 7, 7, 1), f("opcode", 6, 0)]),
        ("U", [f("imm[31:12]", 31, 12, 1), f("rd", 11, 7), f("opcode", 6, 0)]),
        ("J", [f("20", 31, 31, 1), f("imm[10:1]", 30, 21, 1), f("11", 20, 20, 1), f("imm[19:12]", 19, 12, 1),
               f("rd", 11, 7), f("opcode", 6, 0)]),
    ]
    return bitfield(rows, bw=18, gap=22, note="blue fields are immediate bits; f3 = funct3",
                    title="where the immediate bits sit in each RISC-V instruction format")


FIGURES = {
    "fifo_sync": fifo(),
    "uart_tx": uart_tx(1),
    "uart_tx_baud": uart_tx(4),
    "spi_master": spi(),
    "debounce_edge": debounce_edge(),
    "seven_seg_mux": seven_seg_mux(),
    "moving_avg4": chain_sum("a 4-sample moving average: the last four accepted samples, summed, divided by 4",
                             ["h0", "h1", "h2", "h3"], note="en = valid; every register shifts together"),
    "fir4": chain_sum("a 4-tap FIR filter with coefficients 1, 3, 3, 1",
                      ["d0", "d1", "d2"], coeffs=[1, 3, 3, 1], reg_out=True,
                      note="en = valid on every register; y is registered"),
    "isqrt_seq": iterative(8, "x", "root", "start / busy / done timing for the 8-cycle square root"),
    "mult_seq": iterative(8, "a, b", "p", "start / busy / done timing for the 8-cycle multiplier"),
    "div_seq": iterative(16, "n, d", "q, r", "start / busy / done timing for the 16-cycle divider"),
    "rv32i_imm_gen": imm_gen(),
}
