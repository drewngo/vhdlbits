"""Python models for Section 16. Bug hunts that restate an earlier problem reuse its model."""
import importlib.util
from pathlib import Path


def _load(stem):
    spec = importlib.util.spec_from_file_location(stem, Path(__file__).with_name(f"{stem}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODELS


S1, S5, S8, S9, S11 = (_load(s) for s in ("s01", "s05", "s08", "s09", "s11"))


class Mux3:
    def step(self, i):
        return {"y": {0: i["a"], 1: i["b"]}.get(i["sel"], i["c"])}


class RunningTotal:
    def __init__(self):
        self.total = self.over = None

    def out(self, i):
        return {"total": self.total, "over": self.over}

    def clk(self, i):
        if i["reset"]:
            self.total, self.over = 0, 0
        elif self.total is not None:
            self.total = (self.total + i["x"]) % 4096
            self.over = int(self.total >= 2048)


class LoadClear:
    def __init__(self):
        self.q = None

    def out(self, i):
        return {"q": self.q}

    def clk(self, i):
        if i["clear"]:
            self.q = 0
        elif i["load"]:
            self.q = i["d"]


def s8(v):
    return v - 256 if v & 0x80 else v


MODELS = {
    "bug_sensitivity": Mux3,
    "bug_latch": S5["no_latches"],
    "bug_signal_vs_var": RunningTotal,
    "bug_numeric": lambda i: {"m": i["a"] if s8(i["a"]) < s8(i["b"]) else i["b"]},
    "bug_resize": lambda i: {"sum": i["a"] + i["b"]},
    "bug_off_by_one": S9["decade"],
    "bug_async_reset": S8["dff8_async_reset"],
    "bug_fsm_default": S11["seq_1011"],
    "bug_multiple_drivers": LoadClear,
    "bug_integer_overflow": lambda i: {"count": bin(i["din"]).count("1")},
    "bug_shift": lambda i: {"y": (s8(i["x"]) >> 2) & 0xFF},
    "bug_handshake": S11["handshake_fifo1"],
    "bug_gray_loop": S1["gray_decode"],
    "bug_case_others": S5["case_mux"],
}
