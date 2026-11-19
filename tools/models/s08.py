"""Python models for Section 8 (written from the spec, not from the VHDL)."""


class Reg:
    """Generic register model: subclasses define nxt(state, i) and optionally RESET."""
    RESET = None
    RESET_PORT = "reset"
    ACTIVE = 1
    ASYNC = False

    def __init__(self):
        self.q = None

    def in_reset(self, i):
        return self.RESET is not None and i.get(self.RESET_PORT) == self.ACTIVE

    def out(self, i):
        if self.ASYNC and self.in_reset(i):
            return {"q": self.RESET}
        return {"q": self.q}

    def clk(self, i):
        self.q = self.RESET if self.in_reset(i) else self.nxt(self.q, i)


class Dff(Reg):
    def nxt(self, q, i):
        return i["d"]


class Dff8Sync(Dff):
    RESET = 0


class Dff8Async(Dff):
    RESET = 0
    RESET_PORT = "areset"
    ASYNC = True


class DffEnable(Reg):
    RESET = 0

    def nxt(self, q, i):
        return i["d"] if i["en"] else q


class EdgeDetect:
    BOTH = False

    def __init__(self):
        self.prev = None
        self.pulse = None

    def out(self, i):
        return {"pulse": self.pulse}

    def clk(self, i):
        d = i["din"]
        if self.prev is None:
            # din and not U: only bits where din = 0 are known (0).
            self.pulse = None if (self.BOTH or d) else 0
        else:
            self.pulse = d ^ self.prev if self.BOTH else d & ~self.prev & 0xFF
        self.prev = d


class AnyEdge(EdgeDetect):
    BOTH = True


class Sticky:
    def __init__(self):
        self.prev = None
        self.cap = None

    def out(self, i):
        return {"cap": self.cap}

    def clk(self, i):
        if i["reset"]:
            self.cap = 0
        elif self.cap is not None and self.prev is not None:
            self.cap |= self.prev & ~i["din"] & 0xFFFFFFFF
        else:
            self.cap = None
        self.prev = i["din"]


class Negedge(Reg):
    RESET = 0x5A

    def clk(self, i):
        pass

    def fall(self, i):
        self.q = 0x5A if i["reset"] else i["d"]


class ByteEnable(Reg):
    RESET = 0
    RESET_PORT = "resetn"
    ACTIVE = 0

    def nxt(self, q, i):
        if q is None:
            return None if i["be"] != 3 else i["d"]
        if i["be"] & 2:
            q = (q & 0x00FF) | (i["d"] & 0xFF00)
        if i["be"] & 1:
            q = (q & 0xFF00) | (i["d"] & 0x00FF)
        return q


class Latch:
    def __init__(self):
        self.q = None

    def step(self, i):
        if i["en"]:
            self.q = i["d"]
        return {"q": self.q}


class JK(Reg):
    def __init__(self):
        self.q = 0

    def nxt(self, q, i):
        return {(0, 0): q, (0, 1): 0, (1, 0): 1, (1, 1): 1 - q}[(i["j"], i["k"])]


class TFF(Reg):
    RESET = 0

    def nxt(self, q, i):
        return None if q is None else q ^ i["t"]


class Sync2:
    def __init__(self):
        self.s = [None, None]

    def out(self, i):
        return {"sync_out": self.s[1]}

    def clk(self, i):
        self.s = [i["async_in"], self.s[0]]


class DualEdge:
    def __init__(self):
        self.q = None

    def out(self, i):
        return {"q": self.q}

    def clk(self, i):
        self.q = i["d"]

    def fall(self, i):
        self.q = i["d"]


class Pipeline:
    def __init__(self):
        self.s1 = None
        self.y = None

    def out(self, i):
        return {"y": self.y}

    def clk(self, i):
        if i["reset"]:
            self.s1, self.y = (0, 0), 0
            return
        self.y = None if self.s1 is None else self.s1[0] * self.s1[1]
        self.s1 = (i["a"] + i["b"], i["c"])


MODELS = {
    "dff": Dff,
    "dff8_sync_reset": Dff8Sync,
    "dff8_async_reset": Dff8Async,
    "dff_enable": DffEnable,
    "rise_detect": EdgeDetect,
    "any_edge": AnyEdge,
    "sticky_capture": Sticky,
    "dff_negedge": Negedge,
    "byte_enable_reg": ByteEnable,
    "d_latch": Latch,
    "jk_ff": JK,
    "t_ff": TFF,
    "sync2": Sync2,
    "dual_edge": DualEdge,
    "pipeline3": Pipeline,
}
