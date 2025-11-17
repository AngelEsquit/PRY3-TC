"""Máquina de Turing compuesta exclusivamente para ENCRIPTAR (Cifrado César).
Encapsula el pipeline: LETRA -> marcas (MT) -> suma shift (MT) -> módulo 26 (MT) -> marcas -> letra (MT).
"""
import os
from turing_machine import TuringMachine

class CaesarEncryptTM:
    def __init__(self, shift=3, debug=False):
        self.shift = shift % 26
        self.debug = debug
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.tm_letter_to_num = TuringMachine()
        self.tm_add = TuringMachine()
        self.tm_mod26 = TuringMachine()
        self.tm_num_to_letter = TuringMachine()
        if not self.tm_letter_to_num.load_config(os.path.join(config_dir, 'letter_to_number.json')):
            raise RuntimeError('No se pudo cargar letter_to_number.json')
        if not self.tm_add.load_config(os.path.join(config_dir, 'add_simple.json')):
            raise RuntimeError('No se pudo cargar add_simple.json')
        if not self.tm_mod26.load_config(os.path.join(config_dir, 'mod26_full.json')):
            raise RuntimeError('No se pudo cargar mod26_full.json')
        if not self.tm_num_to_letter.load_config(os.path.join(config_dir, 'number_to_letter.json')):
            raise RuntimeError('No se pudo cargar number_to_letter.json')
        # Preconstruir las marcas de shift (permitido como parte de la preparación de entrada)
        self.shift_marks = '|' * self.shift if self.shift > 0 else ''

    def _encrypt_letter(self, letter: str) -> str:
        if not letter.isalpha():
            return letter
        upper = letter.upper()
        # Paso 1: letra -> marcas
        marks_result = self.tm_letter_to_num.run(upper, max_steps=2000)
        letter_marks = ''.join(ch for ch in marks_result if ch == '|')
        # Paso 2: suma marcas + shift_marks
        add_input = f"{letter_marks}+{self.shift_marks}" if self.shift_marks else f"{letter_marks}+"
        add_result = self.tm_add.run(add_input, max_steps=2000)
        sum_marks = ''.join(ch for ch in add_result if ch == '|')
        # Paso 3: módulo 26
        mod_result = self.tm_mod26.run(sum_marks if sum_marks else '_', max_steps=8000)
        mod_marks = ''.join(ch for ch in mod_result if ch == '|')
        # Paso 4: marcas -> letra
        back_result = self.tm_num_to_letter.run(mod_marks if mod_marks else '_', max_steps=2000)
        # Extraer letra
        out_letter = next((c for c in back_result if c.isalpha()), upper)
        return out_letter if letter.isupper() else out_letter.lower()

    def encrypt(self, text: str) -> str:
        return ''.join(self._encrypt_letter(c) for c in text)
