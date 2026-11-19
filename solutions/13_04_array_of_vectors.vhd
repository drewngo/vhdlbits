library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    din  : in  std_logic_vector(63 downto 0);
    maxv : out std_logic_vector(7 downto 0);
    maxi : out std_logic_vector(2 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type word_array is array (natural range <>) of std_logic_vector(7 downto 0);
  signal bytes : word_array(0 to 7);
begin
  gen_unpack: for i in 0 to 7 generate
    bytes(i) <= din(8 * i + 7 downto 8 * i);
  end generate gen_unpack;

  process(all)
    variable best : natural range 0 to 7;
  begin
    best := 0;
    for i in 1 to 7 loop
      if unsigned(bytes(i)) > unsigned(bytes(best)) then
        best := i;
      end if;
    end loop;
    maxv <= bytes(best);
    maxi <= std_logic_vector(to_unsigned(best, 3));
  end process;
end architecture rtl;
