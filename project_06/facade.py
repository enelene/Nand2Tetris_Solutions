from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Assembler:
    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def __init__(self):
        self.symbol_table = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
            'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
            'SCREEN': 16384, 'KBD': 24576
        }
        self.next_variable_address = 16

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        binary_instructions = []

        # First pass: Build symbol table
        instruction_counter = 0
        for line in assembly:
            line = line.strip()
            if not line or line.startswith('//'):
                continue  # Skip comments and empty lines
            elif line.startswith('('):  # Label definition
                label = line[1:-1]
                self.symbol_table[label] = instruction_counter
            else:
                instruction_counter += 1

        # Second pass: Translate assembly to binary
        for line in assembly:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('('):
                continue  # Skip comments, empty lines, and label definitions
            line = line.replace(" ","")
            comment_start = line.find("//")
            if comment_start != -1:
                line = line[0:comment_start]
            if line.startswith('@'):  # A-instruction
                symbol = line[1:]
                if symbol.isdigit():
                    binary_instruction = format(int(symbol), '016b')
                else:
                    if symbol not in self.symbol_table:
                        self.symbol_table[symbol] = self.next_variable_address
                        self.next_variable_address += 1
                    address = self.symbol_table[symbol]
                    binary_instruction = format(address, '016b')
                binary_instructions.append(binary_instruction)
            else:  # C-instruction
                dest, comp, jump = '', '', ''
                if '=' in line:
                    dest, line = line.split('=')
                if ';' in line:
                    comp, jump = line.split(';')
                else:
                    comp = line
                binary_instruction = '111' + self._comp(comp) + self._dest(dest) + self._jump(jump)
                binary_instructions.append(binary_instruction)

        return binary_instructions

    def _comp(self, mnemonic: str) -> str:
        comp_table = {
            '0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
            'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
            '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
            'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
            'D&A': '0000000', 'D|A': '0010101',
            'M': '1110000', '!M': '1110001', '-M': '1110011',
            'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011',
            'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101'
        }
        return comp_table.get(mnemonic, '0000000')

    def _dest(self, mnemonic: str) -> str:
        dest_table = {'': '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
        return dest_table.get(mnemonic, '000')

    def _jump(self, mnemonic: str) -> str:
        jump_table = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}
        return jump_table.get(mnemonic, '000')

