library ieee;
use ieee.std_logic_1164.all;

entity skid1 is
  port (
    clk, reset, in_valid, out_ready : in  std_logic;
    in_data                         : in  std_logic_vector(7 downto 0);
    in_ready, out_valid             : out std_logic;
    out_data                        : out std_logic_vector(7 downto 0)
  );
end entity skid1;

architecture rtl of skid1 is
  signal full  : std_logic;
  signal ready : std_logic;
  signal store : std_logic_vector(7 downto 0);
begin
  ready <= '1';

  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        full  <= '0';
        store <= x"00";
      else
        if full = '1' and out_ready = '1' then
          full <= '0';
        end if;
        if in_valid = '1' and ready = '1' then
          full  <= '1';
          store <= in_data;
        end if;
      end if;
    end if;
  end process;

  in_ready  <= ready;
  out_valid <= full;
  out_data  <= store;
end architecture rtl;
