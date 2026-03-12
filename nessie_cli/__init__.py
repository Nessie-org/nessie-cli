import os
from textx import language, metamodel_from_file

__version__ = "0.1.0.dev"


def process_KWParameter(kv):
    try:
        kv.value = (kv.value.key, kv.value.value)
    except AttributeError:
        pass


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
        }
    )

    return mm
