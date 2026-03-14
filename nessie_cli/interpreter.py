from nessie_api.models.plugin import Action
from nessie_api.protocols import Context
from nessie_api.models import Node, Edge, Graph

from nessie_cli.evaluator import Evaluator


class MalformedCommandError(Exception):
    pass


class Interpreter:
    def __init__(self, context: Context, verbose=False):
        self.context = context
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
                k.value[0]: k.value[1] for k in command.kwargs if k.key == "property"
            }
            idx = self.context.get_active_workspace_index()
            attributes = {k: Node.Attribute(k, v) for k, v in properties.items()}
            self.context.get_full_graph_at(idx).add_node(
                Node(id=id, attributes=attributes)
            )

            self._refresh_graph()
        except Exception as e:
            print(f"Error executing create node command: {e}")

    def _execute_create_edge(self, command):
        try:
            id = command.kwargs.get("id")
            source = command.args[0]
            target = command.args[1]
            properties = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key == "property"
            }
            idx = self.context.get_active_workspace_index()
            attributes = {k: Edge.Attribute(k, v) for k, v in properties.items()}
            self.context.get_full_graph_at(idx).add_edge(
                Edge(id=id, source=source, target=target, attributes=attributes)
            )

            self._refresh_graph()
        except Exception as e:
            print(f"Error executing create edge command: {e}")

    def _execute_edit_node(self, command):
        try:
            id = command.kwargs.get("id")
            changed = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key == "ch-prop"
            }
            to_del = [k.value for k in command.kwargs if k.key == "del-prop"]
            to_change = [Node.Attribute(k, v) for k, v in changed.items()]

            idx = self.context.get_active_workspace_index()
            node = self.context.get_full_graph_at(idx).get_node(id)

            for a in to_change:
                node.add_attribute(a)
            for a in to_del:
                node.remove_attribute(a)

            self._refresh_graph()
        except Exception as e:
            print(f"Error executing edit node command: {e}")

    def _execute_edit_edge(self, command):
        try:
            id = command.kwargs.get("id")
            changed = {
                k.value[0]: k.value[1] for k in command.kwargs if k.key == "ch-prop"
            }
            to_del = [k.value for k in command.kwargs if k.key == "del-prop"]
            to_change = [Edge.Attribute(k, v) for k, v in changed.items()]

            idx = self.context.get_active_workspace_index()
            edge = self.context.get_full_graph_at(idx).get_edge(id)

            for a in to_change:
                edge.add_attribute(a)
            for a in to_del:
                edge.remove_attribute(a)

            self._refresh_graph()
        except Exception as e:
            print(f"Error executing edit edge command: {e}")

    def _execute_delete_node(self, command):
        try:
            id = command.kwargs.get("id")
            idx = self.context.get_active_workspace_index()
            self.context.get_full_graph_at(idx).remove_node(id)
            self._refresh_graph()
        except (ValueError, KeyError) as e:
            raise e
        except Exception as e:
            print(f"Error executing delete node command: {e}")

    def _execute_delete_edge(self, command):
        try:
            id = command.kwargs.get("id")
            idx = self.context.get_active_workspace_index()
            self.context.get_full_graph_at(idx).remove_edge(id)
            self._refresh_graph()
        except Exception as e:
            print(f"Error executing delete edge command: {e}")

    def _execute_drop_graph(self, command):
        try:

            idx = self.context.get_active_workspace_index()
            old_graph = self.context.get_full_graph_at(idx)
            empty_graph = Graph(name=old_graph.name, graph_type=old_graph.graph_type)
            self.context.set_full_graph_at(idx, empty_graph)
            self.context.set_graph_at(idx, empty_graph)
        except Exception as e:
            print(f"Error executing drop graph command: {e}")

    def _execute_filter(self, command):

        try:
            exp = command.args[0]
            if self.verbose:
                print("Variables requested by expression:", ev.variables)
                print("Context for evaluation:")

            filters = ev.simple_evaluate()

            if self.verbose:
                print(f"Evaluation result: {filters}")

            self.context.perform_action(Action("clear_filters", None))
            for fltr in filters:
                self.context.perform_action(Action("add_filter", {"filter": fltr}))

        except NotImplementedError as e:
            raise e
        except Exception as e:
            print(f"Error executing filter command: {e}")

    def _execute_search(self, command):
        try:
            exp = command.args[0]
            toSend = Action("search", {"query": exp})
            self.context.perform_action(toSend)
        except Exception as e:
            print(f"Error executing search command: {e}")

    def _execute_clear(self, command):
        if command.subcommand or command.args or command.kwargs:
            raise MalformedCommandError("Clear command does not take any arguments")
        toSend = Action("clear_console", None)
        self.context.perform_action(toSend)

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

    def _refresh_graph(self):
        toSend = Action("apply_filters", None)
        self.context.perform_action(toSend)
