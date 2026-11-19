library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    duty       : in  std_logic_vector(7 downto 0);
    pwm        : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal cnt : unsigned(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        cnt <= (others => '0');
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
  pwm <= '1' when cnt < unsigned(duty) else '0';
end architecture rtl;
