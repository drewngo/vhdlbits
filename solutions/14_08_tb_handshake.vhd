library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity tb is
end entity tb;

architecture sim of tb is
  constant N_BYTES : positive := 60;

  signal clk                 : std_logic := '0';
  signal reset               : std_logic := '1';
  signal in_valid, out_ready : std_logic := '0';
  signal in_data             : std_logic_vector(7 downto 0) := x"00";
  signal in_ready, out_valid : std_logic;
  signal out_data            : std_logic_vector(7 downto 0);
begin
  clk <= not clk after 5 ns;

  dut: entity work.skid1
    port map (clk => clk, reset => reset, in_valid => in_valid, out_ready => out_ready,
              in_data => in_data, in_ready => in_ready, out_valid => out_valid,
              out_data => out_data);

  reset_p: process
  begin
    wait until rising_edge(clk);
    wait until rising_edge(clk);
    reset <= '0';
    wait;
  end process;

  producer: process
    variable s1, s2 : positive := 11;
    variable r      : real;

    -- Hold valid and data until an edge where the buffer is ready.
    procedure send(byte : std_logic_vector(7 downto 0)) is
    begin
      in_valid <= '1';
      in_data  <= byte;
      loop
        wait until rising_edge(clk);
        exit when in_ready = '1';
      end loop;
      in_valid <= '0';
    end procedure;
  begin
    wait until reset = '0';
    for i in 1 to N_BYTES loop
      send(std_logic_vector(to_unsigned(i, 8)));
      uniform(s1, s2, r);
      if r < 0.3 then
        wait until rising_edge(clk);           -- occasional idle cycle
      end if;
    end loop;
    wait;
  end process;

  consumer: process
    variable s1, s2 : positive := 5;
    variable r      : real;

    -- Randomize backpressure until a transfer happens, then check its data.
    procedure expect(byte : std_logic_vector(7 downto 0)) is
      variable waited : natural := 0;
    begin
      loop
        uniform(s1, s2, r);
        out_ready <= '1' when r < 0.5 else '0';
        wait until rising_edge(clk);
        if out_valid = '1' and out_ready = '1' then
          assert out_data = byte
            report "expected " & to_hstring(byte) & ", got " & to_hstring(out_data)
            severity error;
          exit;
        end if;
        waited := waited + 1;
        assert waited < 100 report "timeout waiting for " & to_hstring(byte) severity failure;
      end loop;
    end procedure;
  begin
    wait until reset = '0';
    for i in 1 to N_BYTES loop
      expect(std_logic_vector(to_unsigned(i, 8)));
    end loop;
    out_ready <= '1';
    for i in 1 to 5 loop
      wait until rising_edge(clk);
      assert out_valid = '0' report "extra data after the last byte: " & to_hstring(out_data) severity error;
    end loop;
    std.env.finish;
  end process;

  protocol: process(clk)
  begin
    if rising_edge(clk) and reset = '0' then
      assert not (out_valid = '0' and in_ready = '0')
        report "in_ready is low while the buffer is empty" severity error;
    end if;
  end process;
end architecture sim;
