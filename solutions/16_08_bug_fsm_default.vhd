library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, din : in  std_logic;
    found           : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (S_NONE, S_1, S_10, S_101, S_1011);
  signal state, next_state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= S_NONE;
      else
        state <= next_state;
      end if;
    end if;
  end process;

  process(all)
  begin
    case state is
      when S_NONE => next_state <= S_1    when din = '1' else S_NONE;
      when S_1    => next_state <= S_1    when din = '1' else S_10;
      when S_10   => next_state <= S_101  when din = '1' else S_NONE;
      when S_101  => next_state <= S_1011 when din = '1' else S_10;
      when S_1011 => next_state <= S_1    when din = '1' else S_10;
    end case;
  end process;

  found <= '1' when state = S_1011 else '0';
end architecture rtl;
