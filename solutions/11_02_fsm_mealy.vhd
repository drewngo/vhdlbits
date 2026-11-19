library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, t : in  std_logic;
    y             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (S_OFF, S_ON);
  signal state, next_state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= S_OFF;
      else
        state <= next_state;
      end if;
    end if;
  end process;

  process(all)
  begin
    next_state <= state;
    if t = '1' then
      case state is
        when S_OFF => next_state <= S_ON;
        when S_ON  => next_state <= S_OFF;
      end case;
    end if;
  end process;

  y <= '1' when state = S_ON and t = '0' else '0';
end architecture rtl;
