"""Drawing 2: the pump driver and interlock perfboard, component level.

Everything inside the frame is soldered on one perfboard: the 12 V pump loop
(D1, Q1) on screw terminals in >= 0.5 mm2 wire, with F1 upstream in the brick
lead, and the 74HC00 interlock
(G1 inverter on the float line with R4, G2 = NAND(PUMP_EN, FLOAT_OK), G3
inverter into the gate through R1, G4 parked on GND). Values and roles come
from nets.INTERLOCK_PARTS / nets.GATES; the terminal names from
nets.PERFBOARD_TERMINALS. Facts: wiring brief 2026-09-02, DECISIONS #7.

Label text must not contain "<" or "&": schemdraw's bbox estimator parses
labels as XML. Use the arrows / "≤" below.
"""

from __future__ import annotations

from pathlib import Path

from schemdraw import elements as elm
from schemdraw import logic

import nets
import style

STEM = "pump-driver"
TITLE = "Plant Butler bench: pump driver and interlock perfboard (component level)"

# ---------------------------------------------------------------- geometry
X_L = 2.0  # left frame edge: terminals to the UNO / float hall / 5 V sit on it
X_R = 21.4  # right frame edge: pump and star terminals
EXT = 4.5  # length of the stub wire outside a terminal (left side)
EXT_F1 = 7.4  # the 12V_IN stub: longer, F1 sits on it
EXT_R = 3.2  # right side (pump leads)
Y_12V = 11.0  # PUMP+ row
Y_PUMPM = 9.0  # PUMP- row (switched return)
Y_EN = 8.5  # PUMP_EN row = G2 in1
Y_G23 = 8.25  # G2 / G3 axis (in1 = +0.25, in2 = -0.25)
Y_FLT = 6.4  # FLT_S row = G1 axis
Y_FLTP = 5.2  # FLT_+ terminal
Y_FLTM = 4.65  # FLT_- terminal
Y_RAIL = 4.0  # 5V_BOARD rail
Y_FOK = 1.6  # FLOAT_OK return to D5
Y_STAR = 1.0  # GND star
X_R3 = 3.2  # R3 pull-down and the FLT_+ drop
X_R4 = 4.0  # R4 pull-up
X_G1, X_G2, X_G3 = 5.6, 9.0, 11.8  # gate input-side x
X_Q1 = 17.0  # Q1 drain / source x
X_D1 = 18.4  # flyback diode x

_PART = {p["ref"]: p for p in nets.INTERLOCK_PARTS}
_GATE = {g["gate"]: g for g in nets.GATES}
_TERM = {t["terminal"]: t for t in nets.PERFBOARD_TERMINALS}
_ROLE = {"G1": "inverter", "G2": "NAND", "G3": "inverter", "G4": "unused"}


def _gate(xy, gid: str) -> logic.Nand:
    """One 74HC00 gate, facing right, labelled with its DIP pins and role."""
    a, b, y = _GATE[gid]["pins"]
    return logic.Nand().at(xy).theta(0).color(style.colour("SIGNAL")).label(
        f"{gid}  {a},{b}→{y}  {_ROLE[gid]}", loc="top", fontsize=style.FS_PIN,
        color=style.colour("SIGNAL"))


def _tie(d, x: float, gate: logic.Nand, net: str = "SIGNAL") -> None:
    """Join both inputs of `gate` to the wire arriving at (x, gate axis)."""
    d += elm.Dot(radius=0.08).at((x, (gate.in1.y + gate.in2.y) / 2)).color(style.colour(net))
    d += style.line("up", 0.25, net).at((x, (gate.in1.y + gate.in2.y) / 2))
    d += style.line("down", 0.25, net).at((x, (gate.in1.y + gate.in2.y) / 2))
    d += style.line("right", gate.in1.x - x, net).at((x, gate.in1.y))
    d += style.line("right", gate.in2.x - x, net).at((x, gate.in2.y))


