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
            for kwarg in command.kwargs:
                print(f" - Keyword Argument: {kwarg.key} = {kwarg.value}")
