library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(7 downto 0);
    s    : out std_logic_vector(7 downto 0);
    sat  : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable wide : signed(8 downto 0);
  begin
    wide := resize(signed(a), 9) + resize(signed(b), 9);
    if wide > 127 then
      s   <= x"7F";
      sat <= '1';
    elsif wide < -128 then
      s   <= x"80";
      sat <= '1';
    else
      s   <= std_logic_vector(wide(7 downto 0));
      sat <= '0';
    end if;
  end process;
end architecture rtl;
