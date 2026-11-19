from diagrams import Svg, box, clocked, fsm, wave


def toggle():
    return fsm(420, 170, {"S_OFF": (110, 95, "y=0"), "S_ON": (310, 95, "y=1")},
               [("S_OFF", "S_ON", "t=1", .25), ("S_ON", "S_OFF", "t=1", .25),
                ("S_OFF", "S_OFF", "t=0", 180), ("S_ON", "S_ON", "t=0", 0)],
               reset=("S_OFF", -90), title="two-state toggle machine (Moore)")


def mealy():
    return fsm(520, 170, {"S_OFF": (160, 95), "S_ON": (360, 95)},
               [("S_OFF", "S_ON", "t=1 / y=0", .25), ("S_ON", "S_OFF", "t=1 / y=0", .25),
                ("S_OFF", "S_OFF", "t=0 / y=0", 180), ("S_ON", "S_ON", "t=0 / y=1", 0)],
               reset=("S_OFF", -90), title="the same machine with a Mealy output (labels are input / output)")


def seq_1011():
    din = [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1]

    def step(h, i):
        return [] if i["reset"] else (h + [i["din"]])[-4:]
    rows = clocked(len(din), [("reset", [1] + [0] * (len(din) - 1)), ("din", din)], step=step,
                   out=lambda h, i: {"found": int(h == [1, 0, 1, 1])}, state=[])
    return wave(rows, slot=15, outputs=("found",), note="1011011 contains two overlapping matches",
                title="found is high for the cycle after the edge that completes 1, 0, 1, 1")


def walker():
    return fsm(520, 170, {"LEFT": (160, 95, "go_l"), "RIGHT": (360, 95, "go_r")},
               [("LEFT", "RIGHT", "bump_l", .25), ("RIGHT", "LEFT", "bump_r", .25),
                ("LEFT", "LEFT", "not bump_l", 180), ("RIGHT", "RIGHT", "not bump_r", 0)],
               reset=("LEFT", -90), title="the walker: a bump on one side turns it around")


def walker_fall():
    return fsm(560, 340, {"LEFT": (170, 100, "go_l"), "RIGHT": (390, 100, "go_r"),
                          "FALL_L": (170, 270, "falling"), "FALL_R": (390, 270, "falling")},
               [("LEFT", "RIGHT", "ground, bump_l", .2), ("RIGHT", "LEFT", "ground, bump_r", .2),
                ("LEFT", "FALL_L", "not ground", .2), ("FALL_L", "LEFT", "ground", .2),
                ("RIGHT", "FALL_R", "not ground", -.2), ("FALL_R", "RIGHT", "ground", -.2),
                ("FALL_L", "FALL_L", "not ground", 180), ("FALL_R", "FALL_R", "not ground", 0),
                ("LEFT", "LEFT", "ground,\nno bump_l", 180), ("RIGHT", "RIGHT", "ground,\nno bump_r", 0)],
               r=34, reset=("LEFT", -90), title="walking and falling; a fall remembers the direction")


def debounce():
    noisy = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0]

    def step(st, i):
        clean, cnt = st
        if i["noisy"] == clean:
            return (clean, 0)
        if cnt + 1 == 4:
            return (i["noisy"], 0)
        return (clean, cnt + 1)
    rows = clocked(len(noisy), [("noisy", noisy)], step=step,
                   out=lambda st, i: {"count": st[1], "clean": st[0]}, state=(0, 0))
    return wave(rows, slot=15, outputs=("clean",), note="count is internal: consecutive edges where noisy differs",
                title="clean follows noisy only after 4 consecutive edges that disagree")


def uart_frame(byte, parity=False, title=""):
    bits = [(byte >> k) & 1 for k in range(8)]
    frame = [0] + bits + ([1 - sum(bits) % 2] if parity else []) + [1]
    rxd = [1, 1] + frame + [1, 1]
    names = ["start"] + [f"d{k}" for k in range(8)] + (["p"] if parity else []) + ["stop"]

    def step(st, i):
        phase, k, sr, data, done = st
        b = i["rxd"]
        if phase == "idle":
            return ("data", 0, 0, data, 0) if b == 0 else ("idle", 0, 0, data, 0)
        if phase == "data":
            sr |= b << k
            if k == 7:
                return ("par" if parity else "stop", 0, sr, data, 0)
            return ("data", k + 1, sr, data, 0)
        if phase == "par":
            return ("stop", b, sr, data, 0)            # k holds the parity bit
        if phase == "wait":
            return ("idle" if b else "wait", 0, 0, data, 0)
        if b == 0:
            return ("wait", 0, 0, data, 0)             # framing error
        if parity and (bin(sr).count("1") + k) % 2 == 0:
            return ("idle", 0, 0, data, 0)             # parity error
        return ("idle", 0, 0, f"{sr:02X}", 1)
    rows = clocked(len(rxd), [("rxd", rxd)], step=step,
                   out=lambda st, i: {"done": st[4], "data": st[3]}, state=("idle", 0, 0, "00", 0))
    ticks = {2 * (2 + k) + 1: nm for k, nm in enumerate(names)}
    return wave(rows, slot=16, outputs=("done", "data"), ticks=ticks, title=title,
                note=f"x\"{byte:02X}\" sent LSB first; labels mark the edge that samples each bit")


