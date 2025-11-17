"""
Programa principal para el Cifrado César con Máquina de Turing
Interfaz de línea de comandos (CLI)
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from caesar_cipher_tm import CaesarCipherTM


def parse_w(w: str):
    """Parsea una cadena w en formato clave#mensaje.

    Formatos soportados:
    - k#MENSAJE  (k numérico 1-27; internamente k mod 26)
    - L#MENSAJE  (L letra A-Z donde shift = posición A=0, B=1, ... Z=25)

    Retorna (shift:int, mensaje:str).
    Lanza ValueError si el formato es inválido.
    """
    if '#' not in w:
        raise ValueError("Formato inválido: falta separador '#' (ej: 3#TEXTO o D#TEXTO)")
    raw_key, message = w.split('#', 1)
    raw_key = raw_key.strip()
    message = message.strip()
    if not message:
        raise ValueError("Mensaje vacío tras la clave")
    # Intentar numérico
    if raw_key.isdigit():
        shift_val = int(raw_key)
        if not 1 <= shift_val <= 27:
            raise ValueError("Shift numérico fuera de rango (1-27)")
        internal_shift = shift_val % 26  # 26->0, 27->1
        return internal_shift, message
    # Intentar letra
    if len(raw_key) == 1 and raw_key.isalpha():
        # A=0, B=1, ..., Z=25. Si el enunciado permite 1..27 habría que ajustar.
        shift = (ord(raw_key.upper()) - ord('A'))
        if shift == 0:
            # Caso A produce desplazamiento 0: permitir pero avisar si se quiere entre 1-25.
            # Mantendremos A=0 para consistencia con tu implementación interna.
            pass
        if shift < 0 or shift > 25:
            raise ValueError("Letra fuera de rango para shift")
        return shift, message
    raise ValueError("Clave inválida: debe ser número (1-27) o letra A-Z")


def print_banner():
    """Imprime el banner del programa"""
    print("\n" + "="*70)
    print(" "*15 + "CIFRADO CÉSAR - MÁQUINA DE TURING")
    print("="*70)


def print_menu():
    """Imprime el menú principal"""
    print("\n" + "-"*70)
    print("OPCIONES:")
    print("-"*70)
    print("1. Cifrar texto")
    print("2. Descifrar texto")
    print("3. Modo interactivo (pruebas rápidas)")
    print("4. Acerca de")
    print("5. Salir")
    print("6. Cifrar desde w (clave#mensaje)")
    print("7. Descifrar desde w (clave#mensaje)")
    print("-"*70)


def encrypt_mode(cipher):
    """Modo de cifrado"""
    print("\n" + "="*70)
    print("MODO CIFRADO")
    print("="*70)
    
    text = input("\nIngrese el texto a cifrar: ")
    
    if not text:
        print("⚠️  Texto vacío")
        return
    
    print("\nCifrando... (esto puede tomar un momento)")
    encrypted = cipher.encrypt(text)
    
    print("\n" + "-"*70)
    print(f"Texto original: {text}")
    print(f"Texto cifrado:  {encrypted}")
    print(f"Clave (shift):  {cipher.shift}")
    print("-"*70)


def decrypt_mode(cipher):
    """Modo de descifrado"""
    print("\n" + "="*70)
    print("MODO DESCIFRADO")
    print("="*70)
    
    text = input("\nIngrese el texto a descifrar: ")
    
    if not text:
        print("⚠️  Texto vacío")
        return
    
    print("\nDescifrando... (esto puede tomar un momento)")
    decrypted = cipher.decrypt(text)
    
    print("\n" + "-"*70)
    print(f"Texto cifrado:    {text}")
    print(f"Texto descifrado: {decrypted}")
    print(f"Clave (shift):    {cipher.shift}")
    print("-"*70)


def interactive_mode():
    """Modo interactivo para pruebas"""
    print("\n" + "="*70)
    print("MODO INTERACTIVO")
    print("="*70)
    
    print("\nEste modo permite probar el cifrado con diferentes claves.")
    print("Ejemplos de textos: 'HOLA', 'HELLO WORLD', 'ABC XYZ'")
    
    text = input("\nIngrese el texto: ")
    
    if not text:
        print("⚠️  Texto vacío")
        return
    
    try:
        raw_shift = int(input("Ingrese la clave (shift, 1-27): "))
        if not 1 <= raw_shift <= 27:
            print("⚠️  La clave debe estar entre 1 y 27")
            return
        shift = raw_shift % 26
    except ValueError:
        print("⚠️  Clave inválida")
        return

    print(f"\nProcesando con shift={shift} (clave ingresada={raw_shift})...")
    cipher = CaesarCipherTM(shift=shift, debug=False)
    
    encrypted = cipher.encrypt(text)
    decrypted = cipher.decrypt(encrypted)
    
    print("\n" + "-"*70)
    print(f"Original:         {text}")
    print(f"Cifrado:          {encrypted}")
    print(f"Descifrado:       {decrypted}")
    print(f"Verificación:     {'✓ OK' if text.upper() == decrypted.upper() else '✗ Error'}")
    print("-"*70)


def about():
    """Información sobre el programa"""
    print("\n" + "="*70)
    print("ACERCA DE")
    print("="*70)
    print("""
