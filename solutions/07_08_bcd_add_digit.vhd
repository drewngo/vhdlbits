library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    cin  : in  std_logic;
    s    : out std_logic_vector(3 downto 0);
    cout : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable t : unsigned(4 downto 0);
  begin
    t := resize(unsigned(a), 5) + unsigned(b) + cin;
    if t > 9 then
      t    := t + 6;
      cout <= '1';
    else
      cout <= '0';
    end if;
    s <= std_logic_vector(t(3 downto 0));
  end process;
end architecture rtl;
