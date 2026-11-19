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
  type state_t is (IDLE, DATA_BITS, PARITY, STOP, WAIT_IDLE);
  signal state  : state_t;
  signal sr     : std_logic_vector(7 downto 0);
  signal nbit   : integer range 0 to 7;
  signal odd_ok : std_logic;   -- running XOR of data + parity bits; '1' means odd parity
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
              state  <= DATA_BITS;
              nbit   <= 0;
              odd_ok <= '0';
            end if;
          when DATA_BITS =>
            sr     <= rxd & sr(7 downto 1);
            odd_ok <= odd_ok xor rxd;
            if nbit = 7 then
              state <= PARITY;
            else
              nbit <= nbit + 1;
            end if;
          when PARITY =>
            odd_ok <= odd_ok xor rxd;
            state  <= STOP;
          when STOP =>
            if rxd = '1' then
              if odd_ok = '1' then
                data <= sr;
                done <= '1';
              end if;
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
