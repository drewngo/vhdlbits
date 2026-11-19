library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    oh    : in  std_logic_vector(7 downto 0);
    idx   : out std_logic_vector(2 downto 0);
    valid : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable n   : natural range 0 to 8;
    variable pos : natural range 0 to 7;
  begin
    n   := 0;
    pos := 0;
    for i in oh'range loop
      if oh(i) = '1' then
        n   := n + 1;
        pos := i;
      end if;
    end loop;
    if n = 1 then
      idx   <= std_logic_vector(to_unsigned(pos, 3));
      valid <= '1';
    else
      idx   <= "000";
      valid <= '0';
    end if;
  end process;
end architecture rtl;
