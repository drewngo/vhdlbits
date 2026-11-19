library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    a, b              : in  std_logic_vector(7 downto 0);
    p                 : out std_logic_vector(15 downto 0);
    busy, done        : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal active : std_logic;
  signal acc    : unsigned(15 downto 0);
  signal mcand  : unsigned(15 downto 0);
  signal mplier : unsigned(7 downto 0);
  signal k      : integer range 0 to 7;
begin
  process(clk)
    variable nacc : unsigned(15 downto 0);
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        active <= '0';
        p      <= (others => '0');
      elsif active = '0' then
        if start = '1' then
          acc    <= (others => '0');
          mcand  <= resize(unsigned(a), 16);
          mplier <= unsigned(b);
          k      <= 0;
          active <= '1';
        end if;
      else
        nacc := acc;
        if mplier(0) = '1' then
          nacc := acc + mcand;
        end if;
        acc    <= nacc;
        mcand  <= shift_left(mcand, 1);
        mplier <= shift_right(mplier, 1);
        if k = 7 then
          active <= '0';
          done   <= '1';
          p      <= std_logic_vector(nacc);
        else
          k <= k + 1;
        end if;
      end if;
    end if;
  end process;
  busy <= active;
end architecture rtl;
