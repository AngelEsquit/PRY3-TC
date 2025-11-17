"""
Script de prueba para la clase base TuringMachine
Verifica que la implementación básica funciona correctamente

Fecha: 30 de octubre de 2025
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turing_machine import TuringMachine


def test_basic_functionality():
    """Prueba la funcionalidad básica de la clase TuringMachine"""
    print("=" * 60)
    print("TEST 1: Funcionalidad Básica de la Clase")
    print("=" * 60)
    
    # Crear instancia
    tm = TuringMachine()
    print("✓ Instancia creada correctamente")
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_simple.json')
    assert tm.load_config(config_path), "No se pudo cargar la configuración"
    
    # Mostrar configuración
    tm.display_configuration()


def test_simple_execution():
    """Prueba una ejecución simple: convertir AAA a BBB"""
    print("\n" + "=" * 60)
    print("TEST 2: Ejecución Simple (AAA → BBB)")
    print("=" * 60)
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_simple.json')
    tm.load_config(config_path)
    
    # Activar modo debug para ver los pasos
    tm.enable_debug_mode()
    
    # Ejecutar
    input_str = "AAA"
    result = tm.run(input_str)
    
    print(f"\nEntrada:  '{input_str}'")
    print(f"Salida:   '{result}'")
    print(f"Esperado: 'BBB'")
    
    assert result == "BBB", f"Salida inesperada: {result} (esperado 'BBB')"


def test_mixed_input():
    """Prueba con entrada mixta: AABAA → BBBBB"""
    print("\n" + "=" * 60)
    print("TEST 3: Entrada Mixta (AABAA → BBBBB)")
    print("=" * 60)
    
    tm = TuringMachine()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_simple.json')
    tm.load_config(config_path)
    
    # Sin debug para ver resultado directo
    tm.disable_debug_mode()
    
    # Ejecutar
    input_str = "AABAA"
    result = tm.run(input_str)
    
    print(f"Entrada:  '{input_str}'")
    print(f"Salida:   '{result}'")
    print(f"Esperado: 'BBBBB'")
    
    assert result == "BBBBB", f"Salida inesperada: {result} (esperado 'BBBBB')"


def test_manual_configuration():
    """Prueba creando una MT manualmente sin JSON"""
    print("\n" + "=" * 60)
    print("TEST 4: Configuración Manual (sin JSON)")
    print("=" * 60)
    
    # Crear MT manualmente
    tm = TuringMachine(
        states=["q0", "q_accept"],
        input_alphabet=["X"],
        tape_alphabet=["X", "Y", "_"],
        initial_state="q0",
        accept_states=["q_accept"],
        blank_symbol="_",
        transitions=[
            {
                "current_state": "q0",
                "read_symbol": "X",
                "next_state": "q0",
                "write_symbol": "Y",
                "move": "R"
            },
            {
                "current_state": "q0",
                "read_symbol": "_",
                "next_state": "q_accept",
                "write_symbol": "_",
                "move": "N"
            }
        ]
    )
    
    print("✓ MT creada manualmente")
    
    # Ejecutar: XXX → YYY
    input_str = "XXX"
    result = tm.run(input_str)
    
    print(f"Entrada:  '{input_str}'")
    print(f"Salida:   '{result}'")
    print(f"Esperado: 'YYY'")
    
    assert result == "YYY", f"Salida inesperada: {result} (esperado 'YYY')"


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "PRUEBAS DE LA CLASE TURINGMACHINE" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝\n")
    
    tests = [
        test_basic_functionality,
        test_simple_execution,
        test_mixed_input,
        test_manual_configuration
    ]
    
    results = []
    for test in tests:
        try:
            test()
            results.append(True)
        except AssertionError as e:
            print(f"✗ Falló la prueba: {e}")
            results.append(False)
        except Exception as e:
            print(f"✗ Error en prueba: {e}")
            results.append(False)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Pruebas exitosas: {passed}/{total}")

    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! ✓")
        print("La clase base TuringMachine está funcionando correctamente.")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")

    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
