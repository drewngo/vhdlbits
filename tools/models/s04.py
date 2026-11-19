"""Python models for Section 4 (written from the spec, not from the VHDL)."""
M32 = (1 << 32) - 1


class ThreeDffs:
    def __init__(self):
        self.stages = [None, None, None]

    def out(self, i):
        return {"q": self.stages[2]}

    def clk(self, i):
        self.stages = [i["d"]] + self.stages[:2]


class TapSelect:
    def __init__(self):
        self.stages = [None, None, None]

    def out(self, i):
        return {"q": i["d"] if i["sel"] == 0 else self.stages[i["sel"] - 1]}

    def clk(self, i):
        self.stages = [i["d"]] + self.stages[:2]


class GenericMap:
    def __init__(self):
        self.q4 = self.q12 = None

    def out(self, i):
        return {"q4": self.q4, "q12": self.q12}

    def clk(self, i):
        self.q4, self.q12 = i["d4"], i["d12"]


class IfGenerate:
    def __init__(self):
        self.y = None

    def out(self, i):
        return {"y": self.y}

    def clk(self, i):
        self.y = i["a"] & i["b"]


def ripple(a, b, cin, n):
    """Sum and the vector of every stage's carry-out for an n-bit ripple adder."""
    couts, c, s = 0, cin, 0
    for k in range(n):
        x, y = (a >> k) & 1, (b >> k) & 1
        s |= (x ^ y ^ c) << k
        c = (x & y) | (x & c) | (y & c)
        couts |= c << k
    return s, couts


def bcd_add(i):
    digits = lambda v: [(v >> (4 * k)) & 15 for k in range(4)]
    total = int("".join(map(str, digits(i["a"])[::-1]))) + int("".join(map(str, digits(i["b"])[::-1]))) + i["cin"]
    return {"sum": int(str(total % 10000).zfill(4), 16), "cout": int(total >= 10000)}


def rotl(v, w):
    return ((v << 1) | (v >> (w - 1))) & ((1 << w) - 1)


MODELS = {
    "instantiate": lambda i: {"y": int(i["a"] == 1 and i["b"] == 0)},
    "positional_map": lambda i: {"out1": i["a"] ^ i["b"], "out2": i["c"] & i["d"]},
    "three_dffs": ThreeDffs,
    "tap_select": TapSelect,
    "adder32": lambda i: {"sum": (i["a"] + i["b"]) & M32},
    "carry_select": lambda i: {"sum": (i["a"] + i["b"]) & M32},
    "generic_map": GenericMap,
    "generate_adder": lambda i: dict(zip(("sum", "couts"), ripple(i["a"], i["b"], i["cin"], 8))),
    "add_sub": lambda i: {"result": (i["a"] - i["b"] if i["sub"] else i["a"] + i["b"]) & M32},
    "component_decl": lambda i: {"y": int(i["a"] == 1 and i["b"] == 0)},
    "adder100_generate": lambda i: dict(zip(("sum", "couts"), ripple(i["a"], i["b"], i["cin"], 100))),
    "bcd_ripple4": bcd_add,
    "own_generic": lambda i: {"dout": rotl(i["din"], 6)},
    "if_generate": IfGenerate,
    "two_level_hier": lambda i: (lambda y1: {"y1": y1, "y2": y1 ^ i["d"] ^ i["e"]})(i["a"] ^ i["b"] ^ i["c"]),
}
