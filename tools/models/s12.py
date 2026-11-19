"""Python models for Section 12 (written from the spec, not from the VHDL)."""


class RomSync:
    def __init__(self):
        self.data = None

    def out(self, i):
        return {"data": self.data}

    def clk(self, i):
        self.data = (i["addr"] ** 2) % 256


class RamSP:
    WRITE_FIRST = False
    SIZE = 32

    def __init__(self):
        self.mem = [0] * self.SIZE
        self.dout = None

    def out(self, i):
        return {"dout": self.dout}

    def clk(self, i):
        wa, ra = i.get("waddr", i.get("addr")), i.get("raddr", i.get("addr"))
        self.dout = i["din"] if (self.WRITE_FIRST and i["we"]) else self.mem[ra]
        if i["we"]:
            self.mem[wa] = i["din"]


class RamWF(RamSP):
    WRITE_FIRST = True


class RamDP(RamSP):
    SIZE = 64


class RegFile:
    BYPASS = False

    def __init__(self):
        self.r = None

    def read(self, a, i):
        if a == 0:
            return 0
        if self.BYPASS and i["we"] and i["wa"] == a:
            return i["wd"]
        return self.r[a]

    def out(self, i):
        if self.r is None:
            return {}
        return {"rd1": self.read(i["ra1"], i), "rd2": self.read(i["ra2"], i)}

    def clk(self, i):
        if i["reset"]:
            self.r = [0] * 32
        elif self.r is not None and i["we"] and i["wa"]:
            self.r[i["wa"]] = i["wd"]


class Bypass(RegFile):
    BYPASS = True


class Cam:
    def __init__(self):
        self.e = None

    def out(self, i):
        if self.e is None:
            return {}
        hits = [k for k in range(4) if self.e[k] == i["key"]]
        return {"hit": int(bool(hits)), "hit_idx": hits[0] if hits else 0}

    def clk(self, i):
        if i["reset"]:
            self.e = [None] * 4
        elif self.e is not None and i["we"]:
            self.e[i["widx"]] = i["din"]


MODELS = {
    "rom_const": lambda i: {"data": (i["addr"] ** 2) % 256},
    "rom_sync": RomSync, "ram_sp": RamSP, "ram_write_first": RamWF, "ram_dp": RamDP,
    "regfile_rv": RegFile, "regfile_bypass": Bypass, "cam4": Cam,
}
