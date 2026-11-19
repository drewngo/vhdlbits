library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, rxd : in  std_logic;
    data            : out std_logic_vector(7 downto 0);
    done            : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (IDLE, DATA_BITS, STOP, WAIT_IDLE);
  signal state : state_t;
  signal sr    : std_logic_vector(7 downto 0);
  signal nbit  : integer range 0 to 7;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        state <= IDLE;
        data  <= x"00";
      else
        case state is
          when IDLE =>
            if rxd = '0' then
              state <= DATA_BITS;
              nbit  <= 0;
            end if;
          when DATA_BITS =>
            sr <= rxd & sr(7 downto 1);
            if nbit = 7 then
              state <= STOP;
            else
              nbit <= nbit + 1;
            end if;
          when STOP =>
            if rxd = '1' then
              data  <= sr;
              done  <= '1';
              state <= IDLE;
            else
              state <= WAIT_IDLE;
            end if;
          when WAIT_IDLE =>
            if rxd = '1' then
              state <= IDLE;
            end if;
        end case;
      end if;
    end if;
  end process;
end architecture rtl;