def handshake():
    in_valid = [0, 1, 1, 1, 0, 1, 1, 0, 0]
    in_data = [None, "11", "22", "33", None, "44", "55", None, None]
    out_ready = [1, 1, 0, 0, 1, 1, 1, 1, 1]

    def step(st, i):
        full, data = st
        leave = full and i["out_ready"]
        ready = (not full) or i["out_ready"]
        if i["in_valid"] and ready:
            return (1, i["in_data"])
        return (0 if leave else full, data)
    rows = clocked(9, [("in_valid", in_valid), ("in_data", in_data), ("out_ready", out_ready)], step=step,
                   out=lambda st, i: {"in_ready": int((not st[0]) or i["out_ready"]), "out_valid": st[0],
                                      "out_data": st[1]}, state=(0, "00"))
    return wave(rows, slot=20, outputs=("in_ready", "out_valid", "out_data"),
                title="a one-entry buffer: data moves on each edge where valid and ready are both 1")


def abcd(reset):
    return fsm(460, 330, {"A": (90, 90), "B": (330, 90), "C": (90, 250), "D": (330, 250, "y=1")},
               [("A", "B", "x=1", .12), ("A", "A", "x=0", 180), ("B", "B", "x=1", 0),
                ("B", "C", "x=0", .12), ("C", "A", "x=0", .25), ("C", "D", "x=1", .12),
                ("D", "C", "x=0", .12), ("D", "B", "x=1", .25)],
               reset=("A", -90) if reset else None, title="the four-state machine from the table")


def header_packet():
    din = ["00", "A5", "12", "34", "7F", "A5", "A5", "01", "33", "A5", "C0"]

    def step(st, i):
        ph, first, payload, done = st
        b = i["din"]
        if ph == "hunt":
            return ("p1", None, payload, 0) if b == "A5" else ("hunt", None, payload, 0)
        if ph == "p1":
            return ("p2", b, payload, 0)
        return ("hunt", None, first + b, 1)
    rows = clocked(len(din), [("din", din)], step=step,
                   out=lambda st, i: {"done": st[3], "payload": st[2]}, state=("hunt", None, "0000", 0))
    return wave(rows, slot=24, outputs=("done", "payload"),
                note="A5 starts a packet; an A5 inside the payload is just data",
                title="hunting for x\"A5\", then capturing two payload bytes")


def bit_unstuff():
    din = [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]

    def step(st, i):
        ones, dead, _ = st
        if i["din"] == 1:
            if dead:
                return (ones, True, None)
            ones += 1
            return (ones, ones == 7, "err" if ones == 7 else None)
        ev = None if dead else {5: "discard", 6: "flag"}.get(ones)
        return (0, False, ev)
    rows = clocked(len(din), [("din", din)], step=step,
                   out=lambda st, i: {"discard": int(st[2] == "discard"), "flag": int(st[2] == "flag"),
                                      "err": int(st[2] == "err")}, state=(0, False, None))
    return wave(rows, slot=10, outputs=("discard", "flag", "err"),
                note="five 1s then 0: discard. six 1s then 0: flag. a seventh 1: err",
                title="bit unstuffing: outputs pulse for the cycle after the edge that completes a pattern")


def vending():
    return fsm(560, 340, {"0¢": (130, 170), "5¢": (360, 70), "10¢": (360, 270)},
               [("0¢", "5¢", "nickel", .15), ("5¢", "0¢", "dime: vend", .15),
                ("0¢", "10¢", "dime", .15), ("10¢", "0¢", "nickel: vend\ndime: vend, change", .15),
                ("5¢", "10¢", "nickel", .2), ("0¢", "0¢", "no coin", 180),
                ("5¢", "5¢", "no coin", 0), ("10¢", "10¢", "no coin", 0)],
               reset=("0¢", 90), note="vend and change are high for the cycle after the edge",
               title="the vending machine's states are the amount inserted so far")


def traffic():
    st = {"MAIN_GREEN": (130, 110, "main_g side_r"), "MAIN_YELLOW": (430, 110, "main_y side_r"),
          "SIDE_GREEN": (430, 290, "main_r side_g"), "SIDE_YELLOW": (130, 290, "main_r side_y")}
    return fsm(570, 380, st,
               [("MAIN_GREEN", "MAIN_YELLOW", "car_side and t ≥ 4"), ("MAIN_YELLOW", "SIDE_GREEN", "t = 1"),
                ("SIDE_GREEN", "SIDE_YELLOW", "t = 3"), ("SIDE_YELLOW", "MAIN_GREEN", "t = 1")],
               r=52, reset=("MAIN_GREEN", -90), note="t restarts at 0 on entering each phase",
               title="the four traffic-light phases")


