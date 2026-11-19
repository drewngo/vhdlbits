SECTION = 1

PROBLEMS = [
    dict(
        num=1, name="one",
        concept="entity + architecture, concurrent assignment, character literals.",
        intro="""
            A VHDL design comes in two parts. The **entity** is the interface: its name and
            its ports. The **architecture** is the body: what the design does. Statements between
            `begin` and `end architecture` run concurrently, all the time, like wires.

            ```vhdl
            entity leds_off is
              port (led : out std_logic_vector(3 downto 0));
            end entity leds_off;

            architecture rtl of leds_off is
            begin
              led <= "0000";      -- a vector literal uses double quotes
            end architecture rtl;
            ```

            `<=` is the signal assignment operator. A single bit is a *character literal*
            in single quotes: `'0'` or `'1'`.
        """,
        verilog="`1'b1` is a syntax error. A single bit is written `'1'`, and there is no `assign` keyword.",
        task="Drive the output `o` permanently high.",
        ports="o: out sl",
        hints=["One line between `begin` and `end architecture`: `o <= ...;`"],
    ),
    dict(
        num=2, name="zero",
        concept="a design with only an output.",
        intro="""
            An entity doesn't need inputs. Constant drivers like this show up as tie-offs:
            unused enables pulled low, unused chip selects pulled high, and so on.

            ```vhdl
            spare_cs_n <= '1';   -- park an unused active-low chip select
            ```
        """,
        verilog="Same as before: no `1'b0`, no `assign`.",
        task="Drive the output `o` permanently low.",
        ports="o: out sl",
        hints=["A low bit is `'0'`."],
    ),
    dict(
        num=3, name="case_and_comments",
        concept="VHDL is case-insensitive, comments start with `--`, and a statement ends with `;`.",
        intro="""
            `SIGNAL`, `Signal` and `signal` are the same keyword, and `Data_In` and `DATA_IN`
            name the same object. Most code bases pick lowercase keywords and stick to it,
            but you will see every style in vendor code.

            ```vhdl
            -- this whole line is a comment
            Ready <= '1';  -- and so is everything after the dashes here
            ```

            VHDL-2008 also has block comments `/* ... */`, though `--` is far more common.

            The stub below deliberately mixes casing. It still compiles: case only
            matters inside character and string literals, where `'1'` and `"0Z"` mean
            exactly what they say (and `'z'` is not the same character as `'Z'`).
        """,
        verilog="Verilog identifiers are case-sensitive, so `clk` and `CLK` are different nets. In VHDL they are the same name, and declaring both is a redeclaration error.",
        task="Output the input inverted: `y` is the logical NOT of `a`. Use the `not` keyword.",
        ports="a: in sl; y: out sl",
        stub="""
            LIBRARY ieee;
            use IEEE.Std_Logic_1164.ALL;

            ENTITY top_module IS
              PORT (
                a : IN  std_logic;
                y : OUT STD_LOGIC
              );
            END ENTITY top_module;

            architecture RTL of TOP_MODULE is
              SIGNAL scratch : Std_Logic;  -- unused; shows that SIGNAL/signal are the same keyword
            begin
              -- Write your answer on the next line. Remember the ';' at the end.

            END ARCHITECTURE rtl;
        """,
        hints=["`y <= not a;` — and try writing it as `Y <= NOT A;` to see that it's the same thing."],
    ),
]
