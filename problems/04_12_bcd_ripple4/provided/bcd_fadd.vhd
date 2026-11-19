library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Provided: do not edit. One-digit BCD adder: a + b + cin, with valid BCD inputs (0-9).
entity bcd_fadd is
  port (
    a, b : in  std_logic_vector(3 downto 0);
    cin  : in  std_logic;
    s    : out std_logic_vector(3 downto 0);
    cout : out std_logic
  );
end entity bcd_fadd;

architecture rtl of bcd_fadd is
begin
  process(all)
    variable t : unsigned(4 downto 0);
  begin
    t := ('0' & unsigned(a)) + ('0' & unsigned(b)) + cin;  -- VHDL-2008: unsigned + std_ulogic
    if t > 9 then
      t := t + 6;
      cout <= '1';
    else
      cout <= '0';
    end if;
    s <= std_logic_vector(t(3 downto 0));
  end process;
end architecture rtl;
