library ieee;
use ieee.std_logic_1164.all;

-- Provided: do not edit. An N-bit register with no reset.
entity reg_n is
  generic (N : positive);
  port (
    clk : in  std_logic;
    d   : in  std_logic_vector(N - 1 downto 0);
    q   : out std_logic_vector(N - 1 downto 0)
  );
end entity reg_n;

architecture rtl of reg_n is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      q <= d;
    end if;
  end process;
end architecture rtl;
