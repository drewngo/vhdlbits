library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, en, sin : in  std_logic;
    dout                : out std_logic_vector(7 downto 0);
    valid               : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal sr  : std_logic_vector(7 downto 0);
  signal cnt : integer range 0 to 7;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        cnt   <= 0;
        dout  <= (others => '0');
        valid <= '0';
      else
        valid <= '0';
        if en = '1' then
          sr <= sin & sr(7 downto 1);
          if cnt = 7 then
            dout  <= sin & sr(7 downto 1);
            valid <= '1';
            cnt   <= 0;
          else
            cnt <= cnt + 1;
          end if;
        end if;
      end if;
    end if;
  end process;
end architecture rtl;
