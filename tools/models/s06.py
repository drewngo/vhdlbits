"""Python models for Section 6 (written from the spec, not from the VHDL)."""


def s8(v):
    return v - 256 if v & 0x80 else v


def sx(v, w):
    return v - (1 << w) if v >> (w - 1) & 1 else v


def shifter(i):
    d, n = i["din"], i["amt"]
    if i["dir"] == 0:
        r = d << n
    elif i["arith"]:
        r = sx(d, 32) >> n
    else:
        r = d >> n
    return {"dout": r & 0xFFFFFFFF}


def sat_add(i):
    t = s8(i["a"]) + s8(i["b"])
    return {"s": max(-128, min(127, t)) & 0xFF, "sat": int(t > 127 or t < -128)}


def bcd(i):
    v = i["bin"]
    return {"hundreds": v // 100, "tens": v // 10 % 10, "ones": v % 10}


def ovf(i):
    t = s8(i["a"]) + s8(i["b"])
    return {"s": t & 0xFF, "ovf": int(not -128 <= t <= 127)}


MODELS = {
    "unsigned_add": lambda i: {"sum": i["a"] + i["b"]},
    "signed_compare": lambda i: {"lt": int(s8(i["a"]) < s8(i["b"])), "eq": int(i["a"] == i["b"]),
                                 "gt": int(s8(i["a"]) > s8(i["b"])), "lt_u": int(i["a"] < i["b"]),
                                 "min_s": min(s8(i["a"]), s8(i["b"])) & 0xFF},
    "signed_overflow": ovf,
    "popcount": lambda i: {"count": bin(i["din"]).count("1")},
    "mux256": lambda i: {"y": (i["din"] >> i["sel"]) & 1},
    "mux256x4": lambda i: {"y": (i["din"] >> (4 * i["sel"])) & 15},
    "resize_signed": lambda i: {"ext_s": s8(i["din"]) & 0xFFFF, "ext_u": i["din"], "trunc": i["din"] & 15},
    "enum_decoder": lambda i: {"busy": int(i["sel"] in (1, 2)), "fin": int(i["sel"] == 3)},
    "integer_range": lambda i: {"s": min(99, i["a"] + i["b"])},
    "abs_value": lambda i: {"mag": abs(s8(i["a"])), "neg": int(s8(i["a"]) < 0)},
    "mult_u": lambda i: {"p": i["a"] * i["b"]},
    "mult_s": lambda i: {"p": (s8(i["a"]) * s8(i["b"])) & 0xFFFF},
    "barrel_shifter": shifter,
    "sat_add_s": sat_add,
    "divmod10": lambda i: {"q": i["din"] // 10, "r": i["din"] % 10},
    "bin_to_bcd": bcd,
    "std_ulogic_note": lambda i: {"y": i["a"] | i["b"]},
}
