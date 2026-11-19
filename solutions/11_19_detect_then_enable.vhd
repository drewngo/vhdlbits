library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, din : in  std_logic;
    go              : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (S_NONE, S_1, S_11, GO1, GO2, GO3);
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
      when S_NONE => next_state <= S_1  when din = '1' else S_NONE;
      when S_1    => next_state <= S_11 when din = '1' else S_NONE;
      when S_11   => next_state <= S_11 when din = '1' else GO1;
      when GO1    => next_state <= GO2;
      when GO2    => next_state <= GO3;
      when GO3    => next_state <= S_NONE;
    end case;
  end process;

  go <= '1' when state = GO1 or state = GO2 or state = GO3 else '0';
end architecture rtl;
