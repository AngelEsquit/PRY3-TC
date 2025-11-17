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
        self.tm_number_key_to_letter = TuringMachine()
        if not self.tm_letter_to_num.load_config(os.path.join(config_dir, 'letter_to_number.json')):
            raise RuntimeError('No se pudo cargar letter_to_number.json')
        if not self.tm_add.load_config(os.path.join(config_dir, 'add_simple.json')):
            raise RuntimeError('No se pudo cargar add_simple.json')
        if not self.tm_mod26.load_config(os.path.join(config_dir, 'mod26_full.json')):
            raise RuntimeError('No se pudo cargar mod26_full.json')
        if not self.tm_num_to_letter.load_config(os.path.join(config_dir, 'number_to_letter.json')):
            raise RuntimeError('No se pudo cargar number_to_letter.json')
        if not self.tm_number_key_to_letter.load_config(os.path.join(config_dir, 'number_key_to_letter.json')):
            raise RuntimeError('No se pudo cargar number_key_to_letter.json')
        # Preconstruir las marcas de shift para compatibilidad con rutas antiguas
        self.shift_marks = '|' * self.shift if self.shift > 0 else ''

    def _key_to_shift_marks(self, raw_key: str) -> str:
        """Convierte clave (número 1..27 o letra A..Z) a marcas '|' usando solo MTs.
        - Si es letra: usa letter_to_number -> marcas.
        - Si es número: numero->letra (MT) y luego letra->marcas (MT).
        Devuelve la secuencia de '|' (puede ser cadena vacía si shift=0).
        """
        if len(raw_key) == 1 and raw_key.isalpha():
            upper = raw_key.upper()
            res = self.tm_letter_to_num.run(upper, max_steps=2000)
            return ''.join(ch for ch in res if ch == '|')
        # numérico: 1..27
        if raw_key.isdigit():
            letter_res = self.tm_number_key_to_letter.run(raw_key, max_steps=2000)
            key_letter = next((c for c in letter_res if c.isalpha()), 'A')
            marks_res = self.tm_letter_to_num.run(key_letter, max_steps=2000)
            return ''.join(ch for ch in marks_res if ch == '|')
        raise ValueError("Clave inválida: debe ser número (1-27) o letra A-Z")

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

    def encrypt_w(self, w: str) -> str:
        """Cifra a partir de w=clave#mensaje sin aritmética en Python.
        Usa MTs para derivar las marcas de la clave.
        """
        if '#' not in w:
            raise ValueError("Formato inválido: falta '#' en w")
        raw_key, message = w.split('#', 1)
        raw_key = raw_key.strip()
        message = message.strip()
        shift_marks = self._key_to_shift_marks(raw_key)
        self.shift_marks = shift_marks  # usar en pipeline existente
        return self.encrypt(message)
