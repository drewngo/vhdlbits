library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, areset, bump_l, bump_r, ground : in  std_logic;
    go_l, go_r, falling                 : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (LEFT, RIGHT, FALL_L, FALL_R);
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
    case state is
      when LEFT =>
        if ground = '0' then
          next_state <= FALL_L;
        elsif bump_l = '1' then
          next_state <= RIGHT;   -- bump_l alone, or both bumps: reverse
        end if;
      when RIGHT =>
        if ground = '0' then
          next_state <= FALL_R;
        elsif bump_r = '1' then
          next_state <= LEFT;    -- bump_r alone, or both bumps: reverse
        end if;
      when FALL_L =>
        if ground = '1' then
          next_state <= LEFT;
        end if;
      when FALL_R =>
        if ground = '1' then
          next_state <= RIGHT;
        end if;
    end case;
  end process;

  go_l    <= '1' when state = LEFT else '0';
  go_r    <= '1' when state = RIGHT else '0';
  falling <= '1' when state = FALL_L or state = FALL_R else '0';
end architecture rtl;
