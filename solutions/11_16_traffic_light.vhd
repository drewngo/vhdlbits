library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    clk, reset, car_side                           : in  std_logic;
    main_g, main_y, main_r, side_g, side_y, side_r : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type phase_t is (MAIN_GREEN, MAIN_YELLOW, SIDE_GREEN, SIDE_YELLOW);
  signal phase : phase_t;
  signal t     : integer range 0 to 4;
begin
  process(clk)
    procedure advance(nxt : phase_t) is
    begin
      phase <= nxt;
      t     <= 0;
    end procedure;
  begin
    if rising_edge(clk) then
      if reset = '1' then
        phase <= MAIN_GREEN;
        t     <= 0;
      else
        case phase is
          when MAIN_GREEN =>
            if car_side = '1' and t = 4 then
              advance(MAIN_YELLOW);
            elsif t < 4 then
              t <= t + 1;
            end if;
          when MAIN_YELLOW =>
            if t = 1 then advance(SIDE_GREEN); else t <= t + 1; end if;
          when SIDE_GREEN =>
            if t = 3 then advance(SIDE_YELLOW); else t <= t + 1; end if;
          when SIDE_YELLOW =>
            if t = 1 then advance(MAIN_GREEN); else t <= t + 1; end if;
        end case;
      end if;
    end if;
  end process;

  main_g <= '1' when phase = MAIN_GREEN else '0';
  main_y <= '1' when phase = MAIN_YELLOW else '0';
  main_r <= '1' when phase = SIDE_GREEN or phase = SIDE_YELLOW else '0';
  side_g <= '1' when phase = SIDE_GREEN else '0';
  side_y <= '1' when phase = SIDE_YELLOW else '0';
  side_r <= '1' when phase = MAIN_GREEN or phase = MAIN_YELLOW else '0';
end architecture rtl;
