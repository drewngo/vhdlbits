library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, btn : in  std_logic;
    press           : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal clean : std_logic;
  signal cnt   : integer range 0 to 7;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      press <= '0';
      if reset = '1' then
        clean <= '0';
        cnt   <= 0;
      elsif btn = clean then
        cnt <= 0;
      elsif cnt = 7 then
        clean <= btn;
        cnt   <= 0;
        press <= btn;          -- '1' only for a 0 -> 1 change
      else
        cnt <= cnt + 1;
      end if;
    end if;
  end process;
end architecture rtl;
