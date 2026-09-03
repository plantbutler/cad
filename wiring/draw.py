"""Render every bench wiring drawing to SVG and PNG next to this file.

    uv run --with schemdraw --with matplotlib python draw.py

No arguments. Each draw_*.py exposes build() -> (svg, png); style.py holds
the shared look, nets.py the facts.
"""

from __future__ import annotations

import draw_overview
import draw_power
import draw_pump_driver
import draw_sensor_bus

DRAWINGS = (draw_overview, draw_pump_driver, draw_sensor_bus, draw_power)


def main() -> None:
    for mod in DRAWINGS:
        svg, png = mod.build()
        print(f"{mod.STEM:12s} {svg.name}  {png.name}")


if __name__ == "__main__":
    main()
