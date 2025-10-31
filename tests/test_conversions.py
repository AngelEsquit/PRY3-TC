"""
Pruebas para las conversiones Letra ↔ Número
"""

import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turing_machine import TuringMachine


def test_letter_to_number():
    """Prueba conversión de letras a números (marcas)"""
    print("\n" + "=" * 60)
    print("TEST: Conversión Letra -> Número")
    print("=" * 60)
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'letter_to_number.json')
    
    if not tm.load_config(config_path):
        print("✗ No se pudo cargar la configuración")
        return False
    
    test_cases = [
        ('A', 0, "A = posición 0"),
        ('B', 1, "B = posición 1"),
        ('C', 2, "C = posición 2"),
        ('H', 7, "H = posición 7"),
        ('Z', 25, "Z = posición 25")
    ]
    
    results = []
    for letter, expected, description in test_cases:
        print(f"\n{description}")
        print(f"Entrada: {letter}")
        
        result = tm.run(letter, max_steps=500)
        mark_count = result.count('|')
        
        print(f"Resultado: {result}")
        print(f"Marcas: {mark_count}, Esperado: {expected}")
        
        if mark_count == expected:
            print("✓ CORRECTO")
            results.append(True)
        else:
            print("✗ INCORRECTO")
            results.append(False)
    
    return all(results)


def test_number_to_letter():
    """Prueba conversión de números (marcas) a letras"""
    print("\n" + "=" * 60)
    print("TEST: Conversión Número -> Letra")
    print("=" * 60)
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'number_to_letter.json')
    
    if not tm.load_config(config_path):
        print("✗ No se pudo cargar la configuración")
        return False
    
    test_cases = [
        ('', 'A', "0 marcas = A"),
        ('|', 'B', "1 marca = B"),
        ('||', 'C', "2 marcas = C"),
        ('|||||||', 'H', "7 marcas = H"),
        ('|' * 25, 'Z', "25 marcas = Z")
    ]
    
    results = []
    for marks, expected, description in test_cases:
        print(f"\n{description}")
        print(f"Entrada: '{marks}' ({len(marks)} marcas)")
        
        result = tm.run(marks if marks else "_", max_steps=500)
        # Extraer la letra del resultado
        letter_found = None
        for char in result:
            if char.isalpha():
                letter_found = char
                break
        
        print(f"Resultado: {result}")
        print(f"Letra encontrada: {letter_found}, Esperado: {expected}")
        
        if letter_found == expected:
            print("✓ CORRECTO")
            results.append(True)
        else:
            print("✗ INCORRECTO")
            results.append(False)
    
    return all(results)


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "PRUEBAS DE CONVERSIÓN" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    results.append(test_letter_to_number())
    results.append(test_number_to_letter())
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Grupos de pruebas exitosos: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS CONVERSIONES FUNCIONAN!")
    else:
        print(f"\n⚠️  {total - passed} grupo(s) fallaron")
    
    print("=" * 60)
