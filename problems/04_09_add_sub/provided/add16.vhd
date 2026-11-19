library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Provided: do not edit. 16-bit adder with carry in and carry out.
entity add16 is
  port (
    a, b : in  std_logic_vector(15 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(15 downto 0);
    cout : out std_logic
  );
end entity add16;

architecture rtl of add16 is
  signal full : unsigned(16 downto 0);
begin
  full <= ('0' & unsigned(a)) + ('0' & unsigned(b)) + cin;  -- VHDL-2008: unsigned + std_ulogic
  sum  <= std_logic_vector(full(15 downto 0));
  cout <= full(16);
end architecture rtl;
