"""Python models for Section 13 (written from the spec, not from the VHDL)."""


def sx(v, w):
    return v - (1 << w) if v >> (w - 1) & 1 else v


def sat(a, b, w):
    t = sx(a, w) + sx(b, w)
    lo, hi = -(1 << (w - 1)), (1 << (w - 1)) - 1
    return max(lo, min(hi, t)) & ((1 << w) - 1)


def array_max(i):
    bs = [(i["din"] >> (8 * k)) & 0xFF for k in range(8)]
    m = max(bs)
    return {"maxv": m, "maxi": bs.index(m)}


def rev(v, w):
    return int(format(v, f"0{w}b")[::-1], 2)


class Records:
    def __init__(self):
        self.s1 = self.s2 = None

    def out(self, i):
        return {} if self.s2 is None else dict(zip(("v_out", "a_out", "d_out"), self.s2))

    def clk(self, i):
        if i["reset"]:
            self.s1 = self.s2 = (0, 0, 0)
        elif self.s1 is not None:
            self.s1, self.s2 = (i["v_in"], i["a_in"], i["d_in"]), self.s1


MODELS = {
    "package_constants": lambda i: {"dout": i["din"] ^ 0x5A3},
    "package_function": lambda i: {"ca": bin(i["a"]).count("1"), "cb": bin(i["b"]).count("1")},
    "record_signal": Records,
    "array_of_vectors": array_max,
    "enum_attributes": lambda i: {"nxt": (i["idx"] + 1) % 6 if i["idx"] <= 5 else 0},
    "unconstrained_ports": lambda i: {"ra": rev(i["a"], 5), "rb": rev(i["b"], 13)},
    "generic_package": lambda i: {"s8": sat(i["a8"], i["b8"], 8), "s12": sat(i["a12"], i["b12"], 12)},
}