Este programa implementa el Cifrado César usando Máquinas de Turing.

COMPONENTES:
- Máquina de Turing base (turing_machine.py)
- Conversión Letra ↔ Número
- Operaciones aritméticas (suma, resta)
- Cifrado/descifrado César

ALGORITMO:
1. Convertir letra a número (A=0, B=1, ..., Z=25)
2. Sumar la clave (shift)
3. Aplicar módulo 26
4. Convertir número a letra

CARACTERÍSTICAS:
- Implementación pura con Máquinas de Turing
- Soporta mayúsculas y minúsculas
- Preserva espacios y caracteres especiales
- Configuraciones en JSON
- Formato de entrada 'w' soportado: clave#mensaje
  Ejemplos:
    3#ROMA NO FUE CONSTRUIDA EN UN DIA.
    26#ROMA NO FUE CONSTRUIDA EN UN DIA. (equivale a desplazamiento 0)
    27#ROMA NO FUE CONSTRUIDA EN UN DIA. (equivale a desplazamiento 1)
    D#ROMA NO FUE CONSTRUIDA EN UN DIA.
  Donde la clave puede ser:
    - Número 1-27 (desplazamiento aplicado como k mod 26)
    - Letra A-Z (A=0, B=1, ..., Z=25)

AUTOR: Proyecto de Teoría de la Computación
FECHA:  Octubre 2025
    """)
    print("="*70)


def encrypt_w():
    """Cifra usando una sola cadena w=clave#mensaje"""
    print("\n" + "="*70)
    print("CIFRADO DESDE w")
    print("="*70)
    w = input("Ingrese w (clave#mensaje): ").strip()
    if not w:
        print("⚠️  Entrada vacía")
        return
    try:
        shift, message = parse_w(w)
    except ValueError as e:
        print(f"⚠️  {e}")
        return
    cipher_local = CaesarCipherTM(shift=shift, debug=False)
    print("Procesando...")
    encrypted = cipher_local.encrypt(message)
    print("\n" + "-"*70)
    print(f"Clave (shift): {shift}")
    print(f"Mensaje original: {message}")
    print(f"Mensaje cifrado : {encrypted}")
    print("-"*70)


def decrypt_w():
    """Descifra usando una sola cadena w=clave#mensaje"""
    print("\n" + "="*70)
    print("DESCIFRADO DESDE w")
    print("="*70)
    w = input("Ingrese w cifrado (clave#mensaje_cifrado): ").strip()
    if not w:
        print("⚠️  Entrada vacía")
        return
    try:
        shift, message = parse_w(w)
    except ValueError as e:
        print(f"⚠️  {e}")
        return
    cipher_local = CaesarCipherTM(shift=shift, debug=False)
    print("Procesando...")
    decrypted = cipher_local.decrypt(message)
    print("\n" + "-"*70)
    print(f"Clave (shift): {shift}")
    print(f"Mensaje cifrado   : {message}")
    print(f"Mensaje descifrado : {decrypted}")
    print("-"*70)


def main():
    """Función principal"""
    print_banner()
    
    # Solicitar la clave inicial
    print("\nBienvenido al Cifrador César con Máquina de Turing")
    
    try:
        raw_shift = int(input("\nIngrese la clave predeterminada (shift, 1-27, default=3): ") or "3")
        if not 1 <= raw_shift <= 27:
            print("⚠️  Usando clave predeterminada: 3")
            raw_shift = 3
        shift = raw_shift % 26
    except ValueError:
        print("⚠️  Usando clave predeterminada: 3")
        shift = 3
    
    print(f"\nInicializando con shift={shift}...")
    cipher = CaesarCipherTM(shift=shift, debug=False)
    print("✓ Inicialización completa")
    
    # Bucle principal
    while True:
        print_menu()
        
        try:
            choice = input("\nSeleccione una opción (1-7): ").strip()
            
            if choice == '1':
                encrypt_mode(cipher)
            elif choice == '2':
                decrypt_mode(cipher)
            elif choice == '3':
                interactive_mode()
            elif choice == '4':
                about()
            elif choice == '5':
                print("\n¡Hasta luego!")
                break
            elif choice == '6':
                encrypt_w()
            elif choice == '7':
                decrypt_w()
            else:
                print("\n⚠️  Opción inválida. Intente de nuevo.")
        
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
