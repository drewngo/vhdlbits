library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a, b : in  std_logic_vector(99 downto 0);
    cin  : in  std_logic;
    sum  : out std_logic_vector(99 downto 0);
    cout : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal wide : unsigned(100 downto 0);
begin
  wide <= ('0' & unsigned(a)) + unsigned(b) + cin;
  sum  <= std_logic_vector(wide(99 downto 0));
  cout <= wide(100);
end architecture rtl;
