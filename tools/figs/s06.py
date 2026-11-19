from diagrams import bitfield


def mux256x4():
    return bitfield([
        ("din", [("value 255", 1023, 1020, "a"), ("value 254", 1019, 1016), ("· · ·", None, 7),
                 ("value 1", 7, 4), ("value 0", 3, 0, "a")]),
    ], bw=19, title="din holds 256 four-bit values; value i is din(4*i+3 downto 4*i)")


def resize_signed():
    return bitfield([
        ("din", [("s", 7, 7), ("din(6:0)", 6, 0)]),
        ("ext_s", [("s s s s s s s s", 15, 8, "a"), ("s", 7, 7), ("din(6:0)", 6, 0)]),
        ("ext_u", [("0 0 0 0 0 0 0 0", 15, 8, "x"), ("s", 7, 7), ("din(6:0)", 6, 0)]),
        ("trunc", [("din(3:0)", 3, 0)]),
    ], bw=18, gap=22, note="s = din(7). resize copies it on signed, fills with 0 on unsigned",
        title="sign extension, zero extension and truncation of an 8-bit value")


def barrel_shifter():
    letters = "abcdefgh"

    def row(cells):
        return [(c, None, 1, "x" if c == "0" else "") for c in cells]
    rows = [
        ("din", row(letters)),
        ("left 3", row("defgh000")),
        ("right 3, logical", row("000abcde")),
        ("right 3, arithmetic", [(c, None, 1, "a" if k < 3 else "") for k, c in enumerate("aaaabcde")]),
    ]
    return bitfield(rows, bw=30, gap=12, numbers=False,
                    note="shown 8 bits wide; a is the sign bit. Grey: zeros shifted in. Blue: sign copies.",
                    title="logical left, logical right and arithmetic right shifts by 3")


FIGURES = {
    "mux256x4": mux256x4(),
    "resize_signed": resize_signed(),
    "barrel_shifter": barrel_shifter(),
}