def _terminal(d, xy, name: str, side: str, ext_label: str, net: str, below: str | None = None,
              ext_len: float = EXT, name_below: bool = False) -> None:
    """A screw terminal on the frame edge: a small square, its name inside the frame
    (above the wire, or below it), a stub wire outwards with what lands on it written
    above it (and `below` under it)."""
    x, y = xy
    c = style.colour(net)
    d += elm.Rect(corner1=(x - 0.14, y - 0.14), corner2=(x + 0.14, y + 0.14),
                  fill="white", lw=1.4).at((0, 0)).theta(0).color(c)
    y_name = y - 0.17 if name_below else y + 0.3
    if side == "left":
        d += style.line("left", ext_len, net).at((x - 0.14, y))
        d += style.note(ext_label, (x - 0.14 - ext_len, y + 0.36), net=net, fontsize=style.FS_BODY)
        d += style.note(name, (x + 0.22, y_name), net=net, fontsize=style.FS_PIN)
        if below:
            d += style.note(below, (x - 0.14 - ext_len, y - 0.1), net=net, fontsize=style.FS_PIN)
    else:
        d += style.line("right", ext_len, net).at((x + 0.14, y))
        d += style.note(ext_label, (x + 0.3, y + 0.36), net=net, fontsize=style.FS_BODY)
        d += style.note(name, (x - 0.22, y_name), net=net, fontsize=style.FS_PIN, halign="right")
        if below:
            d += style.note(below, (x + 0.3, y - 0.1), net=net, fontsize=style.FS_PIN)


def _dot(d, xy, net: str) -> None:
    d += elm.Dot(radius=0.08).at(xy).color(style.colour(net))


def _gnd(d, xy) -> None:
    """Ground symbol: every one of these is the perfboard star (see the U1 note)."""
    d += elm.Ground().at(xy).theta(0).color(style.colour("GND"))


