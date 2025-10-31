"""
Programa principal para el Cifrado César con Máquina de Turing
Interfaz de línea de comandos (CLI)
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from caesar_cipher_tm import CaesarCipherTM


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
        shift = int(input("Ingrese la clave (shift, 1-25): "))
        if not 1 <= shift <= 25:
            print("⚠️  La clave debe estar entre 1 y 25")
            return
    except ValueError:
        print("⚠️  Clave inválida")
        return
    
    print(f"\nProcesando con shift={shift}...")
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

AUTOR: Proyecto de Teoría de la Computación
FECHA:  Octubre 2025
    """)
    print("="*70)


def main():
    """Función principal"""
    print_banner()
    
    # Solicitar la clave inicial
    print("\nBienvenido al Cifrador César con Máquina de Turing")
    
    try:
        shift = int(input("\nIngrese la clave predeterminada (shift, 1-25, default=3): ") or "3")
        if not 1 <= shift <= 25:
            print("⚠️  Usando clave predeterminada: 3")
            shift = 3
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
            choice = input("\nSeleccione una opción (1-5): ").strip()
            
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
