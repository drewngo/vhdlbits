library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  generic (
    DEPTH : positive := 8;
    W     : positive := 8
  );
  port (
    clk, reset, push, pop : in  std_logic;
    din                   : in  std_logic_vector(7 downto 0);
    dout                  : out std_logic_vector(7 downto 0);
    full, empty           : out std_logic;
    count                 : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  type mem_t is array (0 to DEPTH - 1) of std_logic_vector(W - 1 downto 0);
  signal mem    : mem_t;
  signal rd, wr : integer range 0 to DEPTH - 1;
  signal cnt    : integer range 0 to DEPTH;
begin
  process(clk)
    variable do_push, do_pop : boolean;
  begin
    if rising_edge(clk) then
      if reset = '1' then
        rd  <= 0;
        wr  <= 0;
        cnt <= 0;
      else
        do_push := push = '1' and cnt < DEPTH;
        do_pop  := pop = '1' and cnt > 0;
        if do_push then
          mem(wr) <= din;
          wr      <= (wr + 1) mod DEPTH;
        end if;
        if do_pop then
          rd <= (rd + 1) mod DEPTH;
        end if;
        if do_push and not do_pop then
          cnt <= cnt + 1;
        elsif do_pop and not do_push then
          cnt <= cnt - 1;
        end if;
      end if;
    end if;
  end process;

  dout  <= mem(rd) when cnt > 0 else (others => '0');
  empty <= '1' when cnt = 0 else '0';
  full  <= '1' when cnt = DEPTH else '0';
  count <= std_logic_vector(to_unsigned(cnt, 4));
end architecture rtl;
