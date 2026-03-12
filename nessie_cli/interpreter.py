class Interpreter:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def interpret(self, commands):
        for command in commands:
            self.execute_command(command)

    def execute_command(self, command):
        if self.verbose:
            print(
                f"Executing command: {command.command}"
                + (f", {command.subcommand}" if command.subcommand else "")
            )
            for arg in command.args:
                print(f" - Argument: {arg}")
                print(f"   - Type: {type(arg).__name__}")
                if arg.__class__.__name__.endswith("Expression"):
                    show_exp(arg)
            for kwarg in command.kwargs:
                print(f" - Keyword Argument: {kwarg.key} = {kwarg.value}")


def show_exp(exp, indent=0):
    print("  " * indent + f"Expression: {type(exp).__name__}")
    print("  " * indent + f"Operator: {getattr(exp, 'op', None)}")
    if hasattr(exp, "left"):
        print("  " * (indent + 1) + "Left:")
        show_exp(exp.left, indent + 2)
    if hasattr(exp, "right"):
        print("  " * (indent + 1) + "Right:")
        if isinstance(exp.right, list):
            for e in exp.right:
                show_exp(e, indent + 2)
        else:
            show_exp(exp.right, indent + 2)
