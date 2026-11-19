library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, start : in  std_logic;
    x                 : in  std_logic_vector(15 downto 0);
    root              : out std_logic_vector(7 downto 0);
    busy, done        : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal active : std_logic;
  signal xv     : unsigned(15 downto 0);
  signal r      : unsigned(7 downto 0);
  signal b      : integer range 0 to 7;
begin
  process(clk)
    variable t, rn : unsigned(7 downto 0);
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        active <= '0';
        root   <= x"00";
      elsif active = '0' then
        if start = '1' then
          xv     <= unsigned(x);
          r      <= (others => '0');
          b      <= 7;
          active <= '1';
        end if;
      else
        t    := r;
        t(b) := '1';
        if t * t <= xv then
          rn := t;
        else
          rn := r;
        end if;
        if b = 0 then
          active <= '0';
          done   <= '1';
          root   <= std_logic_vector(rn);
        else
          r <= rn;
          b <= b - 1;
        end if;
      end if;
    end if;
  end process;
  busy <= active;
end architecture rtl;
