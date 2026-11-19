library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    g : in  std_logic_vector(7 downto 0);
    b : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable acc : std_logic;
  begin
    acc := '0';
    for i in 7 downto 0 loop
      acc  := acc xor g(i);
      b(i) <= acc;
    end loop;
  end process;
end architecture rtl;
