library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, load : in  std_logic;
    d                : in  std_logic_vector(7 downto 0);
    q                : out std_logic_vector(7 downto 0);
    done             : out std_logic
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
      elsif load = '1' then
        cnt <= unsigned(d);
      elsif cnt /= 0 then
        cnt <= cnt - 1;
      end if;
    end if;
  end process;
  q    <= std_logic_vector(cnt);
  done <= '1' when cnt = 0 else '0';
end architecture rtl;
