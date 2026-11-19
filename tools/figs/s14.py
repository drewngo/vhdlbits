from diagrams import Svg, box, frame, wave


def clock_gen():
    return wave([("clk", "01" * 10 + "0")], slot=16, marks=[20], grid=False,
                ticks={2 * k: str(10 * k) for k in range(11)},
                note="time in ns; the dashed line is std.env.finish at 100 ns",
                title="a 10 ns clock that starts low and rises at 5 ns")


def stimulus_timeline():
    return wave([("a", "0011100000"), ("b", "0000111100")], slot=28, marks=[10], grid=False,
                ticks={0: "0", 2: "10", 4: "20", 5: "25", 8: "40", 10: "50"},
                note="time in ns; finish at 50 ns", title="the stimulus timeline for a and b")


def tb_instance():
    return wave([("clk", "0101010101"), ("a", "0000001111"), ("b", "0000110011"), ("y", "0000000011")],
                slot=26, outputs=("y",), marks=[10], grid=False,
                ticks={2 * k: str(10 * k) for k in range(6)},
                note="time in ns; a and b change on falling edges; y = a and b",
                title="driving ab = 00, 01, 10, 11 on the first four falling edges")


def selfcheck(stim, dut, ins, outs, model, title, stim_sub="", model_sub=""):
    """A self-checking testbench: stimulus drives the DUT and a reference model; assert compares."""
    svg = Svg(700, 230)
    frame(svg, 10, 10, 680, 210, "tb")
    box(svg, 30, 50, 170, 64, "")
    svg.text(115, 74, stim, "middle", "t sm b")
    svg.text(115, 92, stim_sub, "middle", "t sm m")
    box(svg, 280, 50, 180, 64, "")
    svg.text(370, 74, dut, "middle", "t sm b")
    svg.text(370, 92, "DUT (provided)", "middle", "t sm m")
    box(svg, 280, 140, 180, 56, "")
    svg.text(370, 160, model, "middle", "t sm b")
    svg.text(370, 178, model_sub, "middle", "t sm m")
    box(svg, 530, 90, 145, 64, "")
    svg.text(602, 114, "assert", "middle", "t sm b")
    svg.text(602, 132, "actual = expected", "middle", "t sm m")
    svg.arrow((200, 82), (278, 82), cls="s bus")
    svg.text(240, 72, ins, "middle", "t sm")
    svg.arrow((240, 82), (240, 168), (278, 168), cls="s bus")
    svg.dot(240, 82)
    svg.arrow((460, 82), (500, 82), (500, 110), (528, 110), cls="s bus")
    svg.text(468, 72, outs, "start", "t sm a")
    svg.arrow((460, 168), (500, 168), (500, 134), (528, 134), cls="s bus")
    svg.text(468, 184, "expected", "start", "t sm m")
    return svg.render(title)


def tb_handshake():
    svg = Svg(660, 200)
    frame(svg, 10, 10, 640, 180, "tb")
    p = box(svg, 30, 50, 140, 100, "")
    svg.text(100, 86, "producer", "middle", "t sm b")
    svg.text(100, 104, "send(byte) ×50+", "middle", "t sm m")
    d = box(svg, 260, 50, 120, 100, "")
    svg.text(320, 94, "skid1", "middle", "t sm b")
    svg.text(320, 112, "DUT", "middle", "t sm m")
    c = box(svg, 470, 50, 160, 100, "")
    svg.text(550, 86, "consumer", "middle", "t sm b")
    svg.text(550, 104, "expect(byte),", "middle", "t sm m")
    svg.text(550, 120, "random out_ready", "middle", "t sm m")
    for y, lab, right in ((70, "in_valid", True), (95, "in_data", True), (125, "in_ready", False)):
        a, b = ((170, y), (258, y)) if right else ((260, y), (172, y))
        svg.arrow(a, b, cls="s bus" if lab.endswith("data") else "s")
        svg.text(215, y - 8, lab, "middle", "t sm")
    for y, lab, right in ((70, "out_valid", True), (95, "out_data", True), (125, "out_ready", False)):
        a, b = ((380, y), (468, y)) if right else ((470, y), (382, y))
        svg.arrow(a, b, cls="s bus" if lab.endswith("data") else "s")
        svg.text(425, y - 8, lab, "middle", "t sm")
    svg.text(330, 176, "also check: in_ready = 1 whenever out_valid = 0", "middle", "t sm m")
    return svg.render("a producer process and a consumer process talk to the buffer through valid/ready")


FIGURES = {
    "clock_gen": clock_gen(),
    "stimulus_timeline": stimulus_timeline(),
    "tb_instance": tb_instance(),
    "assert_basics": selfcheck("stimulus loop", "mux2", "a, b, sel", "y", "expected y",
                               "an exhaustive self-checking testbench for mux2",
                               stim_sub="all 8 combinations", model_sub="computed in the tb"),
    "tb_counter": selfcheck("clk, reset", "decade", "reset", "q", "reference model",
                            "testing the decade counter against a model inside the testbench",
                            stim_sub="incl. mid-cycle resets", model_sub="a counter in the tb"),
    "tb_textio": selfcheck("read vectors.txt", "adder", "a, b", "sum", "expected_sum",
                           "a file-driven testbench: each line gives a, b and the expected sum",
                           stim_sub="readline, hread", model_sub="third column"),
    "tb_random": selfcheck("uniform()", "comparator", "a, b", "lt", "signed(a) < signed(b)",
                           "constrained-random stimulus checked against the expected comparison",
                           stim_sub="1000 random pairs", model_sub="in the tb"),
    "tb_handshake": tb_handshake(),
}
