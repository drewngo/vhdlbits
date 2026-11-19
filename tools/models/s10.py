"""Python models for Section 10 (written from the spec, not from the VHDL)."""


class Reg:
    """q register; subclasses define nxt(q, i). Inputs named load/d take priority if LOAD."""
    W = 8
    LOAD = True
    RESET = None

    def __init__(self):
        self.q = None

    def out(self, i):
        return {"q": self.q}

    def clk(self, i):
        if self.RESET is not None and i.get("reset"):
            self.q = self.RESET
        elif self.LOAD and i.get("load"):
            self.q = i["d"]
        elif self.q is not None:
            self.q = self.nxt(self.q, i) & ((1 << self.W) - 1)


class Shift4(Reg):
    W = 4

    def out(self, i):
        return {"q": 0 if i["areset"] else self.q}

    def clk(self, i):
        if i["areset"]:
            self.q = 0
        else:
            super().clk(i)

    def nxt(self, q, i):
        return q >> 1 if i["en"] else q


class Rotate8(Reg):
    def nxt(self, q, i):
        if i["ena"] == 1:
            return (q >> 1) | ((q & 1) << 7)
        if i["ena"] == 2:
            return (q << 1) | (q >> 7)
        return q


def s16(v):
    return v - 65536 if v & 0x8000 else v


class ArithShift(Reg):
    W = 16

    def nxt(self, q, i):
        if not i["en"]:
            return q
        return [q << 1, q << 4, s16(q) >> 1, s16(q) >> 4][i["amt"]]


def galois(q, w, taps):
    """Right-shifting Galois LFSR; taps are 1-based positions (w = wrap-around)."""
    out = q & 1
    q >>= 1
    if out:
        for t in taps:
            q ^= 1 << (t - 1)
    return q


class Lfsr5(Reg):
    W = 5
    RESET = 1
    LOAD = False

    def nxt(self, q, i):
        return galois(q, 5, [5, 3])


class Lfsr32(Reg):
    W = 32
    RESET = 1
    LOAD = False

    def nxt(self, q, i):
        return galois(q, 32, [32, 22, 2, 1])


class Sipo:
    def __init__(self):
        self.bits = []
        self.dout = self.valid = None

    def out(self, i):
        return {"dout": self.dout, "valid": self.valid}

    def clk(self, i):
        if i["reset"]:
            self.bits, self.dout, self.valid = [], 0, 0
            return
        if self.valid is None:
            return
        self.valid = 0
        if i["en"]:
            self.bits.append(i["sin"])
            if len(self.bits) == 8:
                self.dout = sum(b << k for k, b in enumerate(self.bits))
                self.valid = 1
                self.bits = []


class Piso:
    def __init__(self):
        self.queue = None   # bits still to show after the current one
        self.sout = self.busy = None

    def out(self, i):
        return {"sout": self.sout, "busy": self.busy}

    def clk(self, i):
        if i["reset"]:
            self.queue, self.sout, self.busy = [], 0, 0
            return
        if self.busy is None:
            return
        if not self.busy:
            if i["load"]:
                bits = [(i["d"] >> k) & 1 for k in range(7, -1, -1)]
                self.sout, self.queue, self.busy = bits[0], bits[1:], 1
        elif self.queue:
            self.sout = self.queue.pop(0)
        else:
            self.sout, self.busy = 0, 0


class ShiftN:
    N = 12

    def __init__(self):
        self.bits = [None] * self.N   # bits[k] is q(k)

    def out(self, i):
        if any(b is None for b in self.bits):
            return {"sout": self.bits[-1]}
        return {"q": sum(b << k for k, b in enumerate(self.bits)), "sout": self.bits[-1]}

    def clk(self, i):
        if i["en"]:
            self.bits = [i["sin"]] + self.bits[:-1]


class TapLut(ShiftN):
    N = 8

    def out(self, i):
        return {"y": self.bits[i["addr"]]}


class Rule90(Reg):
    W = 64

    def nxt(self, q, i):
        return (q >> 1) ^ (q << 1)


class Rule30(Reg):
    W = 64

    def nxt(self, q, i):
        left, right = q >> 1, q << 1
        return left ^ (q | right)


class Life(Reg):
    W = 256

    def nxt(self, q, i):
        alive = lambda r, c: (q >> ((r % 16) * 16 + c % 16)) & 1
        new = 0
        for r in range(16):
            for c in range(16):
                n = sum(alive(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc)
                if n == 3 or (n == 2 and alive(r, c)):
                    new |= 1 << (r * 16 + c)
        return new


MODELS = {
    "shift4": Shift4, "rotate8": Rotate8, "arith_shift": ArithShift, "lfsr5": Lfsr5,
    "sipo8": Sipo, "piso8": Piso, "shift_n_generic": ShiftN, "lfsr32": Lfsr32,
    "tap_lut": TapLut, "rule90": Rule90, "rule30": Rule30, "life16": Life,
}
