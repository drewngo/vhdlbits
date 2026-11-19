library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. Edit rev.vhd instead.
entity top_module is
  port (
    a  : in  std_logic_vector(4 downto 0);
    b  : in  std_logic_vector(12 downto 0);
    ra : out std_logic_vector(4 downto 0);
    rb : out std_logic_vector(12 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  u5:  entity work.rev port map (din => a, dout => ra);
  u13: entity work.rev port map (din => b, dout => rb);
end architecture rtl;
