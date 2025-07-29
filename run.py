import os
import sys

import pandas  # noqa: F401
import plotly.express  # noqa: F401
import requests  # noqa: F401
import streamlit
import streamlit.runtime.scriptrunner.magic_funcs  # noqa: F401
import streamlit.web.cli as stcli


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("entrypoint.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
