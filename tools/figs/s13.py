from diagrams import Svg, bitfield, box, frame


def package_function():
    svg = Svg(520, 192)
    box(svg, 20, 20, 220, 60, "")
    svg.text(30, 38, "package my_pkg is", "start", "t sm b")
    svg.text(30, 58, "  function popcount(...)", "start", "t sm")
    box(svg, 20, 100, 220, 60, "")
    svg.text(30, 118, "package body my_pkg is", "start", "t sm b")
    svg.text(30, 138, "  the function's body", "start", "t sm")
    svg.text(130, 176, "both in my_pkg.vhd", "middle", "t sm m")
    box(svg, 320, 50, 180, 70, "")
    svg.text(330, 68, "use work.my_pkg.all;", "start", "t sm")
    svg.text(330, 88, "top_module", "start", "t sm b")
    svg.text(330, 106, "ca <= popcount(a)", "start", "t sm m")
    svg.arrow((240, 50), (318, 70))
    svg.text(280, 44, "declares", "middle", "t sm m")
    svg.line(130, 80, 130, 100, "s thin dash")
    return svg.render("the package declaration is what users see; the package body implements it")


def record_signal():
    svg = Svg(560, 200)
    regs = []
    for k, x in enumerate((170, 330)):
        p = box(svg, x, 30, 90, 130, f"stage {k + 1}", left=[("valid", .35), ("addr", .55), ("data", .75)],
                right=[("valid", .35), ("addr", .55), ("data", .75)], title_y=46)
        regs.append(p)
        svg.poly([(x, 150), (x + 9, 155), (x, 160)])
    rows = {"valid": .35, "addr": .55, "data": .75}
    for nm, (pin, out) in {"valid": ("v_in", "v_out"), "addr": ("a_in", "a_out"),
                           "data": ("d_in", "d_out")}.items():
        y = 30 + 130 * rows[nm]
        cls = "s" if nm == "valid" else "s bus"
        svg.wire((80, y), (170, y), cls=cls); svg.pin(80, y, pin)
        svg.wire((260, y), (330, y), cls=cls)
        svg.wire((420, y), (490, y), cls=cls); svg.pin(490, y, out, "right", "t a b")
    svg.text(295, 186, "each stage is one signal of type pkt_t", "middle", "t sm m")
    return svg.render("two pipeline stages, each a pkt_t record holding valid, addr and data")


def array_of_vectors():
    return bitfield([
        ("din", [(f"byte {i}", 8 * i + 7, 8 * i) for i in range(7, -1, -1)]),
    ], bw=8, note="bytes(i) := din(8*i+7 downto 8*i)", title="din unpacked into an array of 8 bytes")


def enum_attributes():
    svg = Svg(620, 120)
    names = ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "VIOLET"]
    for k, nm in enumerate(names):
        x = 20 + 98 * k
        box(svg, x, 30, 80, 36, "")
        svg.text(x + 40, 48, nm, "middle", "t sm b")
        svg.text(x + 40, 20, f"'pos = {k}", "middle", "t sm m")
        if k < 5:
            svg.arrow((x + 80, 48), (x + 98, 48))
    svg.arrow((20 + 98 * 5 + 40, 66), (20 + 98 * 5 + 40, 92), (60, 92), (60, 68))
    svg.text(310, 104, "next of color_t'high wraps to color_t'low", "middle", "t sm m")
    return svg.render("color_t in declaration order, with each value's position")


def unconstrained_ports():
    svg = Svg(440, 170)
    frame(svg, 50, 10, 330, 150, "top_module (provided)")
    for k, (i, o, w) in enumerate((("a", "ra", 5), ("b", "rb", 13))):
        y = 40 + 70 * k
        p = box(svg, 160, y, 110, 50, "rev", left=["din"], right=["dout"], title_y=y + 14)
        svg.text(215, y + 34, f"{w} bits", "middle", "t sm a")
        svg.wire((50, p["din"][1]), p["din"], cls="s bus"); svg.pin(50, p["din"][1], i)
        svg.wire(p["dout"], (380, p["dout"][1]), cls="s bus"); svg.pin(380, p["dout"][1], o, "right", "t a b")
    return svg.render("one rev entity, instantiated at two widths; the ports take their size from the actuals")


def generic_package():
    svg = Svg(540, 170)
    box(svg, 20, 50, 160, 60, "")
    svg.text(100, 68, "package sat_pkg", "middle", "t sm b")
    svg.text(100, 88, "generic (W)", "middle", "t sm m")
    for k, w in enumerate((8, 12)):
        y = 20 + 80 * k
        box(svg, 270, y, 220, 50, "")
        svg.text(380, y + 17, f"sat{w}: new sat_pkg", "middle", "t sm b")
        svg.text(380, y + 35, f"generic map (W => {w})", "middle", "t sm m")
        svg.arrow((180, 80), (268, y + 25))
    svg.text(380, 162, "sat8.sat_add(a8, b8), sat12.sat_add(a12, b12)", "middle", "t sm m")
    return svg.render("one generic package, instantiated once per width")


FIGURES = {
    "package_function": package_function(),
    "record_signal": record_signal(),
    "array_of_vectors": array_of_vectors(),
    "enum_attributes": enum_attributes(),
    "unconstrained_ports": unconstrained_ports(),
    "generic_package": generic_package(),
}
