library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    op                                           : in  std_logic_vector(3 downto 0);
    alu_en, wr_reg, mem_rd, mem_wr, branch, halt : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  -- Write your code here
end architecture rtl;
