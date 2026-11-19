# The debugging problems restate earlier specs, so they reuse those problems' diagrams.
from figs.s03 import gray_decode
from figs.s05 import wide_mux
from figs.s08 import async_reset
from figs.s09 import decade
from figs.s11 import handshake, seq_1011

FIGURES = {
    "bug_sensitivity": wide_mux(4, ["a", "b", "c", "c"], "sel", "y",
                                "y = a when sel = 00, b when sel = 01, and c otherwise", bus=False),
    "bug_off_by_one": decade(),
    "bug_async_reset": async_reset(),
    "bug_fsm_default": seq_1011(),
    "bug_handshake": handshake(),
    "bug_gray_loop": gray_decode(),
    "bug_case_others": wide_mux(8, ["d0", "d1", "d2", "d3", "d4", "d5", '"0000"', '"0000"'], "sel", "y",
                                "a 6-to-1 mux; sel = 6 or 7 gives 0000"),
}
