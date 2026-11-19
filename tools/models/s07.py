"""Python models for Section 7 (written from the spec, not from the VHDL)."""

# Segments lit per hex digit (standard glyphs from the 7.5 spec).
LIT = ["abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg", "acdefg", "abc",
       "abcdefg", "abcdfg", "abcefg", "cdefg", "adef", "bcdeg", "adefg", "aefg"]


def seven_seg(i):
    active_high = sum(1 << "abcdefg".index(s) for s in LIT[i["hex"]])
    return {"seg": ~active_high & 0x7F}


def minterm(i, names="abcd"):
    return sum(i[n] << (len(names) - 1 - k) for k, n in enumerate(names))


def s4(v):
    return v - 16 if v & 8 else v


def alu4(i):
    a, b, op = i["a"], i["b"], i["op"]
    y = [a + b, a - b, a & b, a | b, a ^ b, int(s4(a) < s4(b)), int(a < b), b][op] & 15
    return {"y": y, "zero": int(y == 0)}


def bcd_digit(i):
    t = i["a"] + i["b"] + i["cin"]
    return {"s": t % 10, "cout": int(t >= 10)}


def onehot(i):
    v = i["oh"]
    ok = bin(v).count("1") == 1
    return {"idx": v.bit_length() - 1 if ok else 0, "valid": int(ok)}


def parity(v):
    return bin(v).count("1") & 1


TABLE3 = [1, 0, 1, 1, 0, 0, 1, 0]
VEC = [0x7, 0xC, 0x2, 0x9, 0xE, 0x0, 0x5, 0xB, 0x3, 0xF, 0x8, 0x1, 0xA, 0x6, 0xD, 0x4]
F13 = {0, 2, 6, 7, 8, 10, 14, 15}

MODELS = {
    "half_adder": lambda i: {"s": i["a"] ^ i["b"], "c": i["a"] & i["b"]},
    "full_adder": lambda i: {"s": (i["a"] + i["b"] + i["cin"]) & 1, "cout": (i["a"] + i["b"] + i["cin"]) >> 1},
    "adder4_loop": lambda i: (lambda t: {"sum": t & 15, "cout": t >> 4})(i["a"] + i["b"] + i["cin"]),
    "decoder3to8": lambda i: {"y": (1 << i["a"]) if i["en"] else 0},
    "seven_seg": seven_seg,
    "kmap4": lambda i: {"y": int(minterm(i) in {1, 3, 4, 5, 7, 9, 13, 15})},
    "magnitude_cmp": lambda i: {"gt": int(i["a"] > i["b"]), "eq": int(i["a"] == i["b"]), "lt": int(i["a"] < i["b"])},
    "bcd_add_digit": bcd_digit,
    "mux2_wide": lambda i: {"y": i["b"] if i["sel"] else i["a"]},
    "mux9_default": lambda i: {"y": i[f"d{i['sel']}"] if i["sel"] <= 8 else 0xFFFF},
    "adder100_numeric": lambda i: (lambda t: {"sum": t & ((1 << 100) - 1), "cout": t >> 100})(i["a"] + i["b"] + i["cin"]),
    "kmap_dontcare": lambda i: {"y": int(minterm(i) in {2, 3, 5, 7, 11, 13})},
    "sop_and_pos": lambda i: (lambda y: {"y_sop": y, "y_pos": y})(int(minterm(i) in F13)),
    "truth_table3": lambda i: {"y": TABLE3[minterm(i, "abc")]},
    "wave_puzzle_comb1": lambda i: {"q": int((i["a"] and not i["b"]) or (i["b"] and i["c"]))},
    "wave_puzzle_comb2": lambda i: {"q": i["a"] ^ (i["b"] & (i["c"] | i["d"]))},
    "wave_puzzle_vec": lambda i: {"q": VEC[i["x"]]},
    "odd_parity9": lambda i: {"pbit": 1 - parity(i["data"]), "err": int(parity(i["word"]) == 0)},
    "onehot_to_bin": onehot,
    "alu4": alu4,
    "thermometer": lambda i: {"t": (1 << i["n"]) - 1},
}