def build() -> tuple[Path, Path]:
    blue = style.colour("SIGNAL")
    black = style.colour("GND")
    red = style.colour("12V")
    orange = style.colour("5V_BOARD")

    with style.drawing() as d:
        d += style.frame((X_L, 0.2), X_R - X_L, 11.8,
                         label="perfboard: soldered, screw terminals; 12 V loop in >= 0.5 mm2 (never breadboard / Dupont)")

        # ------------------------------------------------ 12 V pump loop (top)
        # F1 is in the brick lead, upstream of the terminal (nets.py: BRICK 12V+ ->
        # PERFBOARD 12V_IN via F1), so the >= 0.5 mm2 run is fused too.
        _terminal(d, (X_L, Y_12V), _TERM["12V_IN"]["terminal"], "left", "brick 12V+ via F1", "12V",
                  name_below=True, ext_len=EXT_F1, below=">= 0.5 mm2")
        d += elm.Fuse().at((X_L - 0.14 - EXT_F1 + 2.9, Y_12V)).right(2.0).color(red).label(
            "F1 T 3 A slow-blow\n+ leg only, in the brick lead", loc="bottom",
            fontsize=style.FS_PIN, color=red)
        d += style.line("right", X_D1 - X_L, "12V", label="PUMP+  12 V", loc="top").at((X_L, Y_12V))
        _dot(d, (X_D1, Y_12V), "12V")
        d += style.line("right", X_R - X_D1, "12V").at((X_D1, Y_12V))
        _terminal(d, (X_R, Y_12V), "PUMP+", "right", ">= 0.5 mm2", "12V", ext_len=EXT_R)

        # flyback diode across the pump terminals, cathode (stripe) to PUMP+
        d += elm.Schottky().at((X_D1, Y_PUMPM)).up(Y_12V - Y_PUMPM).color(red).label(
            f"D1 {_PART['D1']['value']}\nstripe (cathode)\nup = PUMP+", loc="bottom",
            fontsize=style.FS_PIN, color=red, halign="left")

        # Q1: logic-level N-MOSFET, low side. drain = PUMP-, source = star, gate = R1
        q1 = elm.NFet().at((X_Q1, Y_PUMPM)).theta(0).reverse().color(black)
        d += q1
        d += style.note("D", (X_Q1 + 0.12, Y_PUMPM + 0.4), fontsize=style.FS_PIN)
        d += style.note("S", (X_Q1 + 0.12, Y_PUMPM - 1.2), fontsize=style.FS_PIN)
        d += style.note("G", (X_Q1 - 1.3, Y_PUMPM - 0.4), fontsize=style.FS_PIN)
        d += style.note("Q1", (X_Q1 + 0.35, Y_PUMPM - 0.5), fontsize=style.FS_BODY, net="GND")

        # PUMP- row: drain -> D1 anode node -> PUMP- terminal (switched return, not GND)
        d += style.line("right", X_D1 - X_Q1, "PUMP_SW").at((X_Q1, Y_PUMPM))
        _dot(d, (X_D1, Y_PUMPM), "PUMP_SW")
        d += style.line("right", X_R - X_D1, "PUMP_SW").at((X_D1, Y_PUMPM))
        _terminal(d, (X_R, Y_PUMPM), "PUMP-", "right", ">= 0.5 mm2", "PUMP_SW", ext_len=EXT_R,
                  below="switched return\nvia Q1, NOT GND")

        # source -> star
        d += style.line("down", (Y_PUMPM - 1.5) - Y_STAR, "GND").at((X_Q1, Y_PUMPM - 1.5))
        d += elm.Dot(radius=0.16).at((X_Q1, Y_STAR)).color(black)
        d += style.note("GND star", (X_Q1 - 0.4, Y_STAR - 0.2), net="GND", halign="right")
        d += style.line("right", X_R - X_Q1, "GND").at((X_Q1, Y_STAR))
        _terminal(d, (X_R, Y_STAR), "GND", "right", "star: brick 12V-, UNO GND,", "GND", ext_len=1.4,
                  below="UBEC IN- and OUT-, servo brown,\nbreadboard GND rail\n(12 V returns >= 0.5 mm2)")

        # gate node: R1 from G3 arrives here, R2 pull-down to GND
        node_g = q1.gate.x - 0.35
        d += style.line("right", 0.35, "SIGNAL").at((node_g, Y_G23))
        _dot(d, (node_g, Y_G23), "SIGNAL")
        d += elm.Resistor().at((node_g, Y_G23)).down(1.5).color(black).label(
            f"R2 {_PART['R2']['value']}\npull-down", loc="bottom", fontsize=style.FS_PIN,
            color=black, halign="left")
        _gnd(d, (node_g, Y_G23 - 1.5))

        # ------------------------------------------------ the 74HC00 interlock
        g3 = _gate((X_G3, Y_G23), "G3")
        d += g3
        d += elm.Resistor().at(g3.out).to((node_g, Y_G23)).color(blue).label(
            f"R1 {_PART['R1']['value']}", loc="top", fontsize=style.FS_BODY, color=blue)

        g2 = _gate((X_G2, Y_G23), "G2")
        d += g2
        d += style.line("right", 0.35, "SIGNAL").at(g2.out)
        _tie(d, g2.out.x + 0.35, g3)

        # PUMP_EN from D6 -> G2 in1, R3 pull-down
        _terminal(d, (X_L, Y_EN), _TERM["PUMP_EN"]["terminal"], "left", "PUMP_EN  ← UNO D6", "SIGNAL")
        d += style.line("right", g2.in1.x - X_L, "SIGNAL").at((X_L, Y_EN))
        d += style.note("R3: LOW at reset / boot / floating", (X_R3 + 0.4, Y_EN + 0.4), net="SIGNAL",
                        fontsize=style.FS_PIN)
        _dot(d, (X_R3, Y_EN), "SIGNAL")
        d += elm.Resistor().at((X_R3, Y_EN)).down(1.1).color(black).label(
            f"R3 {_PART['R3']['value']}\npull-down", loc="bottom", fontsize=style.FS_PIN,
            color=black, halign="left")
        _gnd(d, (X_R3, Y_EN - 1.1))

        # G1: inverter on the float line; out = FLOAT_OK -> G2 in2 and D5
        g1 = _gate((X_G1, Y_FLT), "G1")
        d += g1
        _terminal(d, (X_L, Y_FLT), _TERM["FLT_S"]["terminal"], "left", "float hall S", "SIGNAL",
                  below="LOW = magnet at hall = allow\nHIGH = block")
        d += style.line("right", (X_G1 - 0.5) - X_L, "SIGNAL").at((X_L, Y_FLT))
        _dot(d, (X_R4, Y_FLT), "SIGNAL")
        _tie(d, X_G1 - 0.5, g1)

        # R4 100 k pull-up from FLT_S to 5V_BOARD: unplugged = HIGH = block
        d += elm.Resistor().at((X_R4, Y_FLT)).down(Y_FLT - Y_RAIL).color(orange).label(
            f"R4 {_PART['R4']['value']}\npull-up", loc="bottom", fontsize=style.FS_PIN,
            color=orange, halign="left")

        # FLOAT_OK node: G1 out -> up to G2 in2, down to the D5 terminal
        fx = g1.out.x + 0.35
        d += style.line("right", 0.35, "SIGNAL").at(g1.out)
        _dot(d, (fx, Y_FLT), "SIGNAL")
        d += style.line("up", g2.in2.y - Y_FLT, "SIGNAL").at((fx, Y_FLT))
        d += style.line("right", g2.in2.x - fx, "SIGNAL").at((fx, g2.in2.y))
        d += style.line("down", Y_FLT - Y_FOK, "SIGNAL").at((fx, Y_FLT))
        d += style.note("FLOAT_OK", (fx + 0.15, Y_FLT + 0.36), net="SIGNAL")
        d += style.line("left", fx - X_L, "SIGNAL").at((fx, Y_FOK))
        d += style.note("G1 out; HIGH = allow", (X_R4 + 0.3, Y_FOK + 0.4), net="SIGNAL", fontsize=style.FS_PIN)
        _terminal(d, (X_L, Y_FOK), _TERM["FLOAT_OK"]["terminal"], "left", "FLOAT_OK  → UNO D5", "SIGNAL")

        # G4: unused, inputs to GND, output open
        g4 = _gate((X_G3, 5.3), "G4")
        d += g4
        d += style.line("left", 0.4, "GND").at(g4.in1)
        d += style.line("left", 0.4, "GND").at(g4.in2)
        d += style.line("down", g4.in1.y - g4.in2.y, "GND").at((g4.in1.x - 0.4, g4.in1.y))
        _gnd(d, (g4.in1.x - 0.4, g4.in2.y))
        d += style.note("inputs to GND\nout n/c", (g4.out.x + 0.2, 5.6), net="SIGNAL", fontsize=style.FS_PIN)

        # ------------------------------------------------ 5V_BOARD rail, C1, float plug + / -
        x_c1 = X_G1 + 0.6
        _terminal(d, (X_L, Y_RAIL), _TERM["5V_BOARD"]["terminal"], "left", "5V_BOARD  ← UNO 5 V pin",
                  "5V_BOARD", name_below=True)
        d += style.line("right", x_c1 - X_L, "5V_BOARD").at((X_L, Y_RAIL))
        _dot(d, (X_R3, Y_RAIL), "5V_BOARD")
        _dot(d, (X_R4, Y_RAIL), "5V_BOARD")
        d += elm.Capacitor().at((x_c1, Y_RAIL)).down(0.9).color(black).label(
            f"C1 {_PART['C1']['value']}\npins 14-7", loc="bottom", fontsize=style.FS_PIN,
            color=black, halign="left")
        _gnd(d, (x_c1, Y_RAIL - 0.9))
        d += style.note("U1 pin 14 (VCC)", (X_R4 + 0.3, Y_RAIL + 0.42), net="5V_BOARD", fontsize=style.FS_PIN)

        _terminal(d, (X_L, Y_FLTP), _TERM["FLT_+"]["terminal"], "left", "float hall + (middle pin)", "5V_BOARD")
        d += style.line("right", X_R3 - X_L, "5V_BOARD").at((X_L, Y_FLTP))
        d += style.line("down", Y_FLTP - Y_RAIL, "5V_BOARD").at((X_R3, Y_FLTP))
        _terminal(d, (X_L, Y_FLTM), _TERM["FLT_-"]["terminal"], "left", "float hall -", "GND")
        d += style.line("right", 0.6, "GND").at((X_L, Y_FLTM))
        _gnd(d, (X_L + 0.6, Y_FLTM))

        # ------------------------------------------------ notes
        d += style.note([
            "U1 74HC00 quad NAND, DIP-14",
            "pin 14 VCC = 5V_BOARD (C1), pin 7 GND = star",
            "every ground symbol on this board = the star",
        ], (X_G2 + 0.6, 3.4))
        d += style.note([
            "Q1: logic-level N-MOSFET module, low side.",
            "AO3400 / IRLZ44N / D4184 ok; an IRF520 is",
            "NOT logic level at 5 V. Module terminals:",
            "G ← R1, D = PUMP-, S = star. Meter: own",
            "gate pull-down? R2 is fitted regardless.",
            "Relay module instead: H/L jumper to H, or",
            "an NPN inverter, so logic LOW = relay off.",
        ], (X_R + 0.3, 7.2), fontsize=style.FS_PIN)

        # pump, outside the perfboard
        d += elm.Rect(corner1=(X_R + EXT_R + 0.15, Y_PUMPM - 0.7), corner2=(X_R + EXT_R + 4.0, Y_12V + 0.7),
                      lw=1.2).at((0, 0)).theta(0).color(style.colour("NOTE"))
        d += style.note(["PUMP  12 V diaphragm", "ASSUME ≤ 1.5 A running,", "3-5x inrush", "(read the label)"],
                        (X_R + EXT_R + 0.35, Y_12V + 0.5), fontsize=style.FS_PIN)

        # interlock summary under the frame
        d += style.note([
            "Runs ONLY when PUMP_EN is HIGH AND the magnet is at the float hall (FLT_S LOW) AND the hall is plugged",
            "and powered AND 5V_BOARD is up (U1 powered). MCU in reset / boot, D6 floating or the jumper pulled,",
            "float unplugged, its GND or VCC lead off, no magnet, tank lifted, board 5 V gone: pump OFF. Fails dry.",
        ], (X_L + 2.2, -0.3), fontsize=style.FS_PIN)
        style.legend(d, (X_L - EXT - 0.1, -0.4), ("12V", "PUMP_SW", "5V_BOARD", "GND", "SIGNAL"))

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
