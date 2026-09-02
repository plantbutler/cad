"""Drawing 1: the overview — every module on the bench and the wire between them.

Reading order: the sensors on the left go into the mux, the mux and the I2C
expander into the board, the board out to the manifold's flow meter, halls and
servo on the right, and the board's two interlock lines into the pump-driver
perfboard, which switches the pump. The 12 V brick feeds the perfboard, the
board's VIN and the UBEC; the UBEC feeds nothing but the servo. The water path
is the strip along the bottom, and the float hall at the reservoir wires back
up into the perfboard.

Conventions kept small on purpose, so the drawing stays readable:
  * a wire that carries a signal is drawn and labelled with its signal name;
  * power is drawn as flags, not as a net of lines: an orange stub with an open
    dot is the 5V_BOARD rail, and every ground symbol is the same node (the star
    on the perfboard). Only the sources are drawn as real lines: brick -> fuses
    -> consumers, UNO 5 V pin -> rail, UBEC -> servo.
Every wire, with its connector, colour and length, is in README.md's pin map.

Label text must not contain "<" or "&" (schemdraw parses labels as XML): use
"≤" and arrows instead.
"""

from __future__ import annotations

from pathlib import Path

from schemdraw import elements as elm

import nets
import style

STEM = "overview"
TITLE = "Plant Butler bench: overview (one manifold, 5 outlets)"

# ---------------------------------------------------------------- geometry
# Everything is placed by hand: the drawing is a map of the bench, not a netlist
# dump, so the blocks sit where the things sit and no wire needs a diagonal.
X_SENS, W_SENS = 0.5, 5.0  # left column: the sensors in the pots
X_MUX, W_MUX = 9.0, 4.5  # mux and expander column
X_UNO, W_UNO = 17.0, 5.0  # the board
X_RIGHT, W_RIGHT = 25.5, 5.0  # manifold side: flow meter, halls, servo, DHT
X_PERF, W_PERF = 34.5, 6.0  # the pump-driver perfboard
Y_12V = 22.4  # the 12 V distribution run, above everything
Y_STRIP = (-6.8, -0.6)  # the hydraulic strip frame
X_STRIP = (22.5, 46.4)


def _a(ic: elm.Ic, name: str):
    """Anchor `name` of a placed block (pin names like "+" are not identifiers)."""
    return getattr(ic, name)


def _route(d, points, net: str = "SIGNAL", label: str | None = None, loc: str = "top") -> None:
    """An orthogonal path through `points`; the label goes on the first segment."""
    for i in range(len(points) - 1):
        seg = elm.Line().at(points[i]).to(points[i + 1]).color(style.colour(net))
        if label and i == 0:
            seg.label(label, loc=loc, fontsize=style.FS_BODY, color=style.colour(net))
        d += seg


def _flag5v(d, xy, direction: str = "down", length: float = 0.55) -> None:
    """Power flag: a short orange stub ending in an open dot, meaning the rail."""
    ln = elm.Line().at(xy).color(style.colour("5V_BOARD"))
    getattr(ln, direction)(length)
    d += ln
    d += style.dot(ln.end, "5V_BOARD", open_=True)
    right = direction in ("right", "up")
    d += style.note("5V_BOARD", (ln.end[0] + (0.18 if right else -0.18), ln.end[1] + 0.08),
                    net="5V_BOARD", fontsize=style.FS_PIN,
                    halign="left" if right else "right", valign="center")


def _gnd(d, xy, direction: str = "down", length: float = 0.35) -> None:
    """A ground symbol on a stub: the star on the perfboard, wherever it is drawn."""
    ln = elm.Line().at(xy).color(style.colour("GND"))
    getattr(ln, direction)(length)
    d += ln
    d += style.ground(ln.end)


