library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    din        : in  std_logic_vector(7 downto 0);
    payload    : out std_logic_vector(15 downto 0);
    done       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (HUNT, B1, B2);
  signal state : state_t;
  signal first : std_logic_vector(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        state   <= HUNT;
        payload <= x"0000";
      else
        case state is
          when HUNT =>
            if din = x"A5" then
              state <= B1;
            end if;
          when B1 =>
            first <= din;
            state <= B2;
          when B2 =>
            payload <= first & din;
            done    <= '1';
            state   <= HUNT;
        end case;
      end if;
    end if;
  end process;
end architecture rtl;
