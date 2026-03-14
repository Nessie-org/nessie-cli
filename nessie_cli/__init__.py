import os
from textx import language, metamodel_from_file

from nessie_api.models import Action, plugin
from nessie_api.models import ConsoleMessageType

from .interpreter import Interpreter, MalformedCommandError

__version__ = "0.1.0.dev"


def process_KWParameter(kv):
    try:
        kv.value = (kv.value.key, kv.value.value)
    except AttributeError:
        pass


def process_expression(exp):
    print(
        f"Processing expression: {type(exp).__name__}",
        type(exp.right) if hasattr(exp, "right") else "No right",
    )

    if not hasattr(exp, "left"):
        return exp

    if isinstance(exp.op, list):
        exp.op = exp.op[0] if exp.op else None

    if (not hasattr(exp, "right") or exp.right is None) and not hasattr(exp, "op"):
        return process_expression(exp.left)
    elif hasattr(exp, "left") and not hasattr(exp, "right") and hasattr(exp, "op"):
        if exp.op is not None:
            return exp
        else:
            return process_expression(exp.left)
    else:
        exp.left = process_expression(exp.left)
        if isinstance(exp.right, list):
            rhs = [process_expression(e) for e in exp.right]
            if not any(rhs):
                del exp.right
            else:
                exp.right = rhs if any(rhs) else None
        else:
            ret = process_expression(exp.right)
            if ret is None:
                del exp.right
            else:
                exp.right = ret

        if not hasattr(exp, "right") and hasattr(exp, "left"):
            return exp.left
        elif not hasattr(exp, "left") and hasattr(exp, "right"):
            return exp.right
        elif not hasattr(exp, "left") and not hasattr(exp, "right"):
            return None

        return exp


@language("nessie_cli", "*.nss")
def nessie_cli_language():
    "nessie_cli language"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, "nessie_cli.tx"))

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    mm.register_obj_processors(
        {
            "KWParameter": process_KWParameter,
            "OrExpression": process_expression,
        }
    )

    return mm


def handle_command_action(action, context):
    try:
        command = action.payload.get("command")
    except AttributeError:
        send_message_to_console(
            "Malformed action payload: 'command' key not found",
            ConsoleMessageType.ERROR,
            context,
        )
        return
    if command:
        try:
            interpreter = Interpreter(context=context, verbose=True)
            return interpreter.execute_command(command)
        except MalformedCommandError as e:
            send_message_to_console(str(e), ConsoleMessageType.ERROR, context)
        except Exception as e:
            send_message_to_console(
                f"Error executing command [THIS MESSAGE IS MEANT TO BE SENT IN DEVELOPEMENT]:\n{e}",
                ConsoleMessageType.ERROR,
                context,
            )
    else:
        print("No command found in action payload")


def send_message_to_console(message, type, context):
    context.perform_action(
        Action("add_console_message", {"message": {"message": message, "type": type}})
    )


@plugin("nessie-cli")
def cli_plugin():
    requires = [
        "add_console_message",
        "clear_console",
        "add_filter",
        "remove_filter",
        "clear_filters",
        "search",
    ]
    handlers = {"cli_execute": handle_command_action}
    return {"requires": requires, "handlers": handlers}
