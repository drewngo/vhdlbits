library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk   : in  std_logic;
    din   : in  std_logic_vector(7 downto 0);
    pulse : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal prev : std_logic_vector(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      prev  <= din;
      pulse <= din xor prev;
    end if;
  end process;
end architecture rtl;
