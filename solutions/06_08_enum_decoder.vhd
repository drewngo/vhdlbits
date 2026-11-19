library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    sel       : in  std_logic_vector(1 downto 0);
    busy, fin : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type stage_t is (IDLE, LOAD, RUN, DONE);
  signal stage : stage_t;
begin
  stage <= stage_t'val(to_integer(unsigned(sel)));

  process(all)
  begin
    busy <= '0';
    fin  <= '0';
    case stage is
      when IDLE       => null;
      when LOAD | RUN => busy <= '1';
      when DONE       => fin  <= '1';
    end case;
  end process;
end architecture rtl;
