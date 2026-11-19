library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    req        : in  std_logic_vector(1 downto 0);
    gnt        : out std_logic_vector(1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal last_was_1 : std_logic;   -- '1' if requester 1 was granted most recently
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        gnt        <= "00";
        last_was_1 <= '1';
      else
        case req is
          when "01" =>
            gnt        <= "01";
            last_was_1 <= '0';
          when "10" =>
            gnt        <= "10";
            last_was_1 <= '1';
          when "11" =>
            if last_was_1 = '1' then
              gnt        <= "01";
              last_was_1 <= '0';
            else
              gnt        <= "10";
              last_was_1 <= '1';
            end if;
          when others =>
            gnt <= "00";
        end case;
      end if;
    end if;
  end process;
end architecture rtl;
