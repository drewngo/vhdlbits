"""Python models for Section 5 (written from the spec, not from the VHDL)."""


class ClockedProcess:
    def __init__(self):
        self.ff = None

    def out(self, i):
        x = i["a"] ^ i["b"]
        return {"y_conc": x, "y_comb": x, "y_ff": self.ff}

    def clk(self, i):
        self.ff = i["a"] ^ i["b"]


class VarsVsSignals:
    def __init__(self):
        self.t = None
        self.y_var = self.y_sig = None

    def out(self, i):
        return {"y_var": self.y_var, "y_sig": self.y_sig}

    def clk(self, i):
        x = i["a"] ^ i["b"]
        self.y_var = x & i["c"]
        if self.t is None:
            self.y_sig = 0 if i["c"] == 0 else None   # 'U' and '0' = '0'
        else:
            self.y_sig = self.t & i["c"]
        self.t = x


def lowest_set(v):
    return (v & -v).bit_length() - 1 if v else 0


DECODE = {0b0001: ["alu_en"], 0b0010: ["alu_en", "wr_reg"], 0b0100: ["mem_rd", "wr_reg"],
          0b0101: ["mem_wr"], 0b1000: ["branch"], 0b1111: ["halt"]}


def ascii_class(c):
    ch = chr(c)
    if "0" <= ch <= "9":
        return 1
    if "A" <= ch <= "Z":
        return 2
    if "a" <= ch <= "z":
        return 3
    return 0


def parity(v):
    return bin(v).count("1") & 1


MODELS = {
    "comb_process": lambda i: {"y_conc": i["a"] & i["b"], "y_proc": i["a"] & i["b"]},
    "clocked_process": ClockedProcess,
    "if_mux": lambda i: (lambda y: {"y_when": y, "y_if": y})(i["b"] if i["sel1"] and i["sel2"] else i["a"]),
    "case_mux": lambda i: {"y": i[f"d{i['sel']}"] if i["sel"] <= 5 else 0},
    "priority_encoder": lambda i: {"pos": lowest_set(i["din"])},
    "no_latches": lambda i: {n: int(n in DECODE.get(i["op"], []))
                             for n in ("alu_en", "wr_reg", "mem_rd", "mem_wr", "branch", "halt")},
    "variables_vs_signals": VarsVsSignals,
    "with_select": lambda i: {"y": i[f"d{i['sel']}"]},
    "case_ranges": lambda i: {"cls": ascii_class(i["ch"])},
    "min4": lambda i: {"m": min(i["a"], i["b"], i["c"], i["d"])},
    "last_assignment_wins": lambda i: {"y": {(0, 0): 0, (1, 0): 1, (0, 1): 2, (1, 1): 3}[(i["a"], i["b"])]},
    "loop_exit": lambda i: {"idx": max(i["din"].bit_length() - 1, 0), "valid": int(i["din"] != 0)},
    "local_function": lambda i: {"pa": parity(i["a"]), "pb": parity(i["b"])},
    "procedure_swap": lambda i: dict(zip(("s0", "s1", "s2"), sorted((i["x"], i["y"], i["z"])))),
}
