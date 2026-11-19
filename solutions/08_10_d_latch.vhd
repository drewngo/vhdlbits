library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    d, en : in  std_logic;
    q     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    if en = '1' then
      q <= d;
    end if;
  end process;
end architecture rtl;
