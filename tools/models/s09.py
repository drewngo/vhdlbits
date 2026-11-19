"""Python models for Section 9 (written from the spec, not from the VHDL)."""


class Counter:
    """State is an int (or None before the first reset). Subclasses define step()/outs()."""
    RESET = 0

    def __init__(self):
        self.c = None

    def out(self, i):
        return {} if self.c is None else self.outs(self.c, i)

    def clk(self, i):
        if i["reset"]:
            self.c = self.RESET
        elif self.c is not None:
            self.c = self.step(self.c, i)

    def outs(self, c, i):
        return {"q": c}


class Count16(Counter):
    def step(self, c, i):
        return (c + 1) % 16


class Decade(Counter):
    def step(self, c, i):
        return (c + 1) % 10


class CountEnTc(Counter):
    def step(self, c, i):
        return (c + i["en"]) % 256

    def outs(self, c, i):
        return {"q": c, "tc": int(c == 255 and i["en"] == 1)}


class TickGen(Counter):
    def step(self, c, i):
        return (c + 1) % 5

    def outs(self, c, i):
        return {"tick": int(c == 4)}


class Bcd2(Counter):
    def step(self, c, i):
        return (c + i["en"]) % 100

    def outs(self, c, i):
        return {"ones": c % 10, "tens": c // 10}


def bcd(n):
    return (n // 10) << 4 | n % 10


class ClockHMS(Counter):
    def step(self, c, i):
        return (c + i["en"]) % 86400

    def outs(self, c, i):
        return {"hh": bcd(c // 3600), "mm": bcd(c // 60 % 60), "ss": bcd(c % 60)}


class OneTo12(Counter):
    RESET = 1

    def step(self, c, i):
        return c % 12 + 1


class UpDown(Counter):
    def step(self, c, i):
        if not i["en"]:
            return c
        return (c + (1 if i["up"] else -1)) % 256


class Countdown(Counter):
    def step(self, c, i):
        if i["load"]:
            return i["d"]
        return max(c - 1, 0)

    def outs(self, c, i):
        return {"q": c, "done": int(c == 0)}


class SlowDecade(Counter):
    def step(self, c, i):
        return (c + i["slowena"]) % 10


class Div1000(Counter):
    def step(self, c, i):
        return (c + 1) % 1000

    def outs(self, c, i):
        d0, d1, d2 = c % 10, c // 10 % 10, c // 100
        return {"enables": 1 | (d0 == 9) << 1 | (d0 == 9 and d1 == 9) << 2, "tick": int(c == 999)}


JOHNSON = [0b0000, 0b0001, 0b0011, 0b0111, 0b1111, 0b1110, 0b1100, 0b1000]


class Johnson(Counter):
    def step(self, c, i):
        return (c + 1) % 8

    def outs(self, c, i):
        return {"q": JOHNSON[c]}


class Ring(Counter):
    def step(self, c, i):
        return (c + i["en"]) % 8

    def outs(self, c, i):
        return {"q": 1 << c}


class Pwm(Counter):
    def step(self, c, i):
        return (c + 1) % 256

    def outs(self, c, i):
        return {"pwm": int(c < i["duty"])}


MODELS = {
    "count16": Count16, "decade": Decade, "count_en_tc": CountEnTc, "tick_gen": TickGen,
    "bcd_counter2": Bcd2, "clock_hms": ClockHMS, "count_1_to_12": OneTo12, "updown": UpDown,
    "countdown_timer": Countdown, "decade_slowena": SlowDecade, "div1000_enables": Div1000,
    "johnson4": Johnson, "onehot_ring": Ring, "pwm8": Pwm,
}
