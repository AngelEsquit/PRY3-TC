"""CLI mínimo para ejecutar el simulador universal de Turing.

Uso:
    python main.py --config config/test_simple.json --input AAA
"""
import sys
import os
import argparse

SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from turing_simulator import TuringMachine  # type: ignore


def parse_args():
    parser = argparse.ArgumentParser(description="Ejecutor universal de MT (una cinta)")
    parser.add_argument("--config", required=True, help="Ruta al archivo JSON de la máquina")
    parser.add_argument("--input", default="", help="Cadena de entrada para la cinta")
    parser.add_argument("--max-steps", type=int, default=10000, help="Máximo de pasos antes de detener")
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.path.isfile(args.config):
        print(f"No existe el archivo JSON: {args.config}")
        sys.exit(1)

    tm = TuringMachine(args.config)
    output = tm.run(args.input, max_steps=args.max_steps)
    print("Estado final:", tm.current_state)
    print("Pasos ejecutados:", tm.steps_executed)
    print("Salida cinta:", output)


if __name__ == "__main__":
    main()
