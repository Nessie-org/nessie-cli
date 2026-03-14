from multiprocessing import context
from textx import metamodel_for_file
from nessie_cli.interpreter import Interpreter


def main():
    # Load the grammar and create the meta-model
    meta = metamodel_for_file("*.nss")

    # Parse a command
    file = meta.model_from_file("tests/test_files/test_file.nss")

    interpreter = Interpreter(None)
    interpreter.interpret(file.commands)


if __name__ == "__main__":
    main()
