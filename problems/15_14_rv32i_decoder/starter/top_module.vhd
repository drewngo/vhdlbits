library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    instr                                                             : in  std_logic_vector(31 downto 0);
    reg_write, alu_src, mem_read, mem_write, mem_to_reg, branch, jump : out std_logic;
    alu_ctrl                                                          : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
