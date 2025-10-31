"""
Máquina de Turing Compuesta para Cifrado César
Esta clase integra múltiples MTs para realizar el cifrado completo
"""

import os
from turing_machine import TuringMachine
from arithmetic_utils import (
    letter_to_number, number_to_letter, 
    number_to_marks, marks_to_number
)


class CaesarCipherTM:
    """
    Máquina de Turing compuesta para cifrado César.
    
    Proceso:
    1. Letra de entrada -> número (usando MT)
    2. Número + shift -> suma (usando MT)
    3. Resultado -> mod 26 (usando función auxiliar)
    4. Número resultado -> letra (usando MT)
    """
    
    def __init__(self, shift=3, debug=False):
        """
        Inicializa la MT de cifrado César.
        
        Args:
            shift: Desplazamiento del cifrado (clave)
            debug: Si True, muestra información de depuración
        """
        self.shift = shift
        self.debug = debug
        
        # Cargar las MTs componentes
        self.tm_letter_to_num = TuringMachine()
        self.tm_add = TuringMachine()
        self.tm_num_to_letter = TuringMachine()
        
        # Rutas a las configuraciones
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        
        letter_to_num_path = os.path.join(config_dir, 'letter_to_number.json')
        add_path = os.path.join(config_dir, 'add_simple.json')
        num_to_letter_path = os.path.join(config_dir, 'number_to_letter.json')
        
        # Cargar configuraciones
        if not self.tm_letter_to_num.load_config(letter_to_num_path):
            raise Exception("No se pudo cargar letra_to_number.json")
        
        if not self.tm_add.load_config(add_path):
            raise Exception("No se pudo cargar add_simple.json")
        
        if not self.tm_num_to_letter.load_config(num_to_letter_path):
            raise Exception("No se pudo cargar number_to_letter.json")
        
        if self.debug:
            print("✓ MTs componentes cargadas exitosamente")
    
    
    def encrypt_letter(self, letter):
        """
        Cifra una sola letra usando el cifrado César.
        
        Args:
            letter: Letra a cifrar (A-Z)
        
        Returns:
            Letra cifrada
        """
        if not letter.isalpha():
            return letter  # No cifrar caracteres no alfabéticos
        
        original_case = letter.isupper()
        letter = letter.upper()
        
        if self.debug:
            print(f"\n{'='*60}")
            print(f"Cifrando: {letter} con shift {self.shift}")
            print(f"{'='*60}")
        
        # Paso 1: Letra -> Número (usando MT)
        if self.debug:
            print("\n[Paso 1] Letra -> Número")
        
        result = self.tm_letter_to_num.run(letter, max_steps=1000)
        letter_num_marks = result.strip('_')
        letter_num = marks_to_number(letter_num_marks)
        
        if self.debug:
            print(f"  {letter} -> {letter_num_marks} ({letter_num})")
        
        # Paso 2: Número + Shift (usando MT de suma)
        if self.debug:
            print(f"\n[Paso 2] Sumar shift: {letter_num} + {self.shift}")
        
        shift_marks = number_to_marks(self.shift)
        add_input = letter_num_marks + '+' + shift_marks
        
        result = self.tm_add.run(add_input, max_steps=1000)
        sum_marks = result.replace('_', '').replace('+', '')
        sum_num = marks_to_number(sum_marks)
        
        if self.debug:
            print(f"  {add_input} -> {sum_marks} ({sum_num})")
        
        # Paso 3: Módulo 26 (usando función auxiliar)
        if self.debug:
            print(f"\n[Paso 3] Módulo 26: {sum_num} mod 26")
        
        mod_num = sum_num % 26
        mod_marks = number_to_marks(mod_num)
        
        if self.debug:
            print(f"  {sum_num} mod 26 = {mod_num} ({mod_marks})")
        
        # Paso 4: Número -> Letra (usando MT)
        if self.debug:
            print(f"\n[Paso 4] Número -> Letra")
        
        result = self.tm_num_to_letter.run(mod_marks if mod_marks else '_', max_steps=1000)
        # Extraer la letra del resultado
        encrypted_letter = None
        for char in result:
            if char.isalpha():
                encrypted_letter = char
                break
        
        if self.debug:
            print(f"  {mod_marks} ({mod_num}) -> {encrypted_letter}")
            print(f"\n✓ Resultado: {letter} -> {encrypted_letter}")
        
        # Restaurar el caso original
        if encrypted_letter:
            return encrypted_letter if original_case else encrypted_letter.lower()
        return letter
    
    
    def encrypt(self, text):
        """
        Cifra un texto completo.
        
        Args:
            text: Texto a cifrar
        
        Returns:
            Texto cifrado
        """
        result = []
        for i, char in enumerate(text):
            if self.debug:
                print(f"\n>>> Procesando carácter {i+1}/{len(text)}: '{char}'")
            
            encrypted_char = self.encrypt_letter(char)
            result.append(encrypted_char)
        
        return ''.join(result)
    
    
    def decrypt_letter(self, letter):
        """
        Descifra una sola letra usando el cifrado César.
        
        Args:
            letter: Letra a descifrar (A-Z)
        
        Returns:
            Letra descifrada
        """
        if not letter.isalpha():
            return letter
        
        original_case = letter.isupper()
        letter = letter.upper()
        
        if self.debug:
            print(f"\n{'='*60}")
            print(f"Descifrando: {letter} con shift {self.shift}")
            print(f"{'='*60}")
        
        # Paso 1: Letra -> Número
        result = self.tm_letter_to_num.run(letter, max_steps=1000)
        letter_num_marks = result.strip('_')
        letter_num = marks_to_number(letter_num_marks)
        
        if self.debug:
            print(f"  {letter} -> {letter_num}")
        
        # Paso 2: Número - Shift (restar el shift)
        # Para descifrar restamos el shift
        decrypted_num = (letter_num - self.shift) % 26
        decrypted_marks = number_to_marks(decrypted_num)
        
        if self.debug:
            print(f"  {letter_num} - {self.shift} mod 26 = {decrypted_num}")
        
        # Paso 3: Número -> Letra
        result = self.tm_num_to_letter.run(decrypted_marks if decrypted_marks else '_', max_steps=1000)
        decrypted_letter = None
        for char in result:
            if char.isalpha():
                decrypted_letter = char
                break
        
        if self.debug:
            print(f"  {decrypted_num} -> {decrypted_letter}")
        
        if decrypted_letter:
            return decrypted_letter if original_case else decrypted_letter.lower()
        return letter
    
    
    def decrypt(self, text):
        """
        Descifra un texto cifrado.
        
        Args:
            text: Texto cifrado
        
        Returns:
            Texto descifrado
        """
        result = []
        for i, char in enumerate(text):
            if self.debug:
                print(f"\n>>> Procesando carácter {i+1}/{len(text)}: '{char}'")
            
            decrypted_char = self.decrypt_letter(char)
            result.append(decrypted_char)
        
        return ''.join(result)


def main():
    """Programa principal de demostración"""
    print("="*70)
    print(" " * 15 + "CIFRADO CÉSAR CON MÁQUINA DE TURING")
    print("="*70)
    
    # Crear la MT de cifrado con shift=3
    print("\nInicializando Máquina de Turing de Cifrado César...")
    cipher = CaesarCipherTM(shift=3, debug=False)
    print("✓ Inicialización completa\n")
    
    # Pruebas básicas
    print("-"*70)
    print("PRUEBAS BÁSICAS")
    print("-"*70)
    
    test_cases = [
        "A",
        "Z",
        "HOLA",
        "HELLO WORLD",
        "ABC XYZ"
    ]
    
    for text in test_cases:
        encrypted = cipher.encrypt(text)
        decrypted = cipher.decrypt(encrypted)
        
        print(f"\nOriginal:   '{text}'")
        print(f"Cifrado:    '{encrypted}'")
        print(f"Descifrado: '{decrypted}'")
        
        if text.upper() == decrypted.upper():
            print("✓ Cifrado/descifrado correcto")
        else:
            print("✗ Error en cifrado/descifrado")
    
    print("\n" + "="*70)
    print("Pruebas completadas")
    print("="*70)


if __name__ == "__main__":
    main()
