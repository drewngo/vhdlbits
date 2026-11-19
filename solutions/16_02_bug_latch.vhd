library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    op                                         : in  std_logic_vector(3 downto 0);
    alu_en, wr_reg, mem_rd, mem_wr, branch, halt : out std_logic
  );
end entity top_module;

architecture rtl of top_module is
begin
  process(all)
  begin
    alu_en <= '0';
    wr_reg <= '0';
    mem_rd <= '0';
    mem_wr <= '0';
    branch <= '0';
    halt   <= '0';
    case op is
      when "0001" => alu_en <= '1';
      when "0010" => alu_en <= '1'; wr_reg <= '1';
      when "0100" => mem_rd <= '1'; wr_reg <= '1';
      when "0101" => mem_wr <= '1';
      when "1000" => branch <= '1';
      when "1111" => halt   <= '1';
      when others => null;
    end case;
  end process;
end architecture rtl;
