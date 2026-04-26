from __future__ import annotations

import argparse

from playtest_pulse.dashboard.app import render_dashboard


# ---------------------------------------------------------------------------
# main
#
# Parses dashboard arguments and renders the Streamlit dashboard.
# ---------------------------------------------------------------------------
def main() -> None:
    args = _parse_args()

    render_dashboard(config_path=args.config)


# ---------------------------------------------------------------------------
# _parse_args
#
# Reads command-line arguments passed through Streamlit.
# ---------------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Playtest Pulse Streamlit dashboard.",
    )
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Path to the YAML config file.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
