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
  begin
    if rising_edge(clk) then
      if load = '1' then
        cells <= d;
      else
        -- left neighbour of cell i is cells(i+1), right neighbour is cells(i-1)
        cells <= ('0' & cells(63 downto 1)) xor (cells(62 downto 0) & '0');
      end if;
    end if;
  end process;
  q <= cells;
end architecture rtl;
