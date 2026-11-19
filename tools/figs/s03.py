from diagrams import Svg, bitfield, gate, hv


def vec_split():
    svg = Svg(300, 140)
    svg.wire((50, 30), (230, 30), cls="s bus")
    svg.text(135, 18, "3", "middle", "t sm m")
    svg.line(130, 24, 140, 36)
    svg.pin(50, 30, "v")
    svg.pin(230, 30, "outv", "right", "t a b")
    svg.dot(90, 30)
    for i, (bit, y) in enumerate([(2, 65), (1, 90), (0, 115)]):
        svg.wire((90, 30), (90, y), (230, y))
        svg.text(110, y - 8, f"v({bit})", "start", "t sm m")
        svg.pin(230, y, f"o{bit}", "right", "t a b")
    return svg.render("v passes to outv and splits into o2, o1, o0")


def byte_split():
    rows = [("din", [("hi", 15, 8, "a"), ("lo", 7, 0)])]
    return bitfield(rows, bw=20, title="din(15 downto 8) is hi, din(7 downto 0) is lo")


def byte_swap():
    return bitfield([
        ("din", [("B3", 31, 24), ("B2", 23, 16), ("B1", 15, 8), ("B0", 7, 0)]),
        ("dout", [("B0", 31, 24, "a"), ("B1", 23, 16, "a"), ("B2", 15, 8, "a"), ("B3", 7, 0, "a")]),
    ], bw=9, links=[((0, 3), (1, 0)), ((0, 2), (1, 1)), ((0, 1), (1, 2)), ((0, 0), (1, 3))],
        title="byte swap: byte 0 moves to byte 3, byte 1 to byte 2, and so on")


def concat():
    return bitfield([
        ("", [('"01"', 31, 30, "x"), ("a", 29, 25), ("b", 24, 20), ("c", 19, 15), ("d", 14, 10),
              ("e", 9, 5), ("f", 4, 0)]),
        ("", [("w", 31, 24, "a"), ("x", 23, 16, "a"), ("y", 15, 8, "a"), ("z", 7, 0, "a")]),
    ], bw=16, gap=34, label_w=10,
        title='"01" & a & b & c & d & e & f, split into bytes w x y z')


def bit_reverse():
    top = [(f"{i}", i, i) for i in range(7, -1, -1)]
    bot = [(f"{7 - i}", i, i, "a") for i in range(7, -1, -1)]
    return bitfield([("din", top), ("dout", bot)], bw=34, gap=60, numbers=True,
                    links=[((0, k), (1, 7 - k)) for k in range(8)],
                    title="bit reverse: dout(i) = din(7 - i)")


def sign_extend():
    return bitfield([
        ("din", [("s", 7, 7), ("din(6:0)", 6, 0)]),
        ("dout", [("s s s s ... s s s s  (24 copies of din(7))", 31, 8, "a"), ("s", 7, 7), ("din(6:0)", 6, 0)]),
    ], bw=12, gap=44, links=[((0, 0), (1, 0)), ((0, 0), (1, 1)), ((0, 1), (1, 2))],
        title="sign extension: the top 24 bits are copies of din(7)")


def pattern_fill():
    return bitfield([
        ("pat", [("pat", 3, 0)]),
        ("dout", [("pat", 15, 12, "a"), ("pat", 11, 8, "a"), ("pat", 7, 4, "a"), ("pat", 3, 0, "a")]),
    ], bw=20, gap=44, links=[((0, 0), (1, k)) for k in range(4)],
        title="dout is pat repeated four times")


def nibble_swap():
    return bitfield([
        ("din", [("H", 7, 4), ("L", 3, 0)]),
        ("dout", [("L", 7, 4, "a"), ("H", 3, 0, "a")]),
    ], bw=26, gap=50, links=[((0, 0), (1, 1)), ((0, 1), (1, 0))],
        title="nibble swap: the two 4-bit halves trade places")