def arbiter_fixed():
    req = [(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1), (0, 0, 0)]

    def step(g, i):
        r = (i["req(0)"], i["req(1)"], i["req(2)"])
        if g is not None and r[g]:
            return g
        return next((k for k in range(3) if r[k]), None)
    rows = clocked(len(req), [(f"req({k})", [r[k] for r in req]) for k in range(3)], step=step,
                   out=lambda g, i: {f"gnt({k})": int(g == k) for k in range(3)}, state=None)
    return wave(rows, slot=18, outputs=("gnt(0)", "gnt(1)", "gnt(2)"),
                note="a held grant is kept even when a higher-priority request arrives",
                title="fixed-priority arbiter with grant hold")


def arbiter_rr():
    req = [(0, 0), (1, 1), (1, 1), (1, 1), (1, 0), (1, 1), (0, 1), (1, 1), (0, 0)]

    def step(st, i):
        last, g = st
        r = (i["req(0)"], i["req(1)"])
        if r == (1, 1):
            g = 1 - last if last is not None else 0
        elif r == (1, 0):
            g = 0
        elif r == (0, 1):
            g = 1
        else:
            g = None
        return (g if g is not None else last, g)
    rows = clocked(len(req), [(f"req({k})", [r[k] for r in req]) for k in range(2)], step=step,
                   out=lambda st, i: {f"gnt({k})": int(st[1] == k) for k in range(2)}, state=(None, None))
    return wave(rows, slot=18, outputs=("gnt(0)", "gnt(1)"), note="when both ask, they take turns",
                title="round-robin arbiter for two requesters")


def detect_then_enable():
    din = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0]

    def step(st, i):
        hist, left = st
        if left:
            left -= 1
            return ([] if left == 0 else hist, left)
        hist = (hist + [i["din"]])[-3:]
        return (hist, 3 if hist == [1, 1, 0] else 0)
    rows = clocked(len(din), [("din", din)], step=step, out=lambda st, i: {"go": int(st[1] > 0)},
                   state=([], 0))
    return wave(rows, slot=14, outputs=("go",),
                note="samples taken at the edges that end the 3 go cycles are ignored",
                title="1, 1, 0 triggers three cycles of go")


def timer_unit():
    svg = Svg(640, 150)
    steps = [("search", "for 1101"), ("shift in", "4 bits: delay"), ("count", "(delay+1)×10"),
             ("done", "until ack")]
    xs = [20 + 160 * k for k in range(4)]
    for (head, sub), x in zip(steps, xs):
        box(svg, x, 30, 120, 56, "")
        svg.text(x + 60, 50, head, "middle", "t b")
        svg.text(x + 60, 70, sub, "middle", "t sm m")
    for x in xs[:-1]:
        svg.arrow((x + 120, 58), (x + 160, 58))
    svg.text(xs[2] + 60, 100, "counting = 1", "middle", "t sm a")
    svg.text(xs[3] + 60, 100, "done = 1", "middle", "t sm a")
    svg.arrow((xs[3] + 60, 86), (xs[3] + 60, 130), (xs[0] + 60, 130), (xs[0] + 60, 88))
    svg.text(330, 122, "ack = 1", "middle", "t sm")
    return svg.render("the timer's four phases")


def elevator():
    return fsm(580, 330, {"IDLE": (140, 90), "DOOR": (140, 250, "door=1"), "MOVE1": (380, 90),
                          "MOVE2": (380, 250)},
               [("IDLE", "DOOR", "P(f)", .15), ("DOOR", "IDLE", "", .15), ("IDLE", "MOVE1", "request\nelsewhere"),
                ("MOVE1", "MOVE2", "", .0), ("MOVE2", "DOOR", "P(new f)"),
                ("MOVE2", "MOVE1", "keep going\nor turn", -.25), ("MOVE2", "IDLE", "no requests", 0),
                ("IDLE", "IDLE", "no requests", -90)],
               r=34, reset=("IDLE", 180), note="MOVE2 moves floor by one in direction dir, then decides",
               title="the elevator's phases; 'decide' runs in IDLE and at the end of MOVE2")


FIGURES = {
    "fsm_toggle": toggle(),
    "fsm_mealy": mealy(),
    "seq_1011": seq_1011(),
    "walker": walker(),
    "walker_fall": walker_fall(),
    "debounce": debounce(),
    "uart_rx_byte": uart_frame(0x4B, title="a UART frame: start bit, 8 data bits LSB first, stop bit"),
    "handshake_fifo1": handshake(),
    "onehot_next_state": abcd(False),
    "binary_next_state": abcd(False),
    "fsm_from_table": abcd(True),
    "header_packet": header_packet(),
    "uart_rx_parity": uart_frame(0x4B, parity=True,
                                 title="a UART frame with an odd parity bit between the data and the stop bit"),
    "bit_unstuff": bit_unstuff(),
    "vending": vending(),
    "traffic_light": traffic(),
    "arbiter_fixed3": arbiter_fixed(),
    "arbiter_rr2": arbiter_rr(),
    "detect_then_enable": detect_then_enable(),
    "timer_unit": timer_unit(),
    "elevator3": elevator(),
}
