library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    a   : in  std_logic_vector(7 downto 0);
    mag : out std_logic_vector(7 downto 0);
    neg : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  mag <= std_logic_vector(abs(signed(a)));
  neg <= a(7);
end architecture rtl;
