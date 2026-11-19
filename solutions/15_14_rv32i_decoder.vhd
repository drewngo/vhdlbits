library ieee;
use ieee.std_logic_1164.all;

entity top_module is
  port (
    instr                                                         : in  std_logic_vector(31 downto 0);
    reg_write, alu_src, mem_read, mem_write, mem_to_reg, branch, jump : out std_logic;
    alu_ctrl                                                      : out std_logic_vector(3 downto 0)
  );
end entity top_module;

architecture rtl of top_module is
  alias opcode   : std_logic_vector(6 downto 0) is instr(6 downto 0);
  alias funct3   : std_logic_vector(2 downto 0) is instr(14 downto 12);
  alias funct7_5 : std_logic is instr(30);
begin
  process(all)
  begin
    reg_write  <= '0';
    alu_src    <= '0';
    mem_read   <= '0';
    mem_write  <= '0';
    mem_to_reg <= '0';
    branch     <= '0';
    jump       <= '0';
    alu_ctrl   <= "0000";
    case opcode is
      when "0110011" =>                       -- R-type
        reg_write <= '1';
        alu_ctrl  <= funct7_5 & funct3;
      when "0010011" =>                       -- op-imm
        reg_write <= '1';
        alu_src   <= '1';
        if funct3 = "101" then
          alu_ctrl <= funct7_5 & funct3;
        else
          alu_ctrl <= '0' & funct3;
        end if;
      when "0000011" =>                       -- load
        reg_write  <= '1';
        alu_src    <= '1';
        mem_read   <= '1';
        mem_to_reg <= '1';
      when "0100011" =>                       -- store
        alu_src   <= '1';
        mem_write <= '1';
      when "1100011" =>                       -- branch
        branch   <= '1';
        alu_ctrl <= "1000";
      when "1101111" =>                       -- jal
        reg_write <= '1';
        jump      <= '1';
      when "1100111" =>                       -- jalr
        reg_write <= '1';
        alu_src   <= '1';
        jump      <= '1';
      when "0110111" | "0010111" =>           -- lui, auipc
        reg_write <= '1';
        alu_src   <= '1';
      when others =>
        null;
    end case;
  end process;
end architecture rtl;
