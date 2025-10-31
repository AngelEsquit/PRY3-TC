"""
Operaciones aritméticas auxiliares para las Máquinas de Turing
Estas funciones NO serán ejecutadas por la MT, sino que sirven como 
utilidades para preparar datos o para componentes del sistema que 
no son parte de la MT pura.
"""

def marks_to_number(marks_string):
    """
    Convierte una cadena de marcas a número.
    Ejemplo: "|||" -> 3
    """
    return marks_string.count('|')


def number_to_marks(n):
    """
    Convierte un número a marcas.
    Ejemplo: 3 -> "|||"
    """
    if n <= 0:
        return ""
    return "|" * n


def mod26_marks(marks_string):
    """
    Calcula módulo 26 de un número representado en marcas.
    Ejemplo: "||||||||||||||||||||||||||||||||" (32 marcas) -> "||||||" (6 marcas)
    
    Esta función es auxiliar y NO forma parte de la MT pura.
    Se usa para pruebas y validación.
    """
    count = marks_to_number(marks_string)
    result = count % 26
    return number_to_marks(result)


def letter_to_number(letter):
    """
    Convierte una letra a su posición en el alfabeto (A=0, B=1, ..., Z=25).
    """
    if not letter.isalpha():
        raise ValueError(f"'{letter}' no es una letra válida")
    
    letter = letter.upper()
    return ord(letter) - ord('A')


def number_to_letter(n):
    """
    Convierte un número a su letra correspondiente (0=A, 1=B, ..., 25=Z).
    """
    if not 0 <= n <= 25:
        raise ValueError(f"Número {n} fuera del rango 0-25")
    
    return chr(ord('A') + n)


def caesar_shift(letter, shift):
    """
    Aplica el cifrado César a una letra.
    
    Args:
        letter: Letra a cifrar (A-Z)
        shift: Desplazamiento (puede ser negativo para descifrar)
    
    Returns:
        Letra cifrada
    """
    if not letter.isalpha():
        return letter  # No cifrar caracteres no alfabéticos
    
    is_upper = letter.isupper()
    letter = letter.upper()
    
    # Convertir a número, aplicar shift con módulo 26, convertir a letra
    num = letter_to_number(letter)
    shifted = (num + shift) % 26
    result = number_to_letter(shifted)
    
    return result if is_upper else result.lower()


def caesar_encrypt(text, shift):
    """
    Cifra un texto completo usando César.
    
    Args:
        text: Texto a cifrar
        shift: Desplazamiento (clave)
    
    Returns:
        Texto cifrado
    """
    return ''.join(caesar_shift(char, shift) for char in text)


def caesar_decrypt(text, shift):
    """
    Descifra un texto cifrado con César.
    
    Args:
        text: Texto cifrado
        shift: Desplazamiento (clave)
    
    Returns:
        Texto descifrado
    """
    return caesar_encrypt(text, -shift)


if __name__ == "__main__":
    # Pruebas rápidas
    print("=== Pruebas de Conversión ===")
    print(f"A -> {letter_to_number('A')} -> {number_to_letter(0)}")
    print(f"Z -> {letter_to_number('Z')} -> {number_to_letter(25)}")
    print(f"H -> {letter_to_number('H')} -> {number_to_letter(7)}")
    
    print("\n=== Pruebas de Marcas ===")
    print(f"3 -> {number_to_marks(3)} -> {marks_to_number('|||')}")
    print(f"32 mod 26 = {mod26_marks('|' * 32)}")
    
    print("\n=== Pruebas de Cifrado ===")
    print(f"'HOLA' con shift 3: {caesar_encrypt('HOLA', 3)}")
    print(f"'KROD' con shift -3: {caesar_decrypt('KROD', 3)}")
    print(f"Mensaje completo: '{caesar_encrypt('HELLO WORLD', 3)}'")
