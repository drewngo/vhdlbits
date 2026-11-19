library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. Eight rising-edge D flip-flops with no reset.
entity my_dff8 is
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(7 downto 0);
    q   : out std_logic_vector(7 downto 0)
  );
end entity my_dff8;

architecture rtl of my_dff8 is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
