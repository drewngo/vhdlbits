"""Python models for Section 15, written from the README text before the VHDL."""
from math import isqrt

M32 = 0xFFFFFFFF


class Machine:
    def __init__(self):
        self.live = False

    def out(self, i):
        return self.outs(i) if self.live else {}

    def clk(self, i):
        if i["reset"]:
            self.reset_state()
            self.live = True
        elif self.live:
            self.step(i)


class Fifo(Machine):
    def reset_state(self):
        self.q = []

    def step(self, i):
        do_pop = i["pop"] and len(self.q) > 0
        do_push = i["push"] and len(self.q) < 8
        if do_pop:
            self.q.pop(0)
        if do_push:
            self.q.append(i["din"])

    def outs(self, i):
        n = len(self.q)
        return {"dout": self.q[0] if n else 0, "full": int(n == 8), "empty": int(n == 0), "count": n}


class UartTx(Machine):
    CPB = 1

    def reset_state(self):
        self.bits = []          # remaining (bit) per clock cycle, current one first

    def step(self, i):
        if self.bits:
            self.bits.pop(0)
        elif i["start"]:
            frame = [0] + [(i["data"] >> k) & 1 for k in range(8)] + [1]
            self.bits = [b for b in frame for _ in range(self.CPB)]

    def outs(self, i):
        return {"txd": self.bits[0] if self.bits else 1, "busy": int(bool(self.bits))}


class UartTxBaud(UartTx):
    CPB = 4


class Spi(Machine):
    def reset_state(self):
        self.c = None         # cycle number within a transfer, None when idle
        self.done, self.rx = 0, 0

    def step(self, i):
        self.done = 0
        if self.c is None:
            if i["start"]:
                self.c, self.tx, self.acc = 0, i["tx"], 0
            return
        if self.c % 4 == 1:
            self.acc = (self.acc << 1) | i["miso"]
        if self.c == 31:
            self.c, self.done, self.rx = None, 1, self.acc
        else:
            self.c += 1

    def outs(self, i):
        if self.c is None:
            return {"sclk": 0, "mosi": 0, "cs_n": 1, "done": self.done, "rx": self.rx}
        bit = 7 - self.c // 4
        return {"sclk": int(self.c % 4 >= 2), "mosi": (self.tx >> bit) & 1, "cs_n": 0,
                "done": 0, "rx": self.rx}


class DebounceEdge(Machine):
    def reset_state(self):
        self.clean, self.n, self.press = 0, 0, 0

    def step(self, i):
        self.press = 0
        if i["btn"] == self.clean:
            self.n = 0
        else:
            self.n += 1
            if self.n == 8:
                self.clean, self.n = i["btn"], 0
                self.press = self.clean

    def outs(self, i):
        return {"press": self.press}


LIT = ["abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg", "acdefg", "abc",
       "abcdefg", "abcdfg", "abcefg", "cdefg", "adef", "bcdeg", "adefg", "aefg"]


def glyph(h):
    return ~sum(1 << "abcdefg".index(s) for s in LIT[h]) & 0x7F


class SegMux(Machine):
    def reset_state(self):
        self.t = 0

    def step(self, i):
        self.t = (self.t + 1) % 16

    def outs(self, i):
        k = self.t // 4
        return {"an": ~(1 << k) & 0xF, "seg": glyph((i["value"] >> (4 * k)) & 15)}


