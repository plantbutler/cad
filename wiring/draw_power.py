"""Drawing 4: power — where the current comes from, what it goes through, where it returns.

One 12 V brick, split into two fused branches: the pump on F1 (its own leg,
slow-blow because a diaphragm pump starts at several times its running current),
and the board plus the UBEC on F2. Two 5 V rails that are never joined: the
board's own 5 V pin feeds the sensors and the logic (it is an OUTPUT, never fed
from outside), and the UBEC feeds the servo and nothing else. Every return goes
to one star point on the pump-driver perfboard, so the pump's current never runs
through the board's ground pin.

The three tables and the "never" list come from nets.py, so the drawing and the
README cannot drift apart. Label text must not contain "<" or "&" (schemdraw
parses labels as XML): use "≤" and arrows instead.
"""

from __future__ import annotations

from pathlib import Path

from schemdraw import elements as elm

import nets
import style

STEM = "power"
TITLE = "Plant Butler bench: power (rails, fuses, star ground)"

# ---------------------------------------------------------------- geometry
X_BUS = 6.6  # the 12 V bus: brick -> F1 (up) and F2 (down)
Y_PUMP_BRANCH = 18.2  # the pump branch runs along here
Y_F2 = 12.4  # the board / UBEC branch
Y_STAR = 2.2  # the star ground line
X_TAB = 33.0  # the tables column
X_RAIL_END = 29.6  # the 5V_BOARD rail ends here (its height comes from the 5 V pin)


def _a(ic: elm.Ic, name: str):
    return getattr(ic, name)


def _route(d, points, net: str, label: str | None = None, loc: str = "top") -> None:
    """An orthogonal path through `points`; the label goes on the first segment."""
    for i in range(len(points) - 1):
        seg = elm.Line().at(points[i]).to(points[i + 1]).color(style.colour(net))
        if label and i == 0:
            seg.label(label, loc=loc, fontsize=style.FS_BODY, color=style.colour(net))
        d += seg


def _to_star(d, xy, x_stub: float, label: str | None = None, dy: float = 0.0) -> None:
    """Take a return down to the star line at x_stub (black; crossings carry no dot).

    `dy` lifts the label, so two returns that land close together stay legible.
    """
    pts = [xy, (x_stub, xy[1]), (x_stub, Y_STAR)] if abs(xy[0] - x_stub) > 1e-9 else [xy, (x_stub, Y_STAR)]
    _route(d, pts, "GND")
    if label:
        d += style.note(label, (x_stub + 0.15, Y_STAR + 0.5 + dy), net="GND", fontsize=style.FS_PIN)


