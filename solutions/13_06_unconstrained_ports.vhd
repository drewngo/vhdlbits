library ieee;
use ieee.std_logic_1164.all;

entity rev is
  port (
    din  : in  std_logic_vector;
    dout : out std_logic_vector
  );
end entity rev;

architecture rtl of rev is
begin
  gen_rev: for i in 0 to din'length - 1 generate
    dout(dout'low + i) <= din(din'high - i);
  end generate gen_rev;
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

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
