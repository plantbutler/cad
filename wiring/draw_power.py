"""Drawing 4: power — where the current comes from, what it goes through, where it returns.

Revision 2026-09-03: one 5 V rail, no UBEC. The R4's ISL854102 buck gives
1.2 A total from VIN, so the servo and the relay coil can live on the board's
own 5 V pin where an R3's linear regulator could not have carried them. Two
things follow, and the drawing says both: the board must be fed from the
barrel jack once the servo moves (a USB port is 500 mA against a 650 mA
stall), and C1 belongs at the servo's plug, not at the board.

The 12 V brick still splits into two fused branches: the pump on F1 (its own
leg, slow-blow because a diaphragm pump starts at several times its running
current) and the board on F2. Every return goes to one star point on the power
board, so the pump's current never runs through the board's ground pin.

The three tables and the "never" list come from nets.py, so the drawing and the
README cannot drift apart. Label text must not contain "<" or "&" (schemdraw
parses labels as XML): use "≤" and arrows instead.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from schemdraw import elements as elm

import nets
import style

STEM = "power"
TITLE = "Plant Butler bench: power (one 5 V rail, two fuses, one star)"

# ---------------------------------------------------------------- geometry
X_BUS = 6.6  # the 12 V bus: brick -> F1 (up) and F2 (down)
Y_PUMP = 18.2  # the pump branch
Y_F2 = 12.4  # the board branch
Y_STAR = 2.2  # the star ground line
X_RAIL_END = 42.0
# The tables sit UNDER the schematic, in two columns. Beside it they made the
# canvas 3.2:1, which shrank the 8 pt tap currents - the numbers the drawing
# exists for - to a couple of pixels once the PNG was scaled into the README.
Y_TAB, X_TAB_L, TAB_GAP = 0.9, 0.5, 1.5  # the right column starts a gap past the widest table
X_TAP0, TAP_DX = 16.4, 4.0  # the rail's consumer taps; TAP0 clears the UNO block's right edge
# Ground returns drop to the star in these lanes, chosen to fall in the GAPS
# between the tap labels above them: a lane inside a label reads as a strike-out.
# Only "brick", "star" and "pump" run the length of the rail, so only those three have to
# fall in a gap between tap labels; "star" also has to clear the servo BLOCK (x 22.5-27.9).
X_LANE = {"brick": 6.0, "uno": 13.6, "star": 28.2, "pump": 19.2, "servo": 22.2, "rail": 33.0}
X_NOTE = 29.0  # the two rail notes: right of the "star" lane, left of C1's drop
_PART = {p["ref"]: p for p in nets.INTERLOCK_PARTS}  # by ref: INTERLOCK_PARTS grows


def _a(ic: elm.Ic, name: str):
    return getattr(ic, name)


def _route(d, points, net: str, label: str | None = None, loc: str = "top") -> None:
    """An orthogonal path through `points`; the label goes on the first segment."""
    for i in range(len(points) - 1):
        seg = elm.Line().at(points[i]).to(points[i + 1]).color(style.colour(net))
        if label and i == 0:
            seg.label(label, loc=loc, fontsize=style.FS_BODY, color=style.colour(net))
        d += seg


def _to_star(d, xy, x_stub: float, label: str | None = None, dy: float = 0.0,
             halign: str = "left") -> None:
    """Take a return down to the star line at x_stub (black; crossings carry no dot).

    halign="right" ends the label just left of the lane instead of starting just
    right of it: that is how a label keeps clear of the NEXT lane along.
    """
    pts = [xy, (x_stub, xy[1]), (x_stub, Y_STAR)] if abs(xy[0] - x_stub) > 1e-9 else [xy, (x_stub, Y_STAR)]
    _route(d, pts, "GND")
    if label:
        x = x_stub + (-0.35 if halign == "right" else 0.15)
        d += style.note(label, (x, Y_STAR + 0.5 + dy), net="GND", fontsize=style.FS_PIN,
                        halign=halign)


def build() -> tuple[Path, Path]:
    with style.drawing() as d:
        # ---------------------------------------------------------------- the source
        brick = style.block_at("12 V brick ≥ 3 A\n(read its label:\n2 A browns out at\npump start)",
                               # 12V+ sits exactly on Y_PUMP: off by a fraction, the run out
                               # of the brick is drawn as a diagonal.
                               [("12V+", "right", Y_PUMP - 17.0), ("12V-", "right", 0.6)],
                               (5.0, 2.4)).at((0.5, 17.0))
        d += brick
        d += style.wire(_a(brick, "12V+"), (X_BUS, Y_PUMP), "12V", "-")
        d += style.dot((X_BUS, Y_PUMP), "12V")

        # ---------------------------------------------------------------- pump branch (F1)
        f1 = elm.Fuse().at((X_BUS, Y_PUMP)).right(1.6).color(style.colour("12V")).label(
            f"F1 {nets.FUSES[0]['value']}\n+ leg only", loc="top", fontsize=style.FS_PIN,
            color=style.colour("12V"))
        d += f1
        perf = style.block_at(
            "power board: two 12 V\nterminals and the star\n+ K1 relay module\n(switches the + leg)",
            [("12V_IN", "left", 2.0), ("IN", "left", 0.6, "← D6"), ("PUMP+", "right", 2.0),
             ("GND", "bottom", 5.6, "star")],
            (6.4, 4.0)).at((10.2, 16.2))
        d += perf
        d += style.wire(f1.end, _a(perf, "12V_IN"), "12V", "-")
        pump = style.block_at("pump\n12 V diaphragm\n≤ 1.5 A running,\n3-5x inrush",
                              [("+", "left", 2.0), ("-", "left", 0.8)],
                              (4.6, 4.0)).at((19.8, 16.2))
        d += pump
        d += style.wire(_a(perf, "PUMP+"), _a(pump, "+"), "PUMP_SW", "-", label="relay NO → pump +")
        d += style.note(["the pump's current runs brick → F1 → COM → NO → pump → star,",
                         "and never through the board's GND pin"],
                        (10.2, 21.2), net="PUMP_SW", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- board branch (F2)
        _route(d, [(X_BUS, Y_PUMP), (X_BUS, Y_F2)], "12V")
        f2 = elm.Fuse().at((X_BUS, Y_F2)).right(1.6).color(style.colour("12V")).label(
            f"F2 {nets.FUSES[1]['value']}", loc="top", fontsize=style.FS_PIN,
            color=style.colour("12V"))
        d += f2
        uno = style.block_at("Arduino UNO R4 WiFi\nISL854102 buck: 1.2 A\ntotal from VIN",
                             [("VIN", "left", 3.0), ("5V", "right", 1.6, "OUTPUT"),
                              ("GND", "bottom", 2.5)],
                             (5.0, 4.0)).at((10.2, 9.4))
        d += uno
        # "-|", not "-": VIN is the only pin on that side, so block_at centres it (its z is
        # ignored) and a straight run from F2 would be drawn as a diagonal.
        d += style.wire(f2.end, _a(uno, "VIN"), "12V", "-|", label="12 V")
        d += style.note(["barrel jack, not USB, from bring-up 6 on:", "a 500 mA port will not carry a 650 mA stall"],
                        (7.0, 8.4), net="12V", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the 5V_BOARD rail
        rail_start = _a(uno, "5V")
        y_rail = rail_start[1]
        _route(d, [rail_start, (X_RAIL_END, y_rail)], "5V_BOARD")
        d += style.dot((X_RAIL_END, y_rail), "5V_BOARD", open_=True)
        d += style.note("5V_BOARD rail (breadboard)", (X_RAIL_END + 0.2, y_rail + 0.05),
                        net="5V_BOARD", fontsize=style.FS_PIN, valign="center")
        skip = ("total", "ceiling")
        loads = [r for r in nets.POWER_BUDGET if r["rail"] == "5V_BOARD" and r["consumer"] not in skip]
        total = next(r for r in nets.POWER_BUDGET if r["consumer"] == "total")
        ceiling = next(r for r in nets.POWER_BUDGET if r["consumer"] == "ceiling")
        x_servo = X_TAP0 + TAP_DX * (len(loads) - 1)
        for i, row in enumerate(loads):
            x = X_TAP0 + TAP_DX * i
            d += elm.Line().at((x, y_rail)).down(0.7).color(style.colour("5V_BOARD"))
            d += style.dot((x, y_rail), "5V_BOARD")
            d += style.note([row["consumer"], row["current"]], (x + 0.18, y_rail - 0.85),
                            net="5V_BOARD", fontsize=style.FS_PIN)
        # to the right of the "star" lane: under the taps it was crossed by three returns
        # wrapped to fit the lane between the "star" return and the servo's drop line
        d += style.note(textwrap.wrap(
            f"total {total['current']}. Ceiling {ceiling['current']}: {ceiling['note']}. "
            "On USB the port is the limit (500 mA) and the servo alone exceeds it.", 68),
            (X_NOTE, y_rail - 2.1), net="5V_BOARD", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the servo, on that rail
        servo = style.block_at("SG90 continuous servo\n~250 mA run, ~650 mA stall",
                               [("red", "left", 1.2), ("brown", "left", 0.5)],
                               (5.4, 1.8)).at((22.5, 4.2))
        d += servo
        red, brown = _a(servo, "red"), _a(servo, "brown")
        _route(d, [(x_servo, y_rail - 0.7), (x_servo, 7.4), (red[0], 7.4), red], "5V_BOARD")
        x_c1 = x_servo - 1.6  # beside the run, so its drop to the star clears the servo block
        d += style.dot((x_c1, 7.4), "5V_BOARD")
        d += elm.Capacitor(polar=True).at((x_c1, 7.4)).down(1.8).color(style.colour("5V_BOARD"))
        # left of the cap, not right: right of it is the servo tap's drop line
        d += style.note([f"C1 {_PART['C1']['value']}", "+ 100 nF, AT THE PLUG"], (x_c1 - 0.5, 6.9),
                        net="5V_BOARD", fontsize=style.FS_PIN, halign="right")
        _route(d, [(x_c1, 5.6), (x_c1, Y_STAR)], "GND")
        d += style.note("its own pair from the rail's feed point", (X_NOTE, 7.15),
                        net="5V_BOARD", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the star
        d += elm.Line().at((2.4, Y_STAR)).to((X_RAIL_END, Y_STAR)).color(style.colour("GND"))
        d += style.ground((13.0, Y_STAR))
        d += style.note("GND star, on the power board: one point, every return",
                        (13.3, Y_STAR - 0.5), net="GND", fontsize=style.FS_PIN)
        _to_star(d, _a(brick, "12V-"), X_LANE["brick"], "brick 12V-")
        # These lanes cross the 5V_BOARD rail, which is fine (a crossing carries no dot) as long
        # as none of them crosses within 0.1 of the 5 V pin, where it would read as a short.
        _to_star(d, _a(perf, "GND"), X_LANE["star"],
                 "the star itself:\nbrick 12V-, pump -,\nUNO GND, servo brown", dy=1.4, halign="right")
        _to_star(d, _a(uno, "GND"), X_LANE["uno"], "UNO GND")
        _to_star(d, _a(pump, "-"), X_LANE["pump"], "pump - (12 V return)", halign="right")
        _to_star(d, brown, X_LANE["servo"], "servo brown", dy=0.7)
        stub = elm.Line().at((X_LANE["rail"], Y_STAR)).up(1.4).color(style.colour("GND"))
        d += stub
        d += style.dot(stub.end, "GND", open_=True)
        d += style.note("breadboard GND rail\n(one wire from the star)",
                        (X_LANE["rail"] + 0.2, stub.end[1] + 0.3), net="GND", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- tables and rules
        fuse_lines = style.table_lines(nets.FUSES, [("ref", "ref"), ("value", "value"),
                                                    ("branch", "branch"), ("leg", "leg")])
        budget_lines = style.table_lines(nets.POWER_BUDGET,
                                         [("rail", "rail"), ("consumer", "consumer"),
                                          ("current", "current"), ("note", "note")])
        x_tab_r = X_TAB_L + max(len(ln) for ln in fuse_lines + budget_lines) * style.CH + TAB_GAP
        y = style.table_note(d, "fuses (+ leg only, never a return)", fuse_lines, (X_TAB_L, Y_TAB))
        style.table_note(d, "what draws from which rail", budget_lines, (X_TAB_L, y - 0.9))
        h_never = (len(nets.NEVER) + 1) * style.LH + 0.5
        d += style.frame((x_tab_r, Y_TAB - h_never),
                         max(len(n) for n in nets.NEVER) * style.CH + 0.5, h_never, label="never")
        d += style.note([f"- {n}" for n in nets.NEVER], (x_tab_r + 0.25, Y_TAB - 0.25),
                        fontsize=style.FS_PIN)
        d += style.note(textwrap.wrap(nets.BENCH_POWER_ALT, 104),
                        (x_tab_r, Y_TAB - h_never - 0.9), fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- legend
        style.legend(d, (0.5, 8.6), ("12V", "5V_BOARD", "PUMP_SW", "GND"))
        # Wrapped short on purpose: the brick's return runs down x=6.0, and any line
        # that reaches it is drawn through.
        d += style.note(["A crossing without a dot is not",
                         "a connection. Signals are in",
                         "overview.png; the relay and its",
                         "resistors in pump-driver.png."],
                        (0.5, 6.4), fontsize=style.FS_PIN)

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