def neighbor_xor():
    bw, x0 = 28, 50
    svg = Svg(x0 + 16 * bw + 20, 200)

    def cx(i):
        return x0 + (15 - i) * bw + bw / 2
    for row, y, name in ((0, 20, "din"), (1, 120, "y")):
        svg.text(x0 - 10, y + 15, name, "end", "t b a" if row else "t")
        for i in range(16):
            svg.rect(cx(i) - bw / 2, y, bw, 30, "s af" if row and i in (1, 15) else "s bg")
            svg.text(cx(i), y + 15, str(i), "middle", "t sm")
    svg.arrow((cx(2), 50), (cx(1) - 3, 118), cls="s thin")
    svg.arrow((cx(1), 50), (cx(1) + 1, 118), cls="s thin")
    svg.arrow((cx(15), 50), (cx(15), 118), cls="s thin as", head="ak")
    svg.arrow((cx(0), 50), (cx(0), 85), (cx(15) + 6, 85), (cx(15) + 6, 118), cls="s thin as", head="ak")
    svg.text(cx(1) + 14, 170, "y(1) = din(1) xor din(2)", "end", "t sm")
    svg.text(cx(15) - 14, 170, "y(15) = din(15) xor din(0)", "start", "t sm a")
    return svg.render("y(i) = din(i) xor din((i+1) mod 16); bit 15 wraps around to bit 0")


def gray_encode():
    rows = [
        ("b", [(f"b{i}", i, i) for i in range(7, -1, -1)]),
        ("b >> 1", [("0", 7, 7, "x")] + [(f"b{i + 1}", i, i) for i in range(6, -1, -1)]),
        ("g", [(f"g{i}", i, i, "a") for i in range(7, -1, -1)]),
    ]
    return bitfield(rows, bw=36, gap=26, label_w=70, numbers=False,
                    note="g = b xor (b >> 1), bit by bit (column-wise)",
                    title="Gray encode: each bit of g is the XOR of the bits in its column")


def gray_decode():
    """A ripple chain: b(7) = g(7), then each b(i) = b(i+1) xor g(i)."""
    svg = Svg(560, 180)
    col = 64
    x0 = 70
    svg.text(20, 30, "g", "middle", "t b")
    svg.text(20, 150, "b", "middle", "t b a")
    prev_out = None
    for k, i in enumerate(range(7, -1, -1)):
        x = x0 + col * k
        svg.text(x, 18, str(i), "middle", "t sm m")
        if k == 0:
            svg.wire((x, 26), (x, 150))
            svg.text(x, 162, "b7", "middle", "t sm a b")
            prev_out = (x, 100)
            svg.dot(*prev_out)
            continue
        ins, out = gate(svg, "xor", x - 18, 90, 2, w=32)
        svg.wire((x - 30, 26), (x - 30, ins[0][1]), ins[0])
        svg.wire(prev_out, (prev_out[0] + 8, prev_out[1]), (prev_out[0] + 8, ins[1][1]), ins[1])
        ox, oy = out
        svg.wire(out, (ox + 6, oy), (ox + 6, 150))
        svg.text(ox + 6, 162, f"b{i}", "middle", "t sm a b")
        prev_out = (ox + 6, 120)
        svg.dot(ox + 6, 120)
    return svg.render("Gray decode: b7 = g7, then b(i) = b(i+1) xor g(i), rippling from MSB to LSB")


def rv_itype():
    return bitfield([
        ("instr", [("imm[11:0]", 31, 20), ("rs1", 19, 15), ("funct3", 14, 12), ("rd", 11, 7),
                   ("opcode", 6, 0)]),
    ], bw=17, title="RISC-V I-type instruction fields")


def rv_rtype():
    return bitfield([
        ("instr", [("funct7", 31, 25), ("rs2", 24, 20), ("rs1", 19, 15), ("funct3", 14, 12), ("rd", 11, 7),
                   ("opcode", 6, 0)]),
    ], bw=17, title="RISC-V R-type instruction fields")


FIGURES = {
    "vec_split": vec_split(),
    "byte_split": byte_split(),
    "byte_swap": byte_swap(),
    "concat": concat(),
    "bit_reverse": bit_reverse(),
    "sign_extend": sign_extend(),
    "pattern_fill": pattern_fill(),
    "nibble_swap": nibble_swap(),
    "neighbor_xor": neighbor_xor(),
    "gray_encode": gray_encode(),
    "gray_decode": gray_decode(),
    "rv_itype_fields": rv_itype(),
    "rv_rtype_pack": rv_rtype(),
}
