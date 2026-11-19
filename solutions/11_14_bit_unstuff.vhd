library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, din     : in  std_logic;
    discard, flag, err : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (ONES0, ONES1, ONES2, ONES3, ONES4, ONES5, ONES6, S_DISC, S_FLAG, S_ERR, S_ERR_WAIT);
  signal state, next_state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= ONES0;
      else
        state <= next_state;
      end if;
    end if;
  end process;

  process(all)
  begin
    case state is
      when ONES0 | S_DISC | S_FLAG => next_state <= ONES1 when din = '1' else ONES0;
      when ONES1    => next_state <= ONES2 when din = '1' else ONES0;
      when ONES2    => next_state <= ONES3 when din = '1' else ONES0;
      when ONES3    => next_state <= ONES4 when din = '1' else ONES0;
      when ONES4    => next_state <= ONES5 when din = '1' else ONES0;
      when ONES5    => next_state <= ONES6 when din = '1' else S_DISC;
      when ONES6    => next_state <= S_ERR   when din = '1' else S_FLAG;
      when S_ERR      => next_state <= S_ERR_WAIT when din = '1' else ONES0;
      when S_ERR_WAIT => next_state <= S_ERR_WAIT when din = '1' else ONES0;
    end case;
  end process;

  discard <= '1' when state = S_DISC else '0';
  flag    <= '1' when state = S_FLAG else '0';
  err     <= '1' when state = S_ERR else '0';
end architecture rtl;
