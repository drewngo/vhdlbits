library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    funct7       : in  std_logic_vector(6 downto 0);
    rs2, rs1, rd : in  std_logic_vector(4 downto 0);
    funct3       : in  std_logic_vector(2 downto 0);
    opcode       : in  std_logic_vector(6 downto 0);
    instr        : out std_logic_vector(31 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
