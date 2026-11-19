library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, j, k : in  std_logic;
    q         : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  signal q_int : std_logic := '0';
begin
  q <= q_int;

  process(clk)
  begin
    if rising_edge(clk) then
      case std_logic_vector'(j & k) is
        when "01"   => q_int <= '0';
        when "10"   => q_int <= '1';
        when "11"   => q_int <= not q_int;
        when others => null;
      end case;
    end if;
  end process;
end architecture rtl;
