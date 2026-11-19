library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  generic (
    W : positive := 6
  );
  port (
    din  : in  std_logic_vector(W - 1 downto 0);
    dout : out std_logic_vector(W - 1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  dout <= din(W - 2 downto 0) & din(W - 1);
end architecture rtl;
