SECTION = 12

RAM32_DECLS = """
type ram_t is array (0 to 31) of std_logic_vector(7 downto 0);
signal ram : ram_t := (others => (others => '0'));
"""

PROBLEMS = [
    dict(
        num=1, name="rom_const", numeric=True,
        concept="a ROM as a `constant` array of `slv` indexed with `to_integer`.",
        intro="""
            A ROM is a constant array. Declare an array type, then a constant of that type,
            and index it with an integer:

            ```vhdl
            type sine_t is array (0 to 7) of std_logic_vector(7 downto 0);
            constant SINE : sine_t := (x"80", x"DA", x"FF", x"DA", x"80", x"25", x"00", x"25");
            ...
            sample <= SINE(to_integer(unsigned(phase)));
            ```

            The contents can also be computed by a function at elaboration time, which beats
            typing tables by hand.
        """,
        verilog="A `case` or an `initial` block filling a `reg` array. In VHDL the constant is part of the type system.",
        task="A 16×8 ROM whose word at address `a` is `a²` mod 256. The read is combinational: `data` shows the word at `addr`.",
        ports="addr: in slv(3:0); data: out slv(7:0)",
        hints=[
            "Either list the 16 values or write a function `init_rom return rom_t` with a loop.",
            "15² = 225 still fits in a byte, so \"mod 256\" never actually wraps here.",
        ],
    ),
    dict(
        num=2, name="rom_sync", mode="seq", numeric=True,
        concept="registered ROM read: the style that maps to block RAM.",
        intro="""
            FPGA block RAMs have a registered read port: you present the address before the
            clock edge and get the data after it. Describing the ROM with a registered output
            lets synthesis map it into a block RAM instead of LUTs.
        """,
        verilog="Same as reading a `reg` array inside `always @(posedge clk)`.",
        task="The ROM from 12.1 with a registered (1-cycle) read: at each rising edge, `data` takes the word at `addr`. No reset.",
        ports="clk: in sl; addr: in slv(3:0); data: out slv(7:0)",
        hints=["The same constant array, read inside `if rising_edge(clk)`."],
    ),
    dict(
        num=3, name="ram_sp", mode="seq", numeric=True,
        concept="array-of-vector `signal` as RAM; read-first vs. write-first.",
        intro="""
            A RAM is an array **signal** written in a clocked process. With a synchronous read
            in the same process, the order of the statements doesn't matter: the read sees the
            array as it was *before* this edge, because signals update after the process
            suspends. That's **read-first** behavior.

            ```vhdl
            if rising_edge(clk) then
              if wr = '1' then
                mem(to_integer(unsigned(a))) <= wdata;
              end if;
              rdata <= mem(to_integer(unsigned(a)));     -- old contents
            end if;
            ```

            The stub declares the RAM initialized to zeros so the grader can compare reads of
            never-written addresses.
        """,
        verilog="Same as nonblocking reads and writes of a `reg` array.",
        task="""
            32×8 single-port RAM `ram`. At each rising edge, if `we = '1'` write `din` at
            `addr`. `dout` is a synchronous read of `addr`, **read-first**: during a write it
            returns the old contents.
        """,
        ports="clk, we: in sl; addr: in slv(4:0); din: in slv(7:0); dout: out slv(7:0)",
        arch_decls=RAM32_DECLS,
        options={"bias": {"we": 0.4}},
        hints=["Exactly the process above."],
    ),
    dict(
        num=4, name="ram_write_first", mode="seq", numeric=True,
        concept="write-first read-during-write behavior.",
        intro="""
            Block RAMs can be configured to return the *new* data during a write
            (**write-first**). To describe it, read `din` instead of the array when writing:

            ```vhdl
            if wr = '1' then
              mem(i) <= wdata;
              rdata  <= wdata;
            else
              rdata  <= mem(i);
            end if;
            ```

            (A shared `variable` for the RAM would also produce write-first behavior, but
            shared variables in RTL are best avoided.)
        """,
        verilog="Same idea; nonblocking assignments alone give read-first.",
        task="Same as 12.3, but **write-first**: during a write, `dout` shows the new data.",
        ports="clk, we: in sl; addr: in slv(4:0); din: in slv(7:0); dout: out slv(7:0)",
        arch_decls=RAM32_DECLS,
        options={"bias": {"we": 0.4}},
        hints=["An `if we = '1' ... else ...` around the read."],
    ),
    dict(
        num=5, name="ram_dp", mode="seq", numeric=True,
        concept="simple dual-port RAM: independent write and read addresses.",
        intro="""
            A **simple dual-port** RAM has one write port and one read port with separate
            addresses, both on the same clock. This is the building block of FIFOs.
        """,
        verilog="Same.",
        task="""
            64×16 RAM. At each rising edge, if `we = '1'` write `din` at `waddr`, and
            `dout` takes the word at `raddr`. Reading the address being written returns the
            old data. The RAM starts as all zeros.
        """,
        ports="clk, we: in sl; waddr, raddr: in slv(5:0); din: in slv(15:0); dout: out slv(15:0)",
        arch_decls="""
            type ram_t is array (0 to 63) of std_logic_vector(15 downto 0);
            signal ram : ram_t := (others => (others => '0'));
        """,
        options={"bias": {"we": 0.5}, "copy": [["raddr", "waddr", 0.2]]},
        hints=["One clocked process with an indexed write and an indexed read."],
    ),
    dict(
        num=6, name="regfile_rv", mode="seq", numeric=True,
        concept="a RISC-V register file (x0 hard-wired to zero).",
        intro="""
            A CPU register file has two read ports (for `rs1` and `rs2`) and one write port.
            Reads are combinational so an instruction gets its operands in the same cycle.
            In RISC-V, register `x0` always reads as zero and ignores writes.
        """,
        verilog="Same.",
        task="""
            32 registers of 32 bits. `rd1` and `rd2` are combinational reads of registers
            `ra1` and `ra2`. At each rising edge, if `we = '1'` and `wa ≠ 0`, register `wa`
            takes `wd`. Register 0 always reads as zero. Active-high synchronous `reset`
            clears every register.
        """,
        ports="clk, reset, we: in sl; ra1, ra2, wa: in slv(4:0); wd: in slv(31:0); rd1, rd2: out slv(31:0)",
        options={"bias": {"we": 0.5}, "reset_prob": 0.005, "cycles": 800, "copy": [["ra1", "wa", 0.15], ["ra2", "wa", 0.15]]},
        hints=["An array of 32 vectors; the write is guarded by `wa /= \"00000\"`, so register 0 stays zero after reset."],
    ),
    dict(
        num=7, name="regfile_bypass", mode="seq", numeric=True,
        concept="write-through bypass (forwarding).",
        intro="""
            In a pipelined CPU, an instruction may read a register in the same cycle another
            instruction writes it. Without forwarding it would see the old value. A
            **bypass** compares the read and write addresses and forwards the write data.
        """,
        verilog="Same.",
        task="""
            Same as 12.6, but a read of the register being written **this cycle** returns
            `wd`: when `we = '1'`, `wa ≠ 0` and `ra1 = wa`, `rd1 = wd` (likewise for `rd2`).
            Register 0 still always reads as zero.
        """,
        ports="clk, reset, we: in sl; ra1, ra2, wa: in slv(4:0); wd: in slv(31:0); rd1, rd2: out slv(31:0)",
        options={"bias": {"we": 0.5}, "reset_prob": 0.005, "cycles": 800, "copy": [["ra1", "wa", 0.25], ["ra2", "wa", 0.25]]},
        hints=["Two comparators and two muxes in front of the 12.6 read ports."],
    ),
    dict(
        num=8, name="cam4", mode="seq", numeric=True,
        concept="content-addressable lookup.",
        intro="""
            A **CAM** answers "where is this value?" instead of "what is at this address?".
            Every entry compares against the key in parallel, and a priority encoder picks a
            match. Caches, TLBs and network lookups use them.
        """,
        verilog="Same.",
        task="""
            4 entries of 8 bits, each with a valid flag. At each rising edge, if `we = '1'`,
            entry `widx` takes `din` and becomes valid. Combinationally, `hit = '1'` when
            `key` equals some **valid** entry, and `hit_idx` is the lowest such index
            (`"00"` when there's no hit). Active-high synchronous `reset` invalidates all
            entries.
        """,
        ports="clk, reset, we: in sl; widx: in slv(1:0); din, key: in slv(7:0); hit: out sl; hit_idx: out slv(1:0)",
        options={"bias": {"we": 0.3}, "range": {"din": [0, 11], "key": [0, 11]}, "reset_prob": 0.01},
        after_ports="The grader keeps `din` and `key` in 0–11 so that hits are common.",
        hints=["A `for` loop from 3 down to 0 that overwrites the result leaves the lowest matching index."],
    ),
]