def build() -> tuple[Path, Path]:
    with style.drawing() as d:
        # ---------------------------------------------------------------- the source
        brick = style.block_at("12 V brick ≥ 3 A\n(read its label:\n2 A browns out at\npump start)",
                               # 12V+ sits exactly on Y_PUMP_BRANCH: off by a fraction, the run
                               # out of the brick is drawn as a diagonal.
                               [("12V+", "right", Y_PUMP_BRANCH - 17.0), ("12V-", "right", 0.6)],
                               (5.0, 2.4)).at((0.5, 17.0))
        d += brick
        d += style.wire(_a(brick, "12V+"), (X_BUS, Y_PUMP_BRANCH), "12V", "-")
        d += style.dot((X_BUS, Y_PUMP_BRANCH), "12V")

        # ---------------------------------------------------------------- pump branch (F1)
        f1 = elm.Fuse().at((X_BUS, Y_PUMP_BRANCH)).right(1.6).color(style.colour("12V")).label(
            f"F1 {nets.FUSES[0]['value']}\n+ leg only", loc="top", fontsize=style.FS_PIN,
            color=style.colour("12V"))
        d += f1
        perf = style.block_at(
            "pump driver + interlock\nperfboard: MOSFET low side,\n74HC00 interlock, flyback\ndiode across the pump",
            [("12V_IN", "left", 2.2), ("PUMP+", "right", 2.8), ("PUMP-", "right", 1.6),
             ("GND", "bottom", 5.6, "star")],
            (6.4, 4.0)).at((10.2, 16.2))
        d += perf
        d += style.wire(f1.end, _a(perf, "12V_IN"), "12V", "-")
        pump = style.block_at("pump\n12 V diaphragm\n≤ 1.5 A running,\n3-5x inrush",
                              [("+", "left", 2.8), ("-", "left", 1.6)],
                              (4.6, 4.0)).at((19.8, 16.2))
        d += pump
        d += style.wire(_a(perf, "PUMP+"), _a(pump, "+"), "12V", "-", label="PUMP+")
        d += style.wire(_a(perf, "PUMP-"), _a(pump, "-"), "PUMP_SW", "-",
                        label="PUMP- switched by the MOSFET", loc="bottom")
        d += style.note(["the pump's current runs brick → F1 → pump → MOSFET → star,",
                         "and never through the board's GND pin"],
                        (10.2, 21.2), net="PUMP_SW", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- board / UBEC branch (F2)
        _route(d, [(X_BUS, Y_PUMP_BRANCH), (X_BUS, Y_F2)], "12V")
        f2 = elm.Fuse().at((X_BUS, Y_F2)).right(1.6).color(style.colour("12V")).label(
            f"F2 {nets.FUSES[1]['value']}", loc="top", fontsize=style.FS_PIN,
            color=style.colour("12V"))
        d += f2
        node = (9.4, Y_F2)
        d += style.wire(f2.end, node, "12V", "-")
        d += style.dot(node, "12V")
        uno = style.block_at("Arduino UNO R4 WiFi\n(on-board buck)",
                             [("VIN", "left", 3.0), ("5V", "right", 1.6, "OUTPUT"),
                              ("GND", "bottom", 2.5)],
                             (5.0, 4.0)).at((10.2, 9.4))
        d += uno
        # "-|", not "-": VIN is the only pin on that side, so block_at centres it (its z is
        # ignored) and a straight run from the F2 node would be drawn as a diagonal.
        d += style.wire(node, _a(uno, "VIN"), "12V", "-|", label="12V")
        ubec = style.block_at("5 V UBEC ≥ 3 A",
                              [("IN+", "left", 1.4), ("IN-", "left", 0.6),
                               ("OUT+", "right", 1.4), ("OUT-", "right", 0.6)],
                              (5.0, 2.0)).at((17.2, 5.0))
        d += ubec
        _route(d, [node, (node[0], 6.4), _a(ubec, "IN+")], "12V")
        servo = style.block_at("SG90 continuous servo\n~250 mA run, ~650 mA stall",
                               [("red", "left", 1.2), ("brown", "left", 0.5)],
                               (5.4, 1.8)).at((25.6, 5.2))
        d += servo
        out_plus, red = _a(ubec, "OUT+"), _a(servo, "red")
        _route(d, [out_plus, red], "5V_SERVO")
        d += style.note("5V_SERVO: this wire and no other", (out_plus[0] + 0.2, red[1] + 0.9),
                        net="5V_SERVO", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the 5V_BOARD rail
        rail_start = _a(uno, "5V")
        y_rail = rail_start[1]
        _route(d, [rail_start, (X_RAIL_END, y_rail)], "5V_BOARD")
        d += style.dot((X_RAIL_END, y_rail), "5V_BOARD", open_=True)
        d += style.note("5V_BOARD rail (breadboard)", (X_RAIL_END + 0.2, y_rail + 0.05),
                        net="5V_BOARD", fontsize=style.FS_PIN, valign="center")
        loads = [r for r in nets.POWER_BUDGET if r["rail"] == "5V_BOARD" and r["consumer"] != "total"]
        total = next(r for r in nets.POWER_BUDGET if r["consumer"] == "total")
        x = 17.6
        for row in loads:
            d += elm.Line().at((x, y_rail)).down(0.7).color(style.colour("5V_BOARD"))
            d += style.dot((x, y_rail), "5V_BOARD")
            d += style.note([row["consumer"], row["current"]], (x - 0.15, y_rail - 0.85),
                            net="5V_BOARD", fontsize=style.FS_PIN)
            x += 3.4
        d += style.note(f"total {total['current']}, {total['note']}", (17.4, y_rail - 1.75),
                        net="5V_BOARD", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the star
        d += elm.Line().at((2.4, Y_STAR)).to((28.6, Y_STAR)).color(style.colour("GND"))
        d += style.ground((13.0, Y_STAR))
        d += style.note("GND star, on the pump-driver perfboard: one point, every return",
                        (13.3, Y_STAR - 0.5), net="GND", fontsize=style.FS_PIN)
        _to_star(d, _a(brick, "12V-"), 6.0, "brick 12V-")
        # 16.2, not 15.8: this return has to cross the 5V_BOARD rail somewhere, and at 15.8
        # it crosses 0.1 from the 5 V pin, where the crossing reads as a short to GND.
        _to_star(d, _a(perf, "GND"), 16.2, "MOSFET source,\n74HC00 GND", dy=1.1)
        _to_star(d, _a(uno, "GND"), 12.7, "UNO GND")
        _to_star(d, _a(ubec, "IN-"), _a(ubec, "IN-")[0], "UBEC IN-")
        _to_star(d, _a(ubec, "OUT-"), _a(ubec, "OUT-")[0], "UBEC OUT-")
        _to_star(d, _a(servo, "brown"), _a(servo, "brown")[0], "servo brown")
        stub = elm.Line().at((28.0, Y_STAR)).up(1.4).color(style.colour("GND"))
        d += stub
        d += style.dot(stub.end, "GND", open_=True)
        d += style.note("breadboard GND rail\n(one wire from the star)", (27.8, stub.end[1] + 0.3),
                        net="GND", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- tables and rules
        y = style.table_note(d, "fuses (+ leg only, never a return)",
                             style.table_lines(nets.FUSES, [("ref", "ref"), ("value", "value"),
                                                            ("branch", "branch"), ("leg", "leg")]),
                             (X_TAB, 21.4))
        y = style.table_note(d, "what draws from which rail",
                             style.table_lines(nets.POWER_BUDGET,
                                               [("rail", "rail"), ("consumer", "consumer"),
                                                ("current", "current"), ("note", "note")]),
                             (X_TAB, y - 0.9))
        d += style.frame((X_TAB, y - 0.9 - (len(nets.NEVER) + 1) * style.LH - 0.5),
                         max(len(n) for n in nets.NEVER) * style.CH + 0.5,
                         (len(nets.NEVER) + 1) * style.LH + 0.5, label="never")
        d += style.note([f"- {n}" for n in nets.NEVER], (X_TAB + 0.25, y - 1.15),
                        fontsize=style.FS_PIN)
        d += style.note(nets.BENCH_POWER_ALT,
                        (X_TAB, y - 2.0 - (len(nets.NEVER) + 1) * style.LH - 0.5),
                        fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- legend
        style.legend(d, (0.5, 8.6), ("12V", "5V_BOARD", "5V_SERVO", "PUMP_SW", "GND"))
        d += style.note(["A crossing without a dot is not a connection.",
                         "Signals are in overview.png; the driver's own",
                         "parts in pump-driver.png."],
                        (0.5, 6.4), fontsize=style.FS_PIN)

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
