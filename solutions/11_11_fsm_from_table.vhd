library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, x : in  std_logic;
    y             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (A, B, C, D);
  signal state, next_state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= A;
      else
        state <= next_state;
      end if;
    end if;
  end process;

  process(all)
  begin
    case state is
      when A => next_state <= B when x = '1' else A;
      when B => next_state <= B when x = '1' else C;
      when C => next_state <= D when x = '1' else A;
      when D => next_state <= B when x = '1' else C;
    end case;
  end process;

  y <= '1' when state = D else '0';
end architecture rtl;
