library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din   : in  std_logic_vector(31 downto 0);
    count : out std_logic_vector(5 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable n : integer range 0 to 32;
  begin
    n := 0;
    for i in din'range loop
      if din(i) = '1' then
        n := n + 1;
      end if;
    end loop;
    count <= std_logic_vector(to_unsigned(n, 6));
  end process;
end architecture rtl;
