library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset, we : in  std_logic;
    widx           : in  std_logic_vector(1 downto 0);
    din, key       : in  std_logic_vector(7 downto 0);
    hit            : out std_logic;
    hit_idx        : out std_logic_vector(1 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type entries_t is array (0 to 3) of std_logic_vector(7 downto 0);
  signal entries : entries_t;
  signal valid   : std_logic_vector(3 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        valid <= "0000";
      elsif we = '1' then
        entries(to_integer(unsigned(widx))) <= din;
        valid(to_integer(unsigned(widx)))   <= '1';
      end if;
    end if;
  end process;

  process(all)
  begin
    hit     <= '0';
    hit_idx <= "00";
    for i in 3 downto 0 loop
      if valid(i) = '1' and entries(i) = key then
        hit     <= '1';
        hit_idx <= std_logic_vector(to_unsigned(i, 2));
      end if;
    end loop;
  end process;
end architecture rtl;
