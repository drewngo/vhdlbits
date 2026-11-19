library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    instr : in  std_logic_vector(31 downto 0);
    imm   : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  alias sign : std_logic is instr(31);
begin
  process(all)
  begin
    case instr(6 downto 0) is
      when "0000011" | "0010011" | "1100111" =>                     -- I
        imm <= (31 downto 12 => sign) & instr(31 downto 20);
      when "0100011" =>                                             -- S
        imm <= (31 downto 12 => sign) & instr(31 downto 25) & instr(11 downto 7);
      when "1100011" =>                                             -- B
        imm <= (31 downto 13 => sign) & instr(31) & instr(7) & instr(30 downto 25)
               & instr(11 downto 8) & '0';
      when "0110111" | "0010111" =>                                 -- U
        imm <= instr(31 downto 12) & x"000";
      when "1101111" =>                                             -- J
        imm <= (31 downto 21 => sign) & instr(31) & instr(19 downto 12) & instr(20)
               & instr(30 downto 21) & '0';
      when others =>
        imm <= (others => '0');
    end case;
  end process;
end architecture rtl;
