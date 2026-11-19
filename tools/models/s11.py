"""Python models for Section 11, written from the README text before the VHDL."""


class Machine:
    """Synchronous-reset machine. Subclasses define reset_state(), step(i) and outs(i)."""
    RESET_PORT = "reset"
    ASYNC = False

    def __init__(self):
        self.live = False

    def out(self, i):
        if self.ASYNC and i[self.RESET_PORT]:
            self.reset_state()
            self.live = True
        return self.outs(i) if self.live else {}

    def clk(self, i):
        if i[self.RESET_PORT]:
            self.reset_state()
            self.live = True
        elif self.live:
            self.step(i)


class Toggle(Machine):
    def reset_state(self):
        self.on = 0

    def step(self, i):
        self.on ^= i["t"]

    def outs(self, i):
        return {"y": self.on}


class Mealy(Toggle):
    def outs(self, i):
        return {"y": int(self.on and not i["t"])}


class Seq1011(Machine):
    def reset_state(self):
        self.hist = ""

    def step(self, i):
        self.hist = (self.hist + str(i["din"]))[-4:]

    def outs(self, i):
        return {"found": int(self.hist == "1011")}


class Walker(Machine):
    RESET_PORT = "areset"
    ASYNC = True

    def reset_state(self):
        self.dir = "L"

    def walk(self, i):
        if i["bump_l"] and i["bump_r"]:
            self.dir = "R" if self.dir == "L" else "L"
        elif i["bump_l"]:
            self.dir = "R"
        elif i["bump_r"]:
            self.dir = "L"

    def step(self, i):
        self.walk(i)

    def outs(self, i):
        return {"go_l": int(self.dir == "L"), "go_r": int(self.dir == "R")}


class WalkerFall(Walker):
    def reset_state(self):
        self.dir = "L"
        self.falling = False

    def step(self, i):
        if self.falling:
            self.falling = not i["ground"]
        elif not i["ground"]:
            self.falling = True
        else:
            self.walk(i)

    def outs(self, i):
        if self.falling:
            return {"go_l": 0, "go_r": 0, "falling": 1}
        return {**super().outs(i), "falling": 0}


class Debounce(Machine):
    def reset_state(self):
        self.clean, self.n = 0, 0

    def step(self, i):
        if i["noisy"] == self.clean:
            self.n = 0
        else:
            self.n += 1
            if self.n == 4:
                self.clean, self.n = i["noisy"], 0

    def outs(self, i):
        return {"clean": self.clean}


class UartRx(Machine):
    PARITY = False

    def reset_state(self):
        self.phase, self.bits = "idle", []
        self.data, self.done = 0, 0

    def step(self, i):
        b = i["rxd"]
        self.done = 0
        if self.phase == "idle":
            if b == 0:
                self.phase, self.bits = "data", []
        elif self.phase == "data":
            self.bits.append(b)
            if len(self.bits) == (9 if self.PARITY else 8):
                self.phase = "stop"
        elif self.phase == "stop":
            if b == 0:
                self.phase = "wait"
            else:
                self.phase = "idle"
                if not self.PARITY or sum(self.bits) % 2 == 1:
                    self.data = sum(v << k for k, v in enumerate(self.bits[:8]))
                    self.done = 1
        elif self.phase == "wait":
            if b == 1:
                self.phase = "idle"

    def outs(self, i):
        return {"data": self.data, "done": self.done}


class UartRxParity(UartRx):
    PARITY = True


class Skid(Machine):
    def reset_state(self):
        self.full, self.data = False, 0

    def ready(self, i):
        return int(not self.full or i["out_ready"] == 1)

    def step(self, i):
        take_in = i["in_valid"] and self.ready(i)
        if self.full and i["out_ready"]:
            self.full = False
        if take_in:
            self.full, self.data = True, i["in_data"]

    def outs(self, i):
        return {"in_ready": self.ready(i), "out_valid": int(self.full), "out_data": self.data}


TABLE = {"A": ("A", "B"), "B": ("C", "B"), "C": ("A", "D"), "D": ("C", "B")}
ORDER = "ABCD"


def onehot_next(i):
    s = ORDER[i["state"].bit_length() - 1]
    n = TABLE[s][i["x"]]
    return {"nxt": 1 << ORDER.index(n), "y": int(s == "D")}


