library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, load : in  std_logic;
    d                : in  std_logic_vector(7 downto 0);
    sout, busy       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal sr     : std_logic_vector(7 downto 0);
  signal remain : integer range 0 to 7;
  signal busy_r : std_logic;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        busy_r <= '0';
        sout   <= '0';
        remain <= 0;
      elsif busy_r = '0' then
        if load = '1' then
          sr     <= d(6 downto 0) & '0';
          sout   <= d(7);
          busy_r <= '1';
          remain <= 7;
        end if;
      elsif remain = 0 then
        busy_r <= '0';
        sout   <= '0';
      else
        sout   <= sr(7);
        sr     <= sr(6 downto 0) & '0';
        remain <= remain - 1;
      end if;
    end if;
  end process;
  busy <= busy_r;
end architecture rtl;
