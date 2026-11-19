"""Python models for Sections 1-3 (written from the spec, not from the VHDL)."""


def bit(v, i):
    return (v >> i) & 1


def popcount(v):
    return bin(v).count("1")


def sext(v, w, to):
    if v >> (w - 1) & 1:
        v -= 1 << w
    return v & ((1 << to) - 1)


def gray_decode(g):
    b = 0
    for i in range(7, -1, -1):
        b |= (bit(g, i) ^ (bit(b, i + 1) if i < 7 else 0)) << i
    return b


def concat_bytes(i):
    v = 0b01
    for n in "abcdef":
        v = (v << 5) | i[n]
    return {"w": v >> 24, "x": v >> 16, "y": v >> 8, "z": v}


MODELS = {
    # Section 1
    "one": lambda i: {"o": 1},
    "zero": lambda i: {"o": 0},
    "case_and_comments": lambda i: {"y": 1 - i["a"]},
    # Section 2
    "wire": lambda i: {"y": i["a"]},
    "fanout": lambda i: {"p": i["c"], "q": i["a"], "r": i["a"], "s": i["b"]},
    "notgate": lambda i: {"y": 1 - i["a"]},
    "andgate": lambda i: {"y": i["a"] & i["b"]},
    "norgate": lambda i: {"y": int(not (i["a"] or i["b"]))},
    "xnorgate": lambda i: {"y": int(i["a"] == i["b"])},
    "internal_signals": lambda i: (lambda y: {"y": y, "y_n": 1 - y})(
        int((i["a"] and i["b"]) or (i["c"] and i["d"]))),
    "two_gate_chip": lambda i: {
        "p1y": int(all(i[f"p1{c}"] for c in "abc") or all(i[f"p1{c}"] for c in "def")),
        "p2y": int((i["p2a"] and i["p2b"]) or (i["p2c"] and i["p2d"]))},
    "all_gates": lambda i: {
        "o_and": i["a"] & i["b"], "o_or": i["a"] | i["b"], "o_xor": i["a"] ^ i["b"],
        "o_nand": 1 - (i["a"] & i["b"]), "o_nor": 1 - (i["a"] | i["b"]),
        "o_xnor": 1 - (i["a"] ^ i["b"]), "o_andnot": int(i["a"] == 1 and i["b"] == 0)},
    "xor3": lambda i: {"y": (i["a"] + i["b"] + i["c"]) % 2},
    "mux2_gates": lambda i: {"y": i["b"] if i["s"] else i["a"]},
    "majority3": lambda i: {"y": int(i["a"] + i["b"] + i["c"] >= 2)},
    "doorbell": lambda i: {"chime": int(i["press"] and not i["mute"]),
                           "light": int(i["press"] and i["mute"])},
    "garage_light": lambda i: {"light": int(not i["force_off"] and
                                            (i["door_open"] or (i["motion"] and i["dark"])))},
    "tristate": lambda i: {"y": str(i["a"]) if i["en"] else "Z"},
    # Section 3
    "vec_split": lambda i: {"outv": i["v"], "o2": bit(i["v"], 2), "o1": bit(i["v"], 1), "o0": bit(i["v"], 0)},
    "byte_split": lambda i: {"hi": i["din"] >> 8, "lo": i["din"] & 0xFF},
    "byte_swap": lambda i: {"dout": int.from_bytes(i["din"].to_bytes(4, "big"), "little")},
    "bitwise_vs_logical": lambda i: {
        "or_bitwise": i["a"] | i["b"], "or_logical": int(i["a"] != 0 or i["b"] != 0),
        "not_both": ((~i["b"] & 7) << 3) | (~i["a"] & 7)},
    "reduction": lambda i: {"all_ones": int(i["v"] == 0xFF), "any_one": int(i["v"] != 0),
                            "parity": popcount(i["v"]) % 2},
    "concat": concat_bytes,
    "bit_reverse": lambda i: {"dout": int(format(i["din"], "08b")[::-1], 2)},
    "sign_extend": lambda i: {"dout": sext(i["din"], 8, 32)},
    "pattern_fill": lambda i: {"dout": i["pat"] * 0x1111},
    "nibble_swap": lambda i: {"dout": ((i["din"] & 0xF) << 4) | (i["din"] >> 4)},
    "wide_reduce": lambda i: {"r_and": int(i["din"] == (1 << 100) - 1), "r_or": int(i["din"] != 0),
                              "r_xor": popcount(i["din"]) % 2},
    "neighbor_xor": lambda i: {"y": sum((bit(i["din"], k) ^ bit(i["din"], (k + 1) % 16)) << k for k in range(16))},
    "wide_bitwise": lambda i: {"all_and": i["a"] & i["b"] & i["c"] & i["d"],
                               "any_or": i["a"] | i["b"] | i["c"] | i["d"],
                               "odd": i["a"] ^ i["b"] ^ i["c"] ^ i["d"]},
    "gray_encode": lambda i: {"g": i["b"] ^ (i["b"] >> 1)},
    "gray_decode": lambda i: {"b": gray_decode(i["g"])},
    "rv_itype_fields": lambda i: {"opcode": i["instr"] & 0x7F, "rd": (i["instr"] >> 7) & 31,
                                  "funct3": (i["instr"] >> 12) & 7, "rs1": (i["instr"] >> 15) & 31,
                                  "imm": sext(i["instr"] >> 20, 12, 32)},
    "rv_rtype_pack": lambda i: {"instr": (i["funct7"] << 25) | (i["rs2"] << 20) | (i["rs1"] << 15) |
                                         (i["funct3"] << 12) | (i["rd"] << 7) | i["opcode"]},
    "literals": lambda i: {"is_zero": int(i["din"] == 0), "is_a5": int(i["din"] == 0xA5),
                           "is_max": int(i["din"] == 0xFF), "masked": i["din"] & 0x0F},
}
