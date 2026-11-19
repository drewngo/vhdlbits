library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, areset, bump_l, bump_r : in  std_logic;
    go_l, go_r                  : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (LEFT, RIGHT);
  signal state, next_state : state_t;
begin
  process(clk, areset)
  begin
    if areset = '1' then
      state <= LEFT;
    elsif rising_edge(clk) then
      state <= next_state;
    end if;
  end process;

  process(all)
  begin
    next_state <= state;
    if bump_l = '1' and bump_r = '1' then
      next_state <= RIGHT when state = LEFT else LEFT;
    elsif bump_l = '1' then
      next_state <= RIGHT;
    elsif bump_r = '1' then
      next_state <= LEFT;
    end if;
  end process;

  go_l <= '1' when state = LEFT else '0';
  go_r <= '1' when state = RIGHT else '0';
end architecture rtl;
