library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din   : in  std_logic_vector(15 downto 0);
    idx   : out std_logic_vector(3 downto 0);
    valid : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    idx   <= "0000";
    valid <= '0';
    for i in 15 downto 0 loop
      if din(i) = '1' then
        idx   <= std_logic_vector(to_unsigned(i, 4));
        valid <= '1';
        exit;
      end if;
    end loop;
  end process;
end architecture rtl;
