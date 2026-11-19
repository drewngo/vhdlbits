library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, load : in  std_logic;
    d         : in  std_logic_vector(63 downto 0);
    q         : out std_logic_vector(63 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal cells : std_logic_vector(63 downto 0);
begin
  process(clk)
    variable left, right : std_logic_vector(63 downto 0);
  begin
    if rising_edge(clk) then
      if load = '1' then
        cells <= d;
      else
        left  := '0' & cells(63 downto 1);
        right := cells(62 downto 0) & '0';
        cells <= left xor (cells or right);
      end if;
    end if;
  end process;
  q <= cells;
end architecture rtl;
