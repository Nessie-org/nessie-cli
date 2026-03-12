from nessie_api.models.plugin import Action

from nessie_cli.evaluator import Evaluator


class Interpreter:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def interpret(self, commands):
        for command in commands:
            self.execute_command(command)

    def execute_command(self, command):
        if self.verbose:
            self._show_command(command)

        handler_name = (
            f"_execute_{command.command}_{command.subcommand}"
            if command.subcommand
            else f"_execute_{command.command}"
        )

        handler = getattr(self, handler_name, None)
        if handler:
            handler(command)
        else:
            raise NotImplementedError(
                f"No handler for command: {command.command}"
                + (f", subcommand: {command.subcommand}" if command.subcommand else "")
            )

    def _execute_create_node(self, command):

        try:
            id = command.kwargs.get("id")
            properties = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key != "property"
            }
            # TODO: Have an actual Action API
            toSend = Action("SomeName", {"id": id, "properties": properties})
        except Exception as e:
            print(f"Error executing create node command: {e}")

    def _execute_create_edge(self, command):
        try:
            id = command.kwargs.get("id")
            properties = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key != "property"
            }
            # TODO: Have an actual Action API
            toSend = Action("SomeName", {"id": id, "properties": properties})
        except Exception as e:
            print(f"Error executing create edge command: {e}")

    def _execute_filter(self, command):

        try:
            exp = command.args[0]
            ev = Evaluator(exp)

            # TODO: Have an actual Action API
            toSend = Action("SomeName", {"evaluator": ev})
        except Exception as e:
            print(f"Error executing filter command: {e}")

    def _execute_search(self, command):
        try:
            exp = command.args[0]
            # TODO: Have an actual Action API
            toSend = Action("SomeName", {"expression": exp})
        except Exception as e:
            print(f"Error executing search command: {e}")

    def _execute_edit_node(self, command):
        try:
            id = command.kwargs.get("id")
            properties = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key != "property"
            }
            # TODO: Have an actual Action API
            toSend = Action("SomeName", {"id": id, "properties": properties})
        except Exception as e:
            print(f"Error executing edit node command: {e}")

    def _show_command(self, command):
        print(
            f"Executing command: {command.command}"
            + (f", {command.subcommand}" if command.subcommand else "")
        )
        for arg in command.args:
            print(f" - Argument: {arg}")
            print(f"   - Type: {type(arg).__name__}")
            if arg.__class__.__name__.endswith("Expression"):
                self._show_exp(arg)
        for kwarg in command.kwargs:
            print(f" - Keyword Argument: {kwarg.key} = {kwarg.value}")

    def _show_exp(self, exp, indent=0):
        print("  " * indent + f"Expression: {type(exp).__name__}")
        if isinstance(exp, (int, float, str)):
            print("  " * indent + f"Value: {exp}")
            return
        op = getattr(exp, "op", None)
        if op:
            print("  " * indent + f"Operator: {op}")
        if hasattr(exp, "left"):
            print("  " * (indent + 1) + "Left:")
            self._show_exp(exp.left, indent + 2)
        if hasattr(exp, "right"):
            print("  " * (indent + 1) + "Right:")
            if isinstance(exp.right, list):
                for e in exp.right:
                    self._show_exp(e, indent + 2)
            else:
                self._show_exp(exp.right, indent + 2)
        if hasattr(exp, "name"):
            print("  " * indent + f"Variable Name: {exp.name}")
