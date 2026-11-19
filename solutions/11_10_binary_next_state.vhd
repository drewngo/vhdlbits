library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    state : in  std_logic_vector(1 downto 0);
    x     : in  std_logic;
    nxt   : out std_logic_vector(1 downto 0);
    y     : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  constant A : std_logic_vector(1 downto 0) := "00";
  constant B : std_logic_vector(1 downto 0) := "01";
  constant C : std_logic_vector(1 downto 0) := "10";
  constant D : std_logic_vector(1 downto 0) := "11";
begin
  process(all)
  begin
    case state is
      when A      => nxt <= B when x = '1' else A;
      when B      => nxt <= B when x = '1' else C;
      when C      => nxt <= D when x = '1' else A;
      when others => nxt <= B when x = '1' else C;
    end case;
  end process;
  y <= '1' when state = D else '0';
end architecture rtl;