def binary_next(i):
    s = ORDER[i["state"]]
    return {"nxt": ORDER.index(TABLE[s][i["x"]]), "y": int(s == "D")}


class FromTable(Machine):
    def reset_state(self):
        self.s = "A"

    def step(self, i):
        self.s = TABLE[self.s][i["x"]]

    def outs(self, i):
        return {"y": int(self.s == "D")}


class HeaderPacket(Machine):
    def reset_state(self):
        self.phase, self.first = "hunt", None
        self.payload, self.done = 0, 0

    def step(self, i):
        d = i["din"]
        self.done = 0
        if self.phase == "hunt":
            if d == 0xA5:
                self.phase = "b1"
        elif self.phase == "b1":
            self.first, self.phase = d, "b2"
        else:
            self.payload, self.done, self.phase = (self.first << 8) | d, 1, "hunt"

    def outs(self, i):
        return {"payload": self.payload, "done": self.done}


class Unstuff(Machine):
    def reset_state(self):
        self.ones, self.waiting = 0, False
        self.pulse = None

    def step(self, i):
        self.pulse = None
        if self.waiting:
            if i["din"] == 0:
                self.waiting, self.ones = False, 0
            return
        if i["din"] == 1:
            self.ones += 1
            if self.ones == 7:
                self.pulse, self.waiting = "err", True
        else:
            if self.ones == 5:
                self.pulse = "discard"
            elif self.ones == 6:
                self.pulse = "flag"
            self.ones = 0

    def outs(self, i):
        return {k: int(self.pulse == k) for k in ("discard", "flag", "err")}


class Vending(Machine):
    def reset_state(self):
        self.total, self.vend, self.change = 0, 0, 0

    def step(self, i):
        self.vend = self.change = 0
        self.total += 5 * i["nickel"] + 10 * i["dime"]
        if self.total >= 15:
            self.vend, self.change = 1, int(self.total == 20)
            self.total = 0

    def outs(self, i):
        return {"vend": self.vend, "change": self.change}


class Traffic(Machine):
    PHASES = ["MAIN_G", "MAIN_Y", "SIDE_G", "SIDE_Y"]
    LIGHTS = {"MAIN_G": ("main_g", "side_r"), "MAIN_Y": ("main_y", "side_r"),
              "SIDE_G": ("main_r", "side_g"), "SIDE_Y": ("main_r", "side_y")}

    def reset_state(self):
        self.ph, self.t = "MAIN_G", 0

    def step(self, i):
        leave = {"MAIN_G": i["car_side"] == 1 and self.t >= 4, "MAIN_Y": self.t == 1,
                 "SIDE_G": self.t == 3, "SIDE_Y": self.t == 1}[self.ph]
        if leave:
            self.ph = self.PHASES[(self.PHASES.index(self.ph) + 1) % 4]
            self.t = 0
        else:
            self.t += 1

    def outs(self, i):
        on = self.LIGHTS[self.ph]
        return {n: int(n in on) for n in ("main_g", "main_y", "main_r", "side_g", "side_y", "side_r")}


class Fixed3(Machine):
    def reset_state(self):
        self.g = None

    def step(self, i):
        r = i["req"]
        if self.g is not None and (r >> self.g) & 1:
            return
        self.g = next((k for k in range(3) if (r >> k) & 1), None)

    def outs(self, i):
        return {"gnt": 0 if self.g is None else 1 << self.g}


class RR2(Machine):
    def reset_state(self):
        self.last, self.gnt = 1, 0

    def step(self, i):
        r = i["req"]
        if r == 0:
            self.gnt = 0
            return
        winner = {1: 0, 2: 1, 3: 1 - self.last}[r]
        self.gnt, self.last = 1 << winner, winner

    def outs(self, i):
        return {"gnt": self.gnt}


class DetectEnable(Machine):
    def reset_state(self):
        self.hist, self.go_left = "", 0

    def step(self, i):
        if self.go_left:
            self.go_left -= 1
            return
        self.hist = (self.hist + str(i["din"]))[-3:]
        if self.hist == "110":
            self.go_left, self.hist = 3, ""

    def outs(self, i):
        return {"go": int(self.go_left > 0)}


