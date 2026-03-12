import os
from textx import language, metamodel_from_file

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

    if not hasattr(exp, "right") or exp.right is None:
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


class VariableName:
    def __init__(self, name):
        self.name = name


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
