library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, valid : in  std_logic;
    x                 : in  std_logic_vector(7 downto 0);
    y                 : out std_logic_vector(10 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal d0, d1, d2 : signed(7 downto 0);
begin
  process(clk)
    variable xs : signed(10 downto 0);
  begin
    if rising_edge(clk) then
      if reset = '1' then
        d0 <= (others => '0');
        d1 <= (others => '0');
        d2 <= (others => '0');
        y  <= (others => '0');
      elsif valid = '1' then
        xs := resize(signed(x), 11);
        y  <= std_logic_vector(xs
                               + resize(d0, 11) + resize(d0, 11) + resize(d0, 11)
                               + resize(d1, 11) + resize(d1, 11) + resize(d1, 11)
                               + resize(d2, 11));
        d0 <= signed(x);
        d1 <= d0;
        d2 <= d1;
      end if;
    end if;
  end process;
end architecture rtl;
