library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    q          : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal r : std_logic_vector(31 downto 0);
begin
  process(clk)
    variable nxt : std_logic_vector(31 downto 0);
  begin
    if rising_edge(clk) then
      if reset = '1' then
        r <= x"00000001";
      else
        nxt     := r(0) & r(31 downto 1);
        nxt(21) := r(22) xor r(0);
        nxt(1)  := r(2) xor r(0);
        nxt(0)  := r(1) xor r(0);
        r <= nxt;
      end if;
    end if;
  end process;
  q <= r;
end architecture rtl;