class MovingAvg(Machine):
    def reset_state(self):
        self.h = [0, 0, 0, 0]

    def step(self, i):
        if i["valid"]:
            self.h = [i["x"]] + self.h[:3]

    def outs(self, i):
        return {"y": sum(self.h) // 4}


def s8(v):
    return v - 256 if v & 0x80 else v


class Fir(Machine):
    def reset_state(self):
        self.d, self.y = [0, 0, 0], 0

    def step(self, i):
        if i["valid"]:
            x = s8(i["x"])
            self.y = x + 3 * self.d[0] + 3 * self.d[1] + self.d[2]
            self.d = [x] + self.d[:2]

    def outs(self, i):
        return {"y": self.y & 0x7FF}


class Iterative(Machine):
    N = 8
    RESULTS = ()

    def reset_state(self):
        self.left, self.done = 0, 0
        self.res = {k: 0 for k in self.RESULTS}

    def step(self, i):
        self.done = 0
        if self.left:
            self.left -= 1
            if self.left == 0:
                self.res, self.done = self.pending, 1
        elif i["start"]:
            self.left, self.pending = self.N, self.compute(i)

    def outs(self, i):
        return {**self.res, "busy": int(self.left > 0), "done": self.done}


class Isqrt(Iterative):
    RESULTS = ("root",)

    def compute(self, i):
        return {"root": isqrt(i["x"])}


class MultSeq(Iterative):
    RESULTS = ("p",)

    def compute(self, i):
        return {"p": i["a"] * i["b"]}


class DivSeq(Iterative):
    N = 16
    RESULTS = ("q", "r", "dz")

    def compute(self, i):
        if i["d"] == 0:
            return {"q": 0xFFFF, "r": i["n"] & 0xFF, "dz": 1}
        return {"q": i["n"] // i["d"], "r": i["n"] % i["d"], "dz": 0}


def s32(v):
    return v - (1 << 32) if v >> 31 else v


def alu(i):
    a, b, f3, f7 = i["a"], i["b"], i["funct3"], i["funct7_5"]
    sh = b & 31
    y = {0: (a - b) if f7 else (a + b), 1: a << sh, 2: int(s32(a) < s32(b)), 3: int(a < b),
         4: a ^ b, 5: (s32(a) >> sh) if f7 else (a >> sh), 6: a | b, 7: a & b}[f3]
    return {"y": y & M32}


def field(v, hi, lo):
    return (v >> lo) & ((1 << (hi - lo + 1)) - 1)


def sext(v, w):
    return (v - (1 << w) if v >> (w - 1) & 1 else v) & M32


def imm_gen(i):
    x = i["instr"]
    op = x & 0x7F
    if op in (0x03, 0x13, 0x67):
        return {"imm": sext(field(x, 31, 20), 12)}
    if op == 0x23:
        return {"imm": sext(field(x, 31, 25) << 5 | field(x, 11, 7), 12)}
    if op == 0x63:
        v = field(x, 31, 31) << 12 | field(x, 7, 7) << 11 | field(x, 30, 25) << 5 | field(x, 11, 8) << 1
        return {"imm": sext(v, 13)}
    if op in (0x37, 0x17):
        return {"imm": x & 0xFFFFF000}
    if op == 0x6F:
        v = field(x, 31, 31) << 20 | field(x, 19, 12) << 12 | field(x, 20, 20) << 11 | field(x, 30, 21) << 1
        return {"imm": sext(v, 21)}
    return {"imm": 0}


SIGNALS = ("reg_write", "alu_src", "mem_read", "mem_write", "mem_to_reg", "branch", "jump")
DECODE = {
    0x33: "1000000", 0x13: "1100000", 0x03: "1110100", 0x23: "0101000",
    0x63: "0000010", 0x6F: "1000001", 0x67: "1100001", 0x37: "1100000", 0x17: "1100000",
}


def decoder(i):
    x = i["instr"]
    op, f3, f7 = x & 0x7F, field(x, 14, 12), field(x, 30, 30)
    bits = DECODE.get(op, "0000000")
    out = {n: int(b) for n, b in zip(SIGNALS, bits)}
    if op == 0x33:
        ctrl = f7 << 3 | f3
    elif op == 0x13:
        ctrl = (f7 << 3 | f3) if f3 == 5 else f3
    elif op == 0x63:
        ctrl = 8
    else:
        ctrl = 0
    out["alu_ctrl"] = ctrl
    return out


MODELS = {
    "fifo_sync": Fifo, "uart_tx": UartTx, "uart_tx_baud": UartTxBaud, "spi_master": Spi,
    "debounce_edge": DebounceEdge, "seven_seg_mux": SegMux, "moving_avg4": MovingAvg,
    "fir4": Fir, "isqrt_seq": Isqrt, "mult_seq": MultSeq, "div_seq": DivSeq,
    "rv32i_alu": alu, "rv32i_imm_gen": imm_gen, "rv32i_decoder": decoder,
}