class TimerUnit(Machine):
    def reset_state(self):
        self.phase, self.hist = "search", ""

    def step(self, i):
        if self.phase == "search":
            self.hist = (self.hist + str(i["din"]))[-4:]
            if self.hist == "1101":
                self.phase, self.delay, self.nbits = "shift", 0, 0
        elif self.phase == "shift":
            self.delay = (self.delay << 1) | i["din"]
            self.nbits += 1
            if self.nbits == 4:
                self.phase, self.left = "count", (self.delay + 1) * 10
        elif self.phase == "count":
            self.left -= 1
            if self.left == 0:
                self.phase = "done"
        elif self.phase == "done":
            if i["ack"]:
                self.phase, self.hist = "search", ""

    def outs(self, i):
        counting = self.phase == "count"
        return {"counting": int(counting), "done": int(self.phase == "done"),
                "remaining": (self.left - 1) // 10 if counting else 0}


class Elevator(Machine):
    def reset_state(self):
        self.floor, self.p, self.up, self.phase = 0, 0, True, "IDLE"

    def decide(self, P):
        f = self.floor
        above = P & ~((1 << (f + 1)) - 1) & 7
        below = P & ((1 << f) - 1)
        if (P >> f) & 1:
            self.phase, self.p = "DOOR", P & ~(1 << f)
        elif (above if self.up else below):
            self.phase, self.p = "MOVE1", P
        elif (below if self.up else above):
            self.up = not self.up
            self.phase, self.p = "MOVE1", P
        else:
            self.phase, self.p = "IDLE", P

    def step(self, i):
        P = self.p | i["call"]
        if self.phase == "IDLE":
            self.decide(P)
        elif self.phase == "DOOR":
            self.phase, self.p = "IDLE", P & ~(1 << self.floor)
        elif self.phase == "MOVE1":
            self.phase, self.p = "MOVE2", P
        else:
            self.floor += 1 if self.up else -1
            self.decide(P)

    def outs(self, i):
        return {"floor": self.floor, "door": int(self.phase == "DOOR")}


class PuzzleSeq1(Machine):
    def reset_state(self):
        self.a_d, self.q = 0, 0

    def step(self, i):
        self.a_d, self.q = i["a"], i["a"] & self.a_d

    def outs(self, i):
        return {"q": self.q}


class PuzzleSeq2(Machine):
    def reset_state(self):
        self.s = 0

    def step(self, i):
        self.s ^= i["a"] & i["b"]

    def outs(self, i):
        return {"p": self.s ^ i["b"], "q": self.s}


class PuzzleSeq3(Machine):
    def reset_state(self):
        self.q = 0

    def step(self, i):
        self.q = min(self.q + 1, 6) if i["x"] else max(self.q - 1, 0)

    def outs(self, i):
        return {"q": self.q}


class PuzzleSeq4(Machine):
    def reset_state(self):
        self.run, self.z = 0, 0

    def step(self, i):
        if i["x"]:
            self.run, self.z = min(self.run + 1, 3), 0
        else:
            self.run, self.z = 0, int(self.run == 3)

    def outs(self, i):
        return {"z": self.z}


MODELS = {
    "fsm_toggle": Toggle, "fsm_mealy": Mealy, "seq_1011": Seq1011, "walker": Walker,
    "walker_fall": WalkerFall, "debounce": Debounce, "uart_rx_byte": UartRx,
    "handshake_fifo1": Skid, "onehot_next_state": onehot_next, "binary_next_state": binary_next,
    "fsm_from_table": FromTable, "header_packet": HeaderPacket, "uart_rx_parity": UartRxParity,
    "bit_unstuff": Unstuff, "vending": Vending, "traffic_light": Traffic,
    "arbiter_fixed3": Fixed3, "arbiter_rr2": RR2, "detect_then_enable": DetectEnable,
    "timer_unit": TimerUnit, "elevator3": Elevator,
    "wave_puzzle_seq1": PuzzleSeq1, "wave_puzzle_seq2": PuzzleSeq2, "wave_puzzle_seq3": PuzzleSeq3,
    "wave_puzzle_seq4": PuzzleSeq4,
}
