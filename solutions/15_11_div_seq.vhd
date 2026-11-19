library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    n                 : in  std_logic_vector(15 downto 0);
    d                 : in  std_logic_vector(7 downto 0);
    q                 : out std_logic_vector(15 downto 0);
    r                 : out std_logic_vector(7 downto 0);
    busy, done, dz    : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal active : std_logic;
  signal num    : unsigned(15 downto 0);   -- dividend bits still to bring down (MSB first)
  signal div    : unsigned(7 downto 0);
  signal rem_r  : unsigned(7 downto 0);
  signal quo    : unsigned(15 downto 0);
  signal low    : std_logic_vector(7 downto 0);
  signal k      : integer range 0 to 15;
begin
  process(clk)
    variable trial : unsigned(8 downto 0);
    variable nrem  : unsigned(7 downto 0);
    variable qbit  : std_logic;
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        active <= '0';
        q      <= (others => '0');
        r      <= (others => '0');
        dz     <= '0';
      elsif active = '0' then
        if start = '1' then
          num    <= unsigned(n);
          div    <= unsigned(d);
          low    <= n(7 downto 0);
          rem_r  <= (others => '0');
          quo    <= (others => '0');
          k      <= 0;
          active <= '1';
        end if;
      else
        trial := rem_r & num(15);
        if trial >= div then
          nrem := resize(trial - div, 8);
          qbit := '1';
        else
          nrem := trial(7 downto 0);
          qbit := '0';
        end if;
        rem_r <= nrem;
        quo   <= quo(14 downto 0) & qbit;
        num   <= shift_left(num, 1);
        if k = 15 then
          active <= '0';
          done   <= '1';
          if div = 0 then
            q  <= (others => '1');
            r  <= low;
            dz <= '1';
          else
            q  <= std_logic_vector(quo(14 downto 0) & qbit);
            r  <= std_logic_vector(nrem);
            dz <= '0';
          end if;
        else
          k <= k + 1;
        end if;
      end if;
    end if;
  end process;
  busy <= active;
end architecture rtl;
