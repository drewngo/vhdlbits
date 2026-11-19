library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, load : in  std_logic;
    d         : in  std_logic_vector(255 downto 0);
    q         : out std_logic_vector(255 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal grid : std_logic_vector(255 downto 0);
begin
  process(clk)
    function cell(g : std_logic_vector(255 downto 0); r, c : natural) return natural is
    begin
      if g((r mod 16) * 16 + (c mod 16)) = '1' then
        return 1;
      end if;
      return 0;
    end function cell;
    variable n   : natural range 0 to 8;
    variable nxt : std_logic_vector(255 downto 0);
  begin
    if rising_edge(clk) then
      if load = '1' then
        grid <= d;
      else
        for r in 0 to 15 loop
          for c in 0 to 15 loop
            n := cell(grid, r + 15, c + 15) + cell(grid, r + 15, c) + cell(grid, r + 15, c + 1)
               + cell(grid, r,      c + 15)                         + cell(grid, r,      c + 1)
               + cell(grid, r + 1,  c + 15) + cell(grid, r + 1,  c) + cell(grid, r + 1,  c + 1);
            if n = 3 or (n = 2 and grid(r * 16 + c) = '1') then
              nxt(r * 16 + c) := '1';
            else
              nxt(r * 16 + c) := '0';
            end if;
          end loop;
        end loop;
        grid <= nxt;
      end if;
    end if;
  end process;
  q <= grid;
end architecture rtl;