def build() -> tuple[Path, Path]:
    with style.drawing() as d:
        # ---------------------------------------------------------------- sensors
        moist = style.block_at(
            "5 x capacitive\nmoisture (pots 1-5)",
            [("AOUT1", "right", 4.2), ("AOUT2", "right", 3.4), ("AOUT3", "right", 2.6),
             ("AOUT4", "right", 1.8), ("AOUT5", "right", 1.0),
             ("V", "bottom", 1.4), ("G", "bottom", 3.0)],
            (W_SENS, 5.0)).at((X_SENS, 13.0))
        d += moist
        ldr = style.block_at("Sensor Kit light (LDR)",
                             [("SIG", "right", 0.6), ("V", "bottom", 1.4), ("G", "bottom", 3.0)],
                             (W_SENS, 1.2)).at((X_SENS, 9.8))
        d += ldr
        _flag5v(d, _a(moist, "V"))
        _gnd(d, _a(moist, "G"))
        _flag5v(d, _a(ldr, "V"))
        _gnd(d, _a(ldr, "G"))

        # ---------------------------------------------------------------- mux + expander
        mux = style.block_at(
            "CD74HC4067\nMUX1",
            [("C0", "left", 5.0), ("C1", "left", 4.2), ("C2", "left", 3.4), ("C3", "left", 2.6),
             ("C4", "left", 1.8), ("C5", "left", 1.0),
             ("SIG", "right", 5.0), ("VCC", "right", 2.2), ("GND", "right", 1.4),
             ("S0", "bottom", 1.0), ("S1", "bottom", 1.8), ("S2", "bottom", 2.6),
             ("S3", "bottom", 3.4), ("EN", "bottom", 4.1)],
            (W_MUX, 5.8)).at((X_MUX, 12.2))
        d += mux
        pcf = style.block_at(
            "PCF8575\n0x20",
            [("P0", "top", 1.0), ("P1", "top", 1.8), ("P2", "top", 2.6), ("P3", "top", 3.4),
             ("SDA", "right", 3.6), ("SCL", "right", 3.0),
             ("VCC", "left", 1.6), ("GND", "left", 1.0), ("P4-P15", "left", 3.6, "spare")],
            (W_MUX, 5.4)).at((X_MUX, 5.6))
        d += pcf
        # the flag points up, not right: level with the pin, its label runs into the SDA
        # corner at x = 15.6 and reads as "SDA tied to 5 V".
        _flag5v(d, _a(mux, "VCC"), "up", 0.5)
        _gnd(d, _a(mux, "GND"), "right", 0.5)
        _flag5v(d, _a(pcf, "VCC"), "left", 0.6)
        _gnd(d, _a(pcf, "GND"), "left", 0.5)

        # analog in: one straight wire per sensor; C6-C15 stay open for later pots
        for i in range(5):
            d += style.wire(_a(moist, f"AOUT{i + 1}"), _a(mux, f"C{i}"), "SIGNAL", "-",
                            label=f"MOIST{i + 1}", loc="top")
        d += style.wire(_a(ldr, "SIG"), _a(mux, "C5"), "SIGNAL", "-|", label="LIGHT", loc="bottom")

        # select lines: four short vertical wires, one bus in the firmware's eyes
        for i in range(4):
            d += style.wire(_a(pcf, f"P{i}"), _a(mux, f"S{i}"), "SIGNAL", "-")
        d += style.note("select bus P0→S0 .. P3→S3 (MUX2 will share it later)",
                        (X_MUX, 4.9), net="SIGNAL", fontsize=style.FS_PIN)
        # EN is tied low on the board: the mux is always enabled
        _gnd(d, _a(mux, "EN"), "down", 0.5)
        d += style.note("EN → GND", (_a(mux, "EN")[0] + 0.25, _a(mux, "EN")[1] - 0.55),
                        net="GND", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- the board
        uno = style.block_at(
            "Arduino\nUNO R4 WiFi",
            # the 5 V pin sits one unit clear of SCL's y: level with it, the rail stub and
            # the I2C run would render as one unbroken horizontal line into the pin.
            [("A0", "left", 14.0), ("A4", "left", 11.4), ("A5", "left", 10.6), ("5V", "left", 4.4),
             ("D2", "right", 14.7), ("D3", "right", 11.7), ("D4", "right", 8.7), ("D9", "right", 5.2),
             ("D7", "right", 2.4), ("D6", "right", 1.0), ("D5", "right", 0.5),
             ("VIN", "top", 1.5, "12 V in"), ("GND", "bottom", 2.5)],
            (W_UNO, 14.8)).at((X_UNO, 3.2))
        d += uno
        d += style.wire(_a(mux, "SIG"), _a(uno, "A0"), "SIGNAL", "-", label="MUX1_SIG (14-bit)")
        # I2C: each on its own vertical so the two never share a line
        _route(d, [_a(pcf, "SDA"), (15.6, 9.2), (15.6, 14.6), _a(uno, "A4")], "I2C", "SDA", "bottom")
        _route(d, [_a(pcf, "SCL"), (16.2, 8.6), (16.2, 13.8), _a(uno, "A5")], "I2C", "SCL", "bottom")
        # the 5 V pin is an OUTPUT: it feeds the rail, and the rail feeds every flag
        rail = elm.Line().at(_a(uno, "5V")).left(1.2).color(style.colour("5V_BOARD"))
        d += rail
        d += style.dot(rail.end, "5V_BOARD", open_=True)
        d += style.note(["5V_BOARD rail", "pin = OUTPUT,", "~120 mA"],
                        (14.1, rail.end[1] - 0.75), net="5V_BOARD", fontsize=style.FS_PIN)
        _gnd(d, _a(uno, "GND"), "down", 0.5)
        d += style.note("→ GND star", (_a(uno, "GND")[0] + 0.25, _a(uno, "GND")[1] - 0.3),
                        net="GND", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- manifold side
        def small(label, y, pins, h=2.0):
            blk = style.block_at(label, pins, (W_RIGHT, h), label_loc="top").at((X_RIGHT, y))
            d.add(blk)
            return blk

        flow = small("YF-S401 flow meter (5 V)", 16.4,
                     [("yellow", "left", 1.5, "pulse"), ("red", "left", 1.0, "5 V"),
                      ("black", "left", 0.5, "GND")])
        hall_screw = small("WPSE313 hall: screw", 13.4,
                           [("S", "left", 1.5), ("+", "left", 1.0), ("-", "left", 0.5)])
        hall_home = small("WPSE313 hall: home", 10.4,
                          [("S", "left", 1.5), ("+", "left", 1.0), ("-", "left", 0.5)])
        # brown leaves left, not down: a ground symbol under this block lands on the DHT
        servo = small("SG90 continuous servo", 7.4,
                      [("orange", "left", 1.0, "signal"), ("brown", "left", 0.4, "GND"),
                       ("red", "right", 1.0, "5V_SERVO")])
        dht = small("Sensor Kit DHT11", 4.8,
                    [("SIG", "left", 1.0), ("V", "bottom", 1.4), ("G", "bottom", 3.4)], h=1.6)

        d += style.wire(_a(uno, "D2"), _a(flow, "yellow"), "SIGNAL", "-", label="FLOW")
        d += style.wire(_a(uno, "D3"), _a(hall_screw, "S"), "SIGNAL", "-", label="HALL_SCREW")
        d += style.wire(_a(uno, "D4"), _a(hall_home, "S"), "SIGNAL", "-", label="HALL_HOME")
        d += style.wire(_a(uno, "D9"), _a(servo, "orange"), "SIGNAL", "-", label="SERVO_PWM")
        d += style.wire(_a(uno, "D7"), _a(dht, "SIG"), "SIGNAL", "-", label="DHT_DATA")
        for blk, pin_v, pin_g in ((flow, "red", "black"), (hall_screw, "+", "-"),
                                  (hall_home, "+", "-")):
            _flag5v(d, _a(blk, pin_v), "left", 0.7)
            _gnd(d, _a(blk, pin_g), "left", 0.5)
        _flag5v(d, _a(dht, "V"))
        _gnd(d, _a(dht, "G"))
        _gnd(d, _a(servo, "brown"), "left", 0.6)
        d += style.note(["5V_BOARD only,", "never 12 V"],
                        (X_RIGHT + W_RIGHT + 1.4, 18.9), net="5V_BOARD", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- perfboard
        perf = style.block_at(
            "pump driver + interlock\nperfboard (soldered,\nscrew terminals)",
            [("5V_BOARD", "left", 8.6), ("PUMP_EN", "left", 8.0), ("FLOAT_OK", "left", 7.2),
             ("FLT_S", "right", 5.6), ("FLT_+", "right", 5.0), ("FLT_-", "right", 4.4),
             ("12V_IN", "top", 1.5), ("PUMP+", "bottom", 1.6), ("PUMP-", "bottom", 3.6),
             ("GND", "bottom", 5.2)],
            (W_PERF, 9.0)).at((X_PERF, 9.0))
        d += perf
        # the interlock pair drops into a corridor of its own below the DHT block: level
        # with D6/D5 it runs under that block, where its power flag and ground symbol land
        # on these two lines. The drop is a separate wire so each label sits on the long run.
        d += style.wire(_a(uno, "D6"), (23.8, 3.0), "SIGNAL", "-|")
        _route(d, [(23.8, 3.0), (33.4, 3.0), (33.4, 17.0), _a(perf, "PUMP_EN")],
               "SIGNAL", "PUMP_EN", "bottom")
        d += style.wire(_a(uno, "D5"), (23.2, 2.3), "SIGNAL", "-|")
        _route(d, [(23.2, 2.3), (32.8, 2.3), (32.8, 16.2), _a(perf, "FLOAT_OK")],
               "SIGNAL", "FLOAT_OK (HIGH = allow)", "bottom")
        _flag5v(d, _a(perf, "5V_BOARD"), "left", 0.7)
        _gnd(d, _a(perf, "GND"), "down", 0.5)
        d += style.note(["the GND star is on this board:", "brick 12V-, UNO GND, UBEC IN-/OUT-,",
                         "servo brown, breadboard GND rail,", "MOSFET source"],
                        (X_PERF + W_PERF + 0.7, 18.6), net="GND", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- 12 V and the servo rail
        # y so that 12V+ lands exactly on Y_12V: off by a fraction, the run to F1/F2 is
        # drawn as a diagonal.
        brick = style.block_at("12 V brick ≥ 3 A",
                               [("12V+", "left", 1.05), ("12V-", "left", 0.45)],
                               (5.0, 1.5)).at((X_PERF + 4.2, Y_12V - 1.05))
        d += brick
        # the outputs leave sideways: below the UBEC is the flow meter, and a stub down
        # there puts the 5V_SERVO run and its ground inside that block.
        # high enough (with Y_12V) that its lower edge clears the "YF-S401 flow meter" title
        # below: crowded, that title reads as this block's caption.
        ubec = style.block_at("5 V UBEC ≥ 3 A",
                              [("IN+", "top", 1.2), ("IN-", "top", 2.6), ("OUT+", "right", 1.05),
                               ("OUT-", "right", 0.45)],
                              (4.4, 1.5)).at((25.4, 19.7))
        d += ubec
        # brick 12V+ runs west along Y_12V: F1 drops to the perfboard, F2 feeds VIN and the UBEC
        node_f1 = (X_PERF + 1.5, Y_12V)
        d += style.wire(_a(brick, "12V+"), node_f1, "12V", "-")
        d += style.dot(node_f1, "12V")
        d += elm.Fuse().at(node_f1).down(1.3).color(style.colour("12V")).label(
            "F1 T 3 A\npump branch\n(+ leg only)", loc="left", fontsize=style.FS_PIN,
            color=style.colour("12V"))
        d += style.wire((node_f1[0], Y_12V - 1.3), _a(perf, "12V_IN"), "12V", "|-")
        seg = elm.Line().at(node_f1).left(2.4).color(style.colour("12V"))
        d += seg
        fuse2 = elm.Fuse().at(seg.end).left(1.4).color(style.colour("12V")).label(
            "F2 1 A", loc="top", fontsize=style.FS_PIN, color=style.colour("12V"))
        d += fuse2
        x_ubec_in = _a(ubec, "IN+")[0]
        d += style.wire(fuse2.end, (x_ubec_in, Y_12V), "12V", "-")
        d += style.dot((x_ubec_in, Y_12V), "12V")
        d += style.wire((x_ubec_in, Y_12V), _a(ubec, "IN+"), "12V", "-")
        d += style.wire((x_ubec_in, Y_12V), (_a(uno, "VIN")[0], Y_12V), "12V", "-",
                        label="12V → VIN (or USB-C on the bench)")
        d += style.wire((_a(uno, "VIN")[0], Y_12V), _a(uno, "VIN"), "12V", "-")
        _gnd(d, _a(brick, "12V-"), "left", 0.6)
        _gnd(d, _a(ubec, "IN-"), "up", 0.45)
        _gnd(d, _a(ubec, "OUT-"), "right", 0.7)
        # UBEC out: east above the flow meter, then down the outside of the manifold
        # column, into the servo's red lead and nothing else
        servo_red = _a(servo, "red")
        out_plus = _a(ubec, "OUT+")
        _route(d, [out_plus, (31.6, out_plus[1]), (31.6, servo_red[1]), servo_red],
               "5V_SERVO", None)
        d += style.note("5V_SERVO from the UBEC: the servo's red lead and nothing else",
                        (X_RIGHT, 1.4), net="5V_SERVO", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- pump and float wires
        d += style.wire(_a(perf, "PUMP+"), (_a(perf, "PUMP+")[0], -2.7), "12V", "-",
                        label="PUMP+", loc="left")
        d += style.wire(_a(perf, "PUMP-"), (_a(perf, "PUMP-")[0], -2.7), "PUMP_SW", "-",
                        label="PUMP- (switched return\nthrough the MOSFET, NOT GND)", loc="right")
        for pin, net, x in (("FLT_S", "SIGNAL", 43.6), ("FLT_+", "5V_BOARD", 44.2),
                            ("FLT_-", "GND", 44.8)):
            anchor = _a(perf, pin)
            _route(d, [anchor, (x, anchor[1]), (x, -1.4)], net)
        d += style.note(["float hall at the reservoir:", "S / + / - back to the perfboard"],
                        (43.2, 8.2), net="SIGNAL", fontsize=style.FS_PIN, halign="right")

        # ---------------------------------------------------------------- hydraulic strip
        x0, x1 = X_STRIP
        y0, y1 = Y_STRIP
        d += style.frame((x0, y0), x1 - x0, y1 - y0,
                         label="water path (flow ←): reservoir → pump → damper → meter → manifold",
                         net="WATER")

        def wbox(x, w, y, h, lines):
            d.add(style.frame((x, y), w, h, net="WATER"))
            d.add(style.note(lines, (x + 0.2, y + h - 0.2), net="NOTE", fontsize=style.FS_PIN))

        wbox(40.9, 5.0, -6.0, 4.6, ["reservoir 1 L", "ABOVE the pump inlet", "(gravity-primed)",
                                    "float + magnet inside;", "hall outside at the TOP",
                                    "stop, float keyed"])
        wbox(35.0, 4.2, -4.7, 1.9, ["pump", "12 V diaphragm"])
        wbox(29.2, 3.6, -5.3, 3.1, ["flow meter", "VERTICAL, flow UP,", "tilt ≤ 5°",
                                    "no pulses below its", "flow floor (read the", "label)"])
        wbox(23.0, 4.6, -4.7, 1.9, ["manifold", "5 ball gates"])
        for xa, xb, lbl in ((40.9, 39.2, ""), (35.0, 32.9, "30-50 cm soft silicone\n(pulsation damper)"),
                            (29.2, 27.6, "")):
            d += elm.Line().at((xa, -3.7)).to((xb, -3.7)).color(style.colour("WATER"))
            d += elm.Arrowhead().at((xb, -3.7)).theta(180).color(style.colour("WATER"))
            if lbl:
                d += style.note(lbl, ((xa + xb) / 2, -3.9), net="WATER", fontsize=style.FS_PIN,
                                halign="center")
        _route(d, [(32.9, -3.7), (30.9, -3.7), (30.9, -5.3)], "WATER")
        for i in range(5):
            d += elm.Line().at((23.4 + i * 0.9, -4.7)).down(0.8).color(style.colour("WATER"))
        d += style.note(["outlets 1-5 → pots", "(the bucket on the bench)"], (23.0, -5.6),
                        net="WATER", fontsize=style.FS_PIN)

        # ---------------------------------------------------------------- legend and notes
        style.legend(d, (0.5, -0.9),
                     ("12V", "5V_BOARD", "5V_SERVO", "GND", "SIGNAL", "I2C", "PUMP_SW", "WATER"))
        notes = [
            "Power is drawn as flags, not as a net of lines: an orange stub with an open dot means the",
            "5V_BOARD rail (fed by the UNO 5 V pin), and every ground symbol is the same node - the star",
            "on the perfboard. Every wire, with its connector, colour and length, is in the pin map in",
            "README.md; the driver's own parts are in pump-driver.png, the mux and expander detail in",
            "sensor-bus.png, the rails and fuses in power.png.",
            "",
            "Never: the UBEC output on the UNO 5 V pin. 12 V on the flow meter (its pulses swing to its",
            "own supply). The pump's return through the board's GND pin. PUMP_EN or the servo on the",
            "I2C expander (its pins power up HIGH).",
            "",
            "Series and pull parts, all on the board side: 1 k in D2 (the flow pulse), a 10 k pull-up to",
            "5V_BOARD on each hall's S line, a 10 k pull-down on D6 and a 100 k pull-up on FLT_S at the",
            "perfboard, 100 nF across each module's VCC and GND. Values and positions: README.md.",
            "",
            "MUX1 C6-C15 are open: pots 6-15 of the next manifolds. Manifold 2 and 3 take D10-D13 and",
            "A1-A3, MUX2's SIG goes to A1 and its EN to P5, the four select lines are shared - README.md.",
        ]
        d += style.note(notes, (6.6, -0.9), fontsize=style.FS_PIN)
        bench = len([w for w in nets.WIRES if not w.later])
        later = len(nets.WIRES) - bench
        d += style.note(f"{bench} wires on this bench, {later} more when the second mux and manifold arrive.",
                        (6.6, -3.9), fontsize=style.FS_PIN)

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
