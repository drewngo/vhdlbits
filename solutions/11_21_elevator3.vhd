library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_module is
  port (
    clk, reset : in  std_logic;
    call       : in  std_logic_vector(2 downto 0);
    floor      : out std_logic_vector(1 downto 0);
    door       : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
  type phase_t is (IDLE, DOOR_OPEN, MOVE1, MOVE2);
  signal phase   : phase_t;
  signal cur     : integer range 0 to 2;
  signal pending : std_logic_vector(2 downto 0);
  signal up      : boolean;
begin
  process(clk)
    variable p   : std_logic_vector(2 downto 0);
    variable f   : integer range 0 to 2;
    variable ab  : boolean;   -- request above f
    variable bl  : boolean;   -- request below f
    variable dir : boolean;

    -- Choose the next phase at floor f with merged requests p (see README "decide").
    procedure decide is
    begin
      ab := false;
      bl := false;
      for k in 0 to 2 loop
        if p(k) = '1' and k > f then ab := true; end if;
        if p(k) = '1' and k < f then bl := true; end if;
      end loop;
      if p(f) = '1' then
        phase   <= DOOR_OPEN;
        p(f)    := '0';
      elsif (dir and ab) or (not dir and bl) then
        phase <= MOVE1;
      elsif ab or bl then
        dir   := not dir;
        phase <= MOVE1;
      else
        phase <= IDLE;
      end if;
    end procedure;
  begin
    if rising_edge(clk) then
      if reset = '1' then
        phase   <= IDLE;
        cur     <= 0;
        pending <= "000";
        up      <= true;
      else
        p   := pending or call;
        f   := cur;
        dir := up;
        case phase is
          when IDLE =>
            decide;
          when DOOR_OPEN =>
            p(f)  := '0';
            phase <= IDLE;
          when MOVE1 =>
            phase <= MOVE2;
          when MOVE2 =>
            if dir then f := f + 1; else f := f - 1; end if;
            decide;
        end case;
        pending <= p;
        cur     <= f;
        up      <= dir;
      end if;
    end if;
  end process;

  floor <= std_logic_vector(to_unsigned(cur, 2));
  door  <= '1' when phase = DOOR_OPEN else '0';
end architecture rtl;
