library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    bin                  : in  std_logic_vector(7 downto 0);
    hundreds, tens, ones : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
    variable sr : unsigned(19 downto 0);
  begin
    sr := (others => '0');
    sr(7 downto 0) := unsigned(bin);
    for i in 1 to 8 loop
      for d in 0 to 2 loop
        if sr(8 + 4 * d + 3 downto 8 + 4 * d) >= 5 then
          sr(8 + 4 * d + 3 downto 8 + 4 * d) := sr(8 + 4 * d + 3 downto 8 + 4 * d) + 3;
        end if;
      end loop;
      sr := shift_left(sr, 1);
    end loop;
    hundreds <= std_logic_vector(sr(19 downto 16));
    tens     <= std_logic_vector(sr(15 downto 12));
    ones     <= std_logic_vector(sr(11 downto 8));
  end process;
end architecture rtl;
