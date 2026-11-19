library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, en : in  std_logic;
    hh, mm, ss     : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal h, m, s : unsigned(7 downto 0);

  -- Increment a two-digit BCD value, wrapping from max to 0.
  function bcd_inc(v : unsigned(7 downto 0); max : unsigned(7 downto 0)) return unsigned is
  begin
    if v = max then
      return x"00";
    elsif v(3 downto 0) = 9 then
      return (v(7 downto 4) + 1) & x"0";
    else
      return v + 1;
    end if;
  end function bcd_inc;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        h <= x"00";
        m <= x"00";
        s <= x"00";
      elsif en = '1' then
        s <= bcd_inc(s, x"59");
        if s = x"59" then
          m <= bcd_inc(m, x"59");
          if m = x"59" then
            h <= bcd_inc(h, x"23");
          end if;
        end if;
      end if;
    end if;
  end process;
  hh <= std_logic_vector(h);
  mm <= std_logic_vector(m);
  ss <= std_logic_vector(s);
end architecture rtl;
