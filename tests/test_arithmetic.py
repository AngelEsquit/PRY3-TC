"""
Pruebas de Operaciones Aritméticas
Versión simplificada para comenzar

Fecha: 30 de octubre de 2025
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turing_machine import TuringMachine


def test_simple_addition():
    """Prueba suma simple: 2 + 3 = 5"""
    print("=" * 60)
    print("TEST: Suma Simple (2 + 3 = 5)")
    print("=" * 60)
    print("\nNota: Los números se representan como marcas |")
    print("2 = ||, 3 = |||")
    print("Entrada: ||+|||")
    print("Esperado: ||||| (se borra el +)")
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'add_simple.json')
    
    if not tm.load_config(config_path):
        print("✗ No se pudo cargar la configuración")
        return False
    
    tm.enable_debug_mode()
    
    # Entrada: ||+||| (dos marcas + tres marcas)
    input_str = "||+|||"
    print(f"\nEntrada: {input_str}")
    result = tm.run(input_str, max_steps=1000)
    
    # Contar las marcas en el resultado
    mark_count = result.count('|')
    print(f"\nResultado: {result}")
    print(f"Número de marcas: {mark_count}")
    print(f"Esperado: 5 marcas")
    
    if mark_count == 5:
        print("✓ PRUEBA EXITOSA")
        return True
    else:
        print("✗ PRUEBA FALLIDA")
        return False


def test_addition_with_zero():
    """Prueba suma con cero: 3 + 0 = 3"""
    print("\n" + "=" * 60)
    print("TEST: Suma con Cero (3 + 0 = 3)")
    print("=" * 60)
    print("Entrada: |||+ (tres marcas + cero marcas)")
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'add_simple.json')
    
    if not tm.load_config(config_path):
        return False
    
    tm.disable_debug_mode()  # Sin debug para ver resultado directo
    
    input_str = "|||+"
    print(f"Entrada: {input_str}")
    result = tm.run(input_str, max_steps=1000)
    
    mark_count = result.count('|')
    print(f"Resultado: {result}")
    print(f"Número de marcas: {mark_count}")
    print(f"Esperado: 3 marcas")
    
    if mark_count == 3:
        print("✓ PRUEBA EXITOSA")
        return True
    else:
        print("✗ PRUEBA FALLIDA")
        return False


def test_simple_subtraction():
    """Prueba resta simple: 5 - 2 = 3"""
    print("\n" + "=" * 60)
    print("TEST: Resta Simple (5 - 2 = 3)")
    print("=" * 60)
    print("Entrada: |||||-|| (cinco marcas - dos marcas)")
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'subtract_simple.json')
    
    if not tm.load_config(config_path):
        print("✗ No se pudo cargar la configuración")
        return False
    
    tm.enable_debug_mode()
    
    input_str = "|||||-||"
    print(f"Entrada: {input_str}")
    result = tm.run(input_str, max_steps=2000)
    
    mark_count = result.count('|')
    print(f"\nResultado: {result}")
    print(f"Número de marcas: {mark_count}")
    print(f"Esperado: 3 marcas")
    
    if mark_count == 3:
        print("✓ PRUEBA EXITOSA")
        return True
    else:
        print("✗ PRUEBA FALLIDA")
        return False


def test_subtraction_to_zero():
    """Prueba resta a cero: 2 - 2 = 0"""
    print("\n" + "=" * 60)
    print("TEST: Resta a Cero (2 - 2 = 0)")
    print("=" * 60)
    print("Entrada: ||-|| (dos marcas - dos marcas)")
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'subtract_simple.json')
    
    if not tm.load_config(config_path):
        return False
    
    tm.disable_debug_mode()
    
    input_str = "||-||"
    print(f"Entrada: {input_str}")
    result = tm.run(input_str, max_steps=2000)
    
    mark_count = result.count('|')
    print(f"Resultado: {result}")
    print(f"Número de marcas: {mark_count}")
    print(f"Esperado: 0 marcas")
    
    if mark_count == 0:
        print("✓ PRUEBA EXITOSA")
        return True
    else:
        print("✗ PRUEBA FALLIDA")
        return False


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PRUEBAS DE ARITMÉTICA" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝\n")
    
    tests = [
        test_simple_addition,
        test_addition_with_zero,
        test_simple_subtraction,
        test_subtraction_to_zero
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Error en prueba: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")
        print("\nNota: Las operaciones aritméticas son complejas.")
        print("Es normal que tomen varios intentos para funcionar correctamente.")
    
    print("=" * 60)
