library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    a, b : in  std_logic;
    y    : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  component mod_a is
    port (
      in1, in2 : in  std_logic;
      o        : out std_logic
    );
  end component mod_a;
begin
  u0: mod_a port map (in1 => a, in2 => b, o => y);
end architecture rtl;
