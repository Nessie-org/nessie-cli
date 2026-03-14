from multiprocessing import context
from textx import metamodel_for_file
from nessie_cli.interpreter import Interpreter


def main():
    # Load the grammar and create the meta-model
    meta = metamodel_for_file("*.nss")

    # Parse a command
    with open("tests/test_files/test_file.nss") as f:
        interpreter = Interpreter(None)
        interpreter.interpret(f.readlines())


if __name__ == "__main__":
    main()
