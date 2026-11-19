library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, we : in  std_logic;
    ra1, ra2, wa   : in  std_logic_vector(4 downto 0);
    wd             : in  std_logic_vector(31 downto 0);
    rd1, rd2       : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type regs_t is array (0 to 31) of std_logic_vector(31 downto 0);
  signal regs : regs_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        regs <= (others => (others => '0'));
      elsif we = '1' and wa /= "00000" then
        regs(to_integer(unsigned(wa))) <= wd;
      end if;
    end if;
  end process;

  rd1 <= regs(to_integer(unsigned(ra1)));
  rd2 <= regs(to_integer(unsigned(ra2)));
end architecture rtl;
