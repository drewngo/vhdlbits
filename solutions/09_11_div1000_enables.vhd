library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    enables    : out std_logic_vector(2 downto 0);
    tick       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal c0, c1, c2 : unsigned(3 downto 0);
  signal en         : std_logic_vector(2 downto 0);

  function next_decade(c : unsigned(3 downto 0)) return unsigned is
  begin
    if c = 9 then
      return "0000";
    end if;
    return c + 1;
  end function next_decade;
begin
  en(0) <= '1';
  en(1) <= '1' when c0 = 9 else '0';
  en(2) <= '1' when c0 = 9 and c1 = 9 else '0';

  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        c0 <= (others => '0');
        c1 <= (others => '0');
        c2 <= (others => '0');
      else
        if en(0) = '1' then c0 <= next_decade(c0); end if;
        if en(1) = '1' then c1 <= next_decade(c1); end if;
        if en(2) = '1' then c2 <= next_decade(c2); end if;
      end if;
    end if;
  end process;

  enables <= en;
  tick    <= '1' when c0 = 9 and c1 = 9 and c2 = 9 else '0';
end architecture rtl;
