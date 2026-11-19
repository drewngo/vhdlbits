library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    data              : in  std_logic_vector(7 downto 0);
    txd, busy         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal sr     : std_logic_vector(8 downto 0);   -- stop bit & data, still to send
  signal remain : integer range 0 to 9;           -- bits left after the current one
  signal active : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        active <= '0';
        txd    <= '1';
        remain <= 0;
      elsif active = '0' then
        if start = '1' then
          sr     <= '1' & data;
          txd    <= '0';                -- start bit
          active <= '1';
          remain <= 9;
        end if;
      elsif remain = 0 then
        active <= '0';
        txd    <= '1';
      else
        txd    <= sr(0);
        sr     <= '1' & sr(8 downto 1);
        remain <= remain - 1;
      end if;
    end if;
  end process;
  busy <= active;
end architecture rtl;
