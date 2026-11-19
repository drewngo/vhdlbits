library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    instr    : in  std_logic_vector(31 downto 0);
    opcode   : out std_logic_vector(6 downto 0);
    rd, rs1  : out std_logic_vector(4 downto 0);
    funct3   : out std_logic_vector(2 downto 0);
    imm      : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  opcode <= instr(6 downto 0);
  rd     <= instr(11 downto 7);
  funct3 <= instr(14 downto 12);
  rs1    <= instr(19 downto 15);
  imm    <= (19 downto 0 => instr(31)) & instr(31 downto 20);
end architecture rtl;
