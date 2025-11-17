"""Máquina de Turing compuesta exclusivamente para DECRIPTAR (Cifrado César inverso).
Usa el enfoque: (letter_num - shift) mod 26 = (letter_num + (26 - shift)) mod 26 mediante MTs.
"""
import os
from turing_machine import TuringMachine

class CaesarDecryptTM:
    def __init__(self, shift=3, debug=False):
        self.shift = shift % 26
        self.inverse_shift = (26 - self.shift) % 26
        self.debug = debug
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        self.tm_letter_to_num = TuringMachine()
        self.tm_add = TuringMachine()
        self.tm_mod26 = TuringMachine()
        self.tm_num_to_letter = TuringMachine()
        self.tm_number_key_to_letter = TuringMachine()
        self.tm_subtract = TuringMachine()
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
        if not self.tm_subtract.load_config(os.path.join(config_dir, 'subtract_simple.json')):
            raise RuntimeError('No se pudo cargar subtract_simple.json')
        self.inverse_shift_marks = '|' * self.inverse_shift if self.inverse_shift > 0 else ''

    def _key_to_shift_marks(self, raw_key: str) -> str:
        """Como en cifrado: convierte clave a marcas solo con MTs."""
        if len(raw_key) == 1 and raw_key.isalpha():
            upper = raw_key.upper()
            res = self.tm_letter_to_num.run(upper, max_steps=2000)
            return ''.join(ch for ch in res if ch == '|')
        if raw_key.isdigit():
            letter_res = self.tm_number_key_to_letter.run(raw_key, max_steps=2000)
            key_letter = next((c for c in letter_res if c.isalpha()), 'A')
            marks_res = self.tm_letter_to_num.run(key_letter, max_steps=2000)
            return ''.join(ch for ch in marks_res if ch == '|')
        raise ValueError("Clave inválida: debe ser número (1-27) o letra A-Z")

    def _inverse_marks_from_key(self, raw_key: str) -> str:
        """Obtiene (26 - k) mod 26 marcas usando solo MTs: 26|-|k -> resta -> marcas."""
        key_marks = self._key_to_shift_marks(raw_key)
        base_26 = '||||||||||||||||||||||||||'  # 26 marcas constante
        if not key_marks:
            return ''
        subtract_input = f"{base_26}-{key_marks}"
        res = self.tm_subtract.run(subtract_input, max_steps=5000)
        return ''.join(ch for ch in res if ch == '|')

    def _decrypt_letter(self, letter: str) -> str:
        if not letter.isalpha():
            return letter
        upper = letter.upper()
        # Paso 1: letra -> marcas
        marks_result = self.tm_letter_to_num.run(upper, max_steps=2000)
        letter_marks = ''.join(ch for ch in marks_result if ch == '|')
        # Paso 2: suma con inverse shift
        add_input = f"{letter_marks}+{self.inverse_shift_marks}" if self.inverse_shift_marks else f"{letter_marks}+"
        add_result = self.tm_add.run(add_input, max_steps=2000)
        sum_marks = ''.join(ch for ch in add_result if ch == '|')
        # Paso 3: módulo 26
        mod_result = self.tm_mod26.run(sum_marks if sum_marks else '_', max_steps=8000)
        mod_marks = ''.join(ch for ch in mod_result if ch == '|')
        # Paso 4: marcas -> letra
        back_result = self.tm_num_to_letter.run(mod_marks if mod_marks else '_', max_steps=2000)
        out_letter = next((c for c in back_result if c.isalpha()), upper)
        return out_letter if letter.isupper() else out_letter.lower()

    def decrypt(self, text: str) -> str:
        return ''.join(self._decrypt_letter(c) for c in text)

    def decrypt_w(self, w: str) -> str:
        """Descifra a partir de w=clave#mensaje usando solo MTs para clave.
        Usa RESTA para obtener el desplazamiento inverso.
        """
        if '#' not in w:
            raise ValueError("Formato inválido: falta '#' en w")
        raw_key, message = w.split('#', 1)
        raw_key = raw_key.strip()
        message = message.strip()
        inv_marks = self._inverse_marks_from_key(raw_key)
        self.inverse_shift_marks = inv_marks
        return self.decrypt(message)
