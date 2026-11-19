library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    state : in  std_logic_vector(3 downto 0);
    x     : in  std_logic;
    nxt   : out std_logic_vector(3 downto 0);
    y     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  -- state(0) = A, state(1) = B, state(2) = C, state(3) = D
begin
  nxt(0) <= (state(0) or state(2)) and not x;              -- A <- A/0, C/0
  nxt(1) <= (state(0) or state(1) or state(3)) and x;      -- B <- A/1, B/1, D/1
  nxt(2) <= (state(1) or state(3)) and not x;              -- C <- B/0, D/0
  nxt(3) <= state(2) and x;                                -- D <- C/1
  y      <= state(3);
end architecture rtl;
