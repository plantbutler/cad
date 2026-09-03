"""Drawing 2: what switches the pump, and what holds it off.

Revision 2026-09-03. The 74HC00 and the MOSFET are gone: a bought relay
module switches the 12 V + leg, and the interlock moved into firmware. What
is left in hardware is worth reading in one glance:

  * the 12 V loop -- brick, F1, COM, NO, pump, star -- crosses no board pin;
  * D6 reaches nothing but the relay's IN, with R1 holding the OFF level
    whenever D6 is not an asserted output (reset, boot, jumper pulled);
  * the float hall goes straight to D5 through R2 and through no gate at all,
    which is the honest picture: nothing in hardware ANDs "firmware says pump"
    with "the tank has water" any more. See nets.INTERLOCK_NOTES, THE GAP.

Values and roles come from nets.INTERLOCK_PARTS, the terminal names from
nets.PERFBOARD_TERMINALS and nets.RELAY_TERMINALS.

Label text must not contain "<" or "&": schemdraw's bbox estimator parses
labels as XML. Use arrows and "≤".
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from schemdraw import elements as elm

import nets
import style

STEM = "pump-driver"
TITLE = "Plant Butler bench: what switches the pump (relay) and what holds it off"

# ---------------------------------------------------------------- geometry
X_FL, X_FR = 3.0, 9.0  # power-board frame edges
Y_FB, Y_FT = 4.6, 11.2  # frame bottom / top
Y_12V = 9.8  # brick + leg: 12V_IN -> 12V_OUT -> COM -> NO -> pump +
Y_BRK = 7.4  # brick 12V- terminal
Y_STAR = 5.6  # the star row
X_STAR = 6.0  # the star dot
X_RET = 1.2  # the pump's return runs up this line into the star stub
Y_RET = -0.2  # ... along this one, below every block
EXT_F1 = 6.0  # the 12V_IN stub: long, F1 sits on it
EXT = 1.8

REL = (12.0, 6.4)  # relay block, lower-left corner
REL_SIZE = (7.4, 4.2)
UNO = (13.6, 1.2)
UNO_SIZE = (4.6, 2.2)
RAILS = (19.6, 1.2)
RAILS_SIZE = (4.8, 2.2)
HALL = (2.0, 1.2)
HALL_SIZE = (5.6, 2.2)
PUMP = (22.4, 8.0)
PUMP_SIZE = (4.4, 2.6)

_PART = {p["ref"]: p for p in nets.INTERLOCK_PARTS}
_TERM = {t["terminal"]: t for t in nets.PERFBOARD_TERMINALS}


def _a(ic: elm.Ic, name: str):
    return getattr(ic, name)


def _route(d, points, net: str, label: str | None = None, loc: str = "top") -> None:
    """An orthogonal path through `points`; the label goes on the first segment."""
    for i in range(len(points) - 1):
        seg = elm.Line().at(points[i]).to(points[i + 1]).color(style.colour(net))
        if label and i == 0:
            seg.label(label, loc=loc, fontsize=style.FS_BODY, color=style.colour(net))
        d += seg


def _terminal(d, xy, name: str, side: str, ext_label, net: str, ext_len: float = EXT,
              name_below: bool = False, ext_halign: str = "left"):
    """A screw terminal on the frame edge: a square, its name inside, a stub outwards."""
    x, y = xy
    c = style.colour(net)
    d += elm.Rect(corner1=(x - 0.14, y - 0.14), corner2=(x + 0.14, y + 0.14),
                  fill="white", lw=1.4).at((0, 0)).theta(0).color(c)
    y_name = y - 0.17 if name_below else y + 0.3
    if side == "left":
        d += style.line("left", ext_len, net).at((x - 0.14, y))
        # ext_halign="right": the label ends left of the stub, clear of the frame edge
        # and of the pump return that comes up this side.
        x_lbl = x - 0.14 - ext_len + (-0.11 if ext_halign == "right" else 0.0)
        d += style.note(ext_label, (x_lbl, y - 0.62), net=net, fontsize=style.FS_PIN,
                        halign=ext_halign)
        d += style.note(name, (x + 0.22, y_name), net=net, fontsize=style.FS_PIN)
        return (x - 0.14 - ext_len, y)
    d += style.line("right", ext_len, net).at((x + 0.14, y))
    d += style.note(ext_label, (x + 0.3, y + 0.36), net=net, fontsize=style.FS_PIN)
    d += style.note(name, (x - 0.22, y_name), net=net, fontsize=style.FS_PIN, halign="right")
    return (x + 0.14 + ext_len, y)


def _flag(d, xy, net: str, text, up: float = 1.4):
    """A short stub ending in an open dot: the rail, drawn where it is tapped."""
    d += style.line("up", up, net).at(xy)
    top = (xy[0], xy[1] + up)
    d += style.dot(top, net, open_=True)
    d += style.note(text, (top[0] + 0.18, top[1] + 0.1), net=net, fontsize=style.FS_PIN)


def build() -> tuple[Path, Path]:
    red = style.colour("12V")

    with style.drawing() as d:
        # ------------------------------------------------ the power board
        d += style.frame((X_FL, Y_FB), X_FR - X_FL, Y_FT - Y_FB,
                         label="power board: F1, two 12 V terminals, the star.\n"
                               "Soldered, screw terminals, >= 0.5 mm2 (never breadboard / Dupont)")
        f1_end = _terminal(d, (X_FL, Y_12V), "12V_IN", "left", "brick 12V+", "12V",
                           ext_len=EXT_F1, name_below=True)
        d += elm.Fuse().at((f1_end[0] + 1.2, Y_12V)).right(2.0).color(red).label(
            f"F1 {_PART['F1']['value']}, + leg only", loc="top", fontsize=style.FS_PIN, color=red)
        d += style.line("right", X_FR - X_FL, "12V", label="12 V").at((X_FL, Y_12V))
        out_end = _terminal(d, (X_FR, Y_12V), "12V_OUT", "right", "to relay COM", "12V")

        brk_end = _terminal(d, (X_FL, Y_BRK), "", "left", "brick 12V-", "GND")  # noqa: F841
        _route(d, [(X_FL, Y_BRK), (X_STAR, Y_BRK), (X_STAR, Y_STAR)], "GND")
        star_end = _terminal(d, (X_FL, Y_STAR), "GND (star)", "left",
                             ["pump -, UNO GND,", "servo brown,", "breadboard GND rail"], "GND",
                             ext_halign="right")
        d += style.line("right", X_STAR - X_FL, "GND").at((X_FL, Y_STAR))
        d += elm.Dot(radius=0.17).at((X_STAR, Y_STAR)).color(style.colour("GND"))
        d += style.note("one star, every return", (X_STAR + 0.3, Y_STAR - 0.1),
                        net="GND", fontsize=style.FS_PIN)

        # ------------------------------------------------ the relay module
        relay = style.block_at(
            "K1  relay module\n(bought; VERIFY active-HIGH\nor active-LOW on IN)",
            [("COM", "left", 3.4), ("IN", "left", 0.8),
             ("NO", "right", 3.4), ("NC", "right", 0.8),
             ("VCC", "bottom", 2.4), ("GND", "bottom", 5.0)],
            REL_SIZE, pinspacing=2.6).at(REL)
        d += relay
        d += style.wire(out_end, _a(relay, "COM"), "12V", "-")
        d += style.note("NC: not connected.\nNO, so a dead coil is a dead pump.",
                        (_a(relay, "NC")[0] + 0.25, _a(relay, "NC")[1] + 0.1),
                        net="NOTE", fontsize=style.FS_PIN)

        # ------------------------------------------------ the pump and its return
        pump = style.block_at("PUMP  12 V diaphragm\nASSUME ≤ 1.5 A running,\n3-5x inrush (read the label)",
                              [("+", "left", 1.8), ("-", "left", 0.8)], PUMP_SIZE,
                              pinspacing=1.0).at(PUMP)
        d += pump
        d += style.wire(_a(relay, "NO"), _a(pump, "+"), "PUMP_SW", "-",
                        label="switched 12 V", loc="top")
        minus = _a(pump, "-")
        _route(d, [minus, (PUMP[0] + PUMP_SIZE[0] + 1.2, minus[1]),
                   (PUMP[0] + PUMP_SIZE[0] + 1.2, Y_RET), (X_RET, Y_RET), (X_RET, Y_STAR),
                   star_end], "GND")
        d += style.dot(star_end, "GND")
        d += style.note("the pump's 12 V return: brick → F1 → COM → NO → pump → star, "
                        "and never through a board pin",
                        (X_RET + 0.3, Y_RET - 0.15), net="GND", fontsize=style.FS_PIN)

        # ------------------------------------------------ the logic side
        uno = style.block_at("Arduino UNO R4 WiFi", [("D6", "top", 2.3), ("D5", "left", 1.1)],
                             UNO_SIZE).at(UNO)
        d += uno
        rails = style.block_at("breadboard rails", [("+5V", "top", 1.4), ("GND", "top", 3.4)],
                               RAILS_SIZE, pinspacing=2.0).at(RAILS)
        d += rails
        hall = style.block_at("float hall (WPSE313)\n+ to 5V_BOARD, - to GND",
                              [("S", "right", 1.1)], HALL_SIZE).at(HALL)
        d += hall

        # D6 -> IN, with R1 holding the OFF level
        d6, inp = _a(uno, "D6"), _a(relay, "IN")
        y_en = 5.4
        _route(d, [d6, (d6[0], y_en), (inp[0], y_en), inp], "SIGNAL", label="PUMP_EN", loc="bottom")
        d += style.dot((12.6, y_en), "SIGNAL")
        d += elm.Resistor().at((12.6, y_en)).down(1.6).color(style.colour("SIGNAL")).label(
            f"R1 {_PART['R1']['value']}", loc="bottom", fontsize=style.FS_PIN,
            color=style.colour("SIGNAL"), halign="right")
        d += style.dot((12.6, y_en - 1.6), "SIGNAL", open_=True)
        d += style.note("to the module's OFF level (see below)", (12.85, y_en - 1.72),
                        net="SIGNAL", fontsize=style.FS_PIN)

        # coil supply
        _route(d, [_a(rails, "+5V"), (_a(rails, "+5V")[0], 4.6), (_a(relay, "VCC")[0], 4.6),
                   _a(relay, "VCC")], "5V_BOARD", label="coil ~80 mA", loc="bottom")
        _route(d, [_a(rails, "GND"), (_a(rails, "GND")[0], 5.2), (_a(relay, "GND")[0], 5.2),
                   _a(relay, "GND")], "GND")

        # float hall -> D5, with R2 pulling an open line to "not OK"
        s, d5 = _a(hall, "S"), _a(uno, "D5")
        d += style.wire(s, d5, "SIGNAL", "-", label="float sense: straight to D5, no gate",
                        loc="bottom")
        d += style.dot((10.0, s[1]), "SIGNAL")
        d += elm.Resistor().at((10.0, s[1])).up(1.6).color(style.colour("5V_BOARD")).label(
            f"R2 {_PART['R2']['value']}", loc="top", fontsize=style.FS_PIN,
            color=style.colour("5V_BOARD"), halign="right")
        d += style.line("up", 0.4, "5V_BOARD").at((10.0, s[1] + 1.6))
        d += style.dot((10.0, s[1] + 2.0), "5V_BOARD", open_=True)
        d += style.note("5V_BOARD rail: an open, dead\nor unplugged hall reads 'not OK'",
                        (9.6, s[1] + 2.0), net="5V_BOARD", fontsize=style.FS_PIN, halign="right")

        # ------------------------------------------------ notes
        notes = []
        for n in nets.RELAY_NOTES[:5]:
            notes += textwrap.wrap(f"- {n}", 108, subsequent_indent="  ")
        d += style.note(notes, (13.5, Y_FT + 4.0), fontsize=style.FS_PIN)
        d += style.note([
            "R1 pulls D6 to whichever level leaves the relay OFF: to GND if the module's IN is active-HIGH, to",
            "5V_BOARD if it is active-LOW. It is what holds the pump off while D6 is still an input - at reset,",
            "during boot, and with the jumper pulled - so its direction is decided by reading the module, not guessed.",
        ], (X_RET, Y_RET - 1.1), net="SIGNAL", fontsize=style.FS_PIN)
        d += style.note([
            "THE GAP: no hardware AND any more. A sketch that hangs with D6 asserted keeps the pump running.",
            "Bounded only by firmware: the watchdog enabled (the WDT, not DECISIONS #10's IWDT), a hard maximum",
            "run time beside the line that asserts D6, and a no-flow abort from the meter. A float that grants",
            "permission while the meter counts nothing latches, and every later dose is refused until a human clears it.",
            "Plan item 4 puts a 74HC00 back between D6, the float and IN.",
        ], (X_RET, Y_RET - 2.3), net="PUMP_SW", fontsize=style.FS_PIN)
        style.legend(d, (X_RET, Y_RET - 4.4), ("12V", "PUMP_SW", "5V_BOARD", "GND", "SIGNAL"))

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
