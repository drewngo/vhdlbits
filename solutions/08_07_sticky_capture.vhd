library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    din        : in  std_logic_vector(31 downto 0);
    cap        : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal prev : std_logic_vector(31 downto 0);
  signal held : std_logic_vector(31 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      prev <= din;
      if reset = '1' then
        held <= (others => '0');
      else
        held <= held or (prev and not din);
      end if;
    end if;
  end process;
  cap <= held;
end architecture rtl;
