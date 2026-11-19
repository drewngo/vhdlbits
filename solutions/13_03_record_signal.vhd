library ieee;
use ieee.std_logic_1164.all;

package my_pkg is
  type pkt_t is record
    valid : std_logic;
    addr  : std_logic_vector(3 downto 0);
    data  : std_logic_vector(7 downto 0);
  end record pkt_t;

  constant PKT_NONE : pkt_t := (valid => '0', addr => (others => '0'), data => (others => '0'));
end package my_pkg;

library ieee;
use ieee.std_logic_1164.all;
use work.my_pkg.all;

entity top_module is
  port (
    clk, reset, v_in : in  std_logic;
    a_in             : in  std_logic_vector(3 downto 0);
    d_in             : in  std_logic_vector(7 downto 0);
    v_out            : out std_logic;
    a_out            : out std_logic_vector(3 downto 0);
    d_out            : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal s1, s2 : pkt_t;
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        s1 <= PKT_NONE;
        s2 <= PKT_NONE;
      else
        s1 <= (valid => v_in, addr => a_in, data => d_in);
        s2 <= s1;
      end if;
    end if;
  end process;

  v_out <= s2.valid;
  a_out <= s2.addr;
  d_out <= s2.data;
end architecture rtl;
