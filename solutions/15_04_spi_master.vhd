library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, start, miso : in  std_logic;
    tx                      : in  std_logic_vector(7 downto 0);
    sclk, mosi, cs_n, done  : out std_logic;
    rx                      : out std_logic_vector(7 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  signal active : std_logic;
  signal c      : integer range 0 to 31;
  signal sh_tx  : std_logic_vector(7 downto 0);
  signal sh_rx  : std_logic_vector(7 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      done <= '0';
      if reset = '1' then
        active <= '0';
        cs_n   <= '1';
        sclk   <= '0';
        mosi   <= '0';
        rx     <= x"00";
      elsif active = '0' then
        if start = '1' then
          active <= '1';
          cs_n   <= '0';
          sh_tx  <= tx;
          mosi   <= tx(7);
          c      <= 0;
        end if;
      else
        if c mod 4 = 1 then                     -- sclk rises after this edge: sample
          sh_rx <= sh_rx(6 downto 0) & miso;
        end if;
        if c = 31 then
          active <= '0';
          cs_n   <= '1';
          sclk   <= '0';
          mosi   <= '0';
          done   <= '1';
          rx     <= sh_rx;
        else
          c <= c + 1;
          if (c + 1) mod 4 >= 2 then
            sclk <= '1';
          else
            sclk <= '0';
          end if;
          if (c + 1) mod 4 = 0 then             -- sclk falls: next data bit
            mosi  <= sh_tx(6);
            sh_tx <= sh_tx(6 downto 0) & '0';
          end if;
        end if;
      end if;
    end if;
  end process;
end architecture rtl;
