library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(3 downto 0);
    cout : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable c : std_logic;
  begin
    c := cin;
    for i in 0 to 3 loop
      sum(i) <= a(i) xor b(i) xor c;
      c      := (a(i) and b(i)) or (a(i) and c) or (b(i) and c);
    end loop;
    cout <= c;
  end process;
end architecture rtl;
