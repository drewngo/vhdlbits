library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, din, ack : in  std_logic;
    counting, done       : out std_logic;
    remaining            : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (S_NONE, S_1, S_11, S_110, SHIFT, COUNT, FINISHED);
  signal state : state_t;
  signal delay : unsigned(3 downto 0);
  signal nbits : integer range 0 to 3;
  signal sub   : integer range 0 to 9;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state <= S_NONE;
      else
        case state is
          -- search for 1101 (with overlap)
          when S_NONE => state <= S_1 when din = '1' else S_NONE;
          when S_1    => state <= S_11 when din = '1' else S_NONE;
          when S_11   => state <= S_11 when din = '1' else S_110;
          when S_110  =>
            if din = '1' then
              state <= SHIFT;
              nbits <= 0;
            else
              state <= S_NONE;
            end if;
          when SHIFT =>
            delay <= delay(2 downto 0) & din;
            if nbits = 3 then
              state <= COUNT;
              sub   <= 0;
            else
              nbits <= nbits + 1;
            end if;
          when COUNT =>
            if sub = 9 then
              sub <= 0;
              if delay = 0 then
                state <= FINISHED;
              else
                delay <= delay - 1;
              end if;
            else
              sub <= sub + 1;
            end if;
          when FINISHED =>
            if ack = '1' then
              state <= S_NONE;
            end if;
        end case;
      end if;
    end if;
  end process;

  counting  <= '1' when state = COUNT else '0';
  done      <= '1' when state = FINISHED else '0';
  remaining <= std_logic_vector(delay) when state = COUNT else "0000";
end architecture rtl;
