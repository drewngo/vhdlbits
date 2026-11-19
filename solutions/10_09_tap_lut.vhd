library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, en, sin : in  std_logic;
    addr         : in  std_logic_vector(2 downto 0);
    y            : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal sr : std_logic_vector(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if en = '1' then
        sr <= sr(6 downto 0) & sin;
      end if;
    end if;
  end process;
  y <= sr(to_integer(unsigned(addr)));
end architecture rtl;
