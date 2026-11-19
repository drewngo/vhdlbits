library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, nickel, dime : in  std_logic;
    vend, change             : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type state_t is (C0, C5, C10);
  signal state : state_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      vend   <= '0';
      change <= '0';
      if reset = '1' then
        state <= C0;
      else
        case state is
          when C0 =>
            if nickel = '1' then
              state <= C5;
            elsif dime = '1' then
              state <= C10;
            end if;
          when C5 =>
            if nickel = '1' then
              state <= C10;
            elsif dime = '1' then
              vend  <= '1';
              state <= C0;
            end if;
          when C10 =>
            if nickel = '1' then
              vend  <= '1';
              state <= C0;
            elsif dime = '1' then
              vend   <= '1';
              change <= '1';
              state  <= C0;
            end if;
        end case;
      end if;
    end if;
  end process;
end architecture rtl;
