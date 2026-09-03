"""Drawing 3: the sensor bus — CD74HC4067 mux and PCF8575 expander in detail.

UNO Wire (A4/A5, 5 V) -> PCF8575 0x20; its P0-P3 drive the mux select lines
(drawn as a 4-wire bus) and P4 reads the manifold's home hall back IN, which
is why the expander earns its place: a level can cross I2C, a counted pulse
train cannot. MUX1 SIG -> A0; EN tied to GND; every module VCC from the
5V_BOARD rail with 100 nF. MUX2 (later) dashed: shares S0-S3, EN from P6,
SIG -> A1. Both screens hang off the same SDA/SCL pair and are named in the
I2C address table rather than drawn: they are consumers of this bus, not part
of the sensing path. The channel table, expander pin table and I2C addresses
are printed beside the blocks from nets.py. Label text must not contain "<"
or "&" (schemdraw parses labels as XML): arrows / "≤" instead.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from schemdraw import elements as elm

import nets
import style

STEM = "sensor-bus"
TITLE = "Plant Butler bench: sensor bus (CD74HC4067 mux + PCF8575 expander)"

# ---------------------------------------------------------------- geometry
X_UNO = 0.0  # UNO body left edge
W_UNO, H_UNO = 4.0, 8.0
Y_UNO = 7.5  # UNO body bottom
X_PCF_R = 13.8  # PCF right-side stub ends here (body spans X_PCF_R - 0.5 - W_PCF .. X_PCF_R - 0.5)
W_PCF, H_PCF = 4.6, 7.0
X_MUX = 18.8  # mux left-side stub ends here (body starts 0.5 further right)
W_MUX, H_MUX1, H_MUX2 = 4.4, 5.0, 2.6
Y_S0 = 14.5  # MUX1 S0 and PCF P0: the select bus rows
Y_MUX2_TOP = 7.7
X_TAB = 27.4  # tables column


def _ic(label: str, pins, size, later: bool = False) -> elm.Ic:
    """An Ic with its name inside.

    pins = (name, side, z[, outside label]); z is the pin's offset along the side
    in drawing units from the body's bottom (left/right sides) or left edge
    (top/bottom sides). schemdraw centres the pin group and takes `pos` as a
    fraction of (n-1)*pinspacing, so pos is computed from z here; a side with
    one pin is centred whatever z says.
    """
    w, h = size
    counts: dict[str, int] = {}
    for p in pins:
        counts[p[1]] = counts.get(p[1], 0) + 1
    icpins = []
    for p in pins:
        name, side, z = p[0], p[1], p[2]
        n = counts[side]
        length = w if side in ("top", "bottom") else h
        span = (n - 1) * style.PINSPACING
        pad = (length - span) / 2
        pos = (z - pad) / span if span else None
        if pos == 0:
            pos = 1e-6
        icpins.append(elm.IcPin(name=name, side=side, pos=pos, pin=(p[3] if len(p) > 3 else None)))
    ic = elm.Ic(pins=icpins, size=size, pinspacing=style.PINSPACING, edgepadW=style.EDGEPAD,
                edgepadH=style.EDGEPAD, leadlen=style.LEADLEN, lsize=style.FS_BODY, plblsize=style.FS_PIN)
    ic.theta(0)
    ic.label(label, loc="center", fontsize=style.FS_BODY,
             color=style.colour("NOTE") if later else "black")
    if later:
        ic.linestyle(style.LATER_LS).color(style.colour("NOTE"))
    return ic


def _dot(d, xy, net: str = "SIGNAL", open_: bool = False) -> None:
    d += elm.Dot(radius=0.08, open=open_).at(xy).color(style.colour(net))


def _gnd(d, xy, later: bool = False) -> None:
    g = elm.Ground().at(xy).theta(0).color(style.colour("NOTE" if later else "GND"))
    if later:
        g.linestyle(style.LATER_LS)
    d += g


def _power(d, ic: elm.Ic, later: bool = False) -> None:
    """VCC and GND on the bottom side: 5V_BOARD tag, 100 nF across, ground symbol."""
    v, g = ic.VCC, ic.GND
    y_node = v.y - 0.5
    d += style.line("down", 0.5, "5V_BOARD", later=later).at(v)
    _dot(d, (v.x, y_node), "5V_BOARD")
    d += style.line("down", 0.45, "5V_BOARD", later=later).at((v.x, y_node))
    _dot(d, (v.x, y_node - 0.45), "5V_BOARD", open_=True)
    d += style.note("5V_BOARD", (v.x - 0.2, y_node - 0.35), net="5V_BOARD", fontsize=style.FS_PIN, halign="right")
    d += style.line("down", 0.5, "GND", later=later).at(g)
    _dot(d, (g.x, y_node), "GND")
    cap = elm.Capacitor().at((v.x, y_node)).to((g.x, y_node)).color(style.colour("GND")).label(
        "100 nF", loc="bottom", fontsize=style.FS_PIN, color=style.colour("GND"))
    if later:
        cap.linestyle(style.LATER_LS)
    d += cap
    d += style.line("down", 0.35, "GND", later=later).at((g.x, y_node))
    _gnd(d, (g.x, y_node - 0.35), later=later)


def build() -> tuple[Path, Path]:
    green = style.colour("I2C")
    grey = style.colour("NOTE")

    with style.drawing() as d:
        # ------------------------------------------------ blocks
        pcf = _ic("PCF8575\n0x20", [
            ("SCL", "left", 6.4), ("SDA", "left", 4.2), ("A0", "left", 3.0), ("A1", "left", 2.4),
            ("A2", "left", 1.8), ("INT", "left", 0.9, "n/c"),
            ("P0", "right", 6.5), ("P1", "right", 5.9), ("P2", "right", 5.3), ("P3", "right", 4.7),
            ("P4", "right", 4.1), ("P5", "right", 3.5, "spare"), ("P6", "right", 2.9),
            ("P7", "right", 2.3, "spare"), ("P8-15", "right", 1.7, "next home halls"),
            ("VCC", "bottom", 1.4), ("GND", "bottom", 2.9),
        ], size=(W_PCF, H_PCF)).at((X_PCF_R, Y_S0)).anchor("P0")
        d += pcf

        mux1 = _ic("CD74HC4067\nMUX1", [
            ("S0", "left", 4.3), ("S1", "left", 3.7), ("S2", "left", 3.1), ("S3", "left", 2.5),
            ("EN", "left", 1.3),
            ("C0", "right", 4.4, "moisture 1 AOUT"), ("C1", "right", 3.8, "moisture 2 AOUT"),
            ("C2", "right", 3.2, "moisture 3 AOUT"), ("C3", "right", 2.6, "moisture 4 AOUT"),
            ("C4", "right", 2.0, "moisture 5 AOUT"), ("C5", "right", 1.4, "LDR SIG"),
            ("C6-15", "right", 0.6, "open"),
            ("SIG", "top", 2.2), ("VCC", "bottom", 1.3), ("GND", "bottom", 2.7),
        ], size=(W_MUX, H_MUX1)).at((X_MUX, Y_S0)).anchor("S0")
        d += mux1

        mux2 = _ic("CD74HC4067\nMUX2 (later)", [
            ("S0-S3", "left", 1.9), ("EN", "left", 0.7),
            ("C0-15", "right", 1.3, "open (later pots)"),
            ("SIG", "bottom", 3.6), ("VCC", "bottom", 1.3), ("GND", "bottom", 2.7),
        ], size=(W_MUX, H_MUX2), later=True).at((X_MUX, Y_MUX2_TOP - H_MUX2 + 1.9)).anchor("S0-S3")
        d += mux2

        # UNO: A5 / 5V / A4 face the PCF's SCL / the rail / SDA; A0, A1 on the left; GND below
        y_scl, y_sda = pcf.SCL.y, pcf.SDA.y
        y_5v = (y_scl + y_sda) / 2
        uno = _ic("Arduino UNO\nR4 WiFi", [
            ("A5", "right", y_scl - Y_UNO), ("5V", "right", y_5v - Y_UNO), ("A4", "right", y_sda - Y_UNO),
            ("A0", "left", 7.2), ("A1", "left", 1.0), ("GND", "bottom", 2.0),
        ], size=(W_UNO, H_UNO)).at((X_UNO + W_UNO / 2, Y_UNO + H_UNO / 2)).anchor("center")
        d += uno

        # ------------------------------------------------ I2C + 5V_BOARD between UNO and PCF
        d += style.note(["the same two wires also carry the two screens:",
                         "OLED 0x3C and the LCD1602 backpack 0x27"],
                        (uno.A5.x + 0.4, y_scl + 1.5), net="I2C", fontsize=style.FS_PIN)
        d += style.wire(uno.A5, pcf.SCL, "I2C", "-", label="SCL", loc="top")
        d += style.wire(uno.A4, pcf.SDA, "I2C", "-", label="SDA", loc="top")
        x_5v = uno["5V"].x
        x_pu = x_5v + 0.7  # pull-ups (on the module) between the two I2C lines
        x_tag = x_5v + 2.4
        d += style.line("right", x_tag - x_5v, "5V_BOARD").at(uno["5V"])
        _dot(d, (x_tag, y_5v), "5V_BOARD", open_=True)
        d += style.note("5V_BOARD (rail)", (x_tag + 0.2, y_5v + 0.25), net="5V_BOARD", fontsize=style.FS_PIN)
        _dot(d, (x_pu, y_scl), "I2C")
        _dot(d, (x_pu, y_5v), "5V_BOARD")
        _dot(d, (x_pu, y_sda), "I2C")
        for y0, y1 in ((y_scl, y_5v), (y_5v, y_sda)):
            d += elm.Resistor().at((x_pu, y0)).to((x_pu, y1)).color(green).label(
                "4.7 k", loc="top", fontsize=style.FS_PIN, color=green)
        d += style.note("ONE set for the whole bus:\nVERIFY all three modules\n(see the I2C notes below)",
                        (x_pu - 1.0, y_sda - 0.3), fontsize=style.FS_PIN)

        # PCF address pins A0-A2 to GND -> 0x20; INT open
        x_tie = pcf.A0.x - 0.5
        for a in (pcf.A0, pcf.A1, pcf.A2):
            d += style.line("left", 0.5, "GND").at(a)
        d += style.line("down", pcf.A0.y - pcf.A2.y, "GND").at((x_tie, pcf.A0.y))
        _dot(d, (x_tie, pcf.A1.y), "GND")
        _gnd(d, (x_tie, pcf.A2.y))
        d += style.note("A0-A2 low\n= 0x20", (x_tie - 0.15, pcf.A1.y + 0.1), net="GND", fontsize=style.FS_PIN,
                        halign="right")

        # ------------------------------------------------ select lines PCF P0-P3 -> MUX1 S0-S3
        # Four INDEPENDENT wires, never one bus node: P0..P3 and S0..S3 sit on the
        # same four rows, so each is a straight run. Shorting any two of them
        # scrambles the channel order and the channel table above stops being true.
        xc = X_PCF_R
        selects = ((pcf.P0, mux1.S0), (pcf.P1, mux1.S1), (pcf.P2, mux1.S2), (pcf.P3, mux1.S3))
        for p, s in selects:
            d += style.wire(p, s, "SIGNAL", "-")
        d += style.note("4 separate select lines:  P0→S0  P1→S1  P2→S2  P3→S3",
                        (xc + 0.2, pcf.P0.y + 1.2), net="SIGNAL", fontsize=style.FS_PIN)

        # later: MUX2 taps each of the four, EN from P5, SIG -> A1. Its "S0-S3" pin is
        # the four mux pins drawn as one, so the last run into it is a 4-wire bundle.
        y_j = mux2["S0-S3"].y
        x_drop = xc + 2.2
        for i, (_, s) in enumerate(selects):
            x = x_drop + 0.3 * i
            _dot(d, (x, s.y), "SIGNAL")
            d += style.wire((x, s.y), (x, y_j), "SIGNAL", "-", later=True)
        d += elm.Line().at((x_drop, y_j)).to(mux2["S0-S3"]).color(grey).linewidth(3.2).linestyle(style.LATER_LS)
        d += style.note("S0-S3: the same 4 wires\ntapped for MUX2 (later)", (x_drop + 1.3, y_j + 2.6),
                        fontsize=style.FS_PIN)
        x_p6 = xc + 1.4
        d += style.line("right", x_p6 - pcf.P6.x, "SIGNAL", later=True).at(pcf.P6)
        d += style.wire((x_p6, pcf.P6.y), (x_p6, mux2.EN.y), "SIGNAL", "-", later=True)
        d += style.wire((x_p6, mux2.EN.y), mux2.EN, "SIGNAL", "-", later=True, label="MUX2_EN ← P6 (later)",
                        loc="bottom")

        # P4 is the one expander pin read as an INPUT: the manifold's home hall lands here.
        # It crosses the dashed MUX2_EN run once, without a dot: not a connection.
        x_p4 = xc + 1.9
        y_p4_end = mux2.EN.y - 1.6
        d += style.line("right", x_p4 - pcf.P4.x, "SIGNAL").at(pcf.P4)
        d += style.wire((x_p4, pcf.P4.y), (x_p4, y_p4_end), "SIGNAL", "-")
        _dot(d, (x_p4, y_p4_end), "SIGNAL", open_=True)
        # Short lines on purpose: a longer one runs into MUX2's 5V_BOARD flag label.
        d += style.note(["HALL_HOME S ← the manifold:", "the one INPUT on this chip.",
                         "10 k pull-up R3;", "write P4 HIGH first"],
                        (x_p4 + 0.25, y_p4_end + 0.15), net="SIGNAL", fontsize=style.FS_PIN)

        # MUX1 EN tied LOW
        d += style.line("left", 0.4, "GND").at(mux1.EN)
        _gnd(d, (mux1.EN.x - 0.4, mux1.EN.y))
        d += style.note("EN → GND", (mux1.EN.x - 0.75, mux1.EN.y + 0.12), net="GND", fontsize=style.FS_PIN,
                        halign="right")

        # ------------------------------------------------ analog: MUX1 SIG -> A0 over the top, MUX2 SIG -> A1 underneath
        y_top = mux1.SIG.y + 0.6
        x_a0 = uno.A0.x - 0.6
        d += style.wire(mux1.SIG, (mux1.SIG.x, y_top), "SIGNAL", "-")
        d += style.wire((mux1.SIG.x, y_top), (x_a0, y_top), "SIGNAL", "-",
                        label="MUX1_SIG → A0  (14-bit; select, wait ≥ 1 ms, read twice, keep the second)", loc="top")
        d += style.wire((x_a0, y_top), (x_a0, uno.A0.y), "SIGNAL", "-")
        d += style.line("right", 0.6, "SIGNAL").at((x_a0, uno.A0.y))

        y_bot = mux2.GND.y - 2.4
        x_a1 = uno.A1.x - 1.0
        d += style.wire(mux2.SIG, (mux2.SIG.x, y_bot), "SIGNAL", "-", later=True)
        d += style.wire((mux2.SIG.x, y_bot), (x_a1, y_bot), "SIGNAL", "-", later=True,
                        label="MUX2_SIG → A1 (later)", loc="top")
        d += style.wire((x_a1, y_bot), (x_a1, uno.A1.y), "SIGNAL", "-", later=True)
        d += style.line("right", 1.0, "SIGNAL", later=True).at((x_a1, uno.A1.y))

        # ------------------------------------------------ power at each module, UNO GND
        _power(d, pcf)
        _power(d, mux1)
        _power(d, mux2, later=True)
        d += style.line("down", 0.4, "GND").at(uno.GND)
        _gnd(d, (uno.GND.x, uno.GND.y - 0.4))
        d += style.note("→ GND star (perfboard)", (uno.GND.x + 0.35, uno.GND.y - 0.2), net="GND",
                        fontsize=style.FS_PIN)
        d += style.note("Wire = A4/A5 at 5 V, no on-board pull-ups.\nQwiic is Wire1 at 3.3 V: not for these.",
                        (x_a1, y_bot + 0.75), fontsize=style.FS_PIN)

        # ------------------------------------------------ tables
        y = y_top + 0.3
        y = style.table_note(d, "MUX1 channels (read on A0)", style.table_lines(nets.MUX_CHANNELS, [
            ("channel", "ch"), ("source", "source"), ("signal", "signal"), ("note", "note")]), (X_TAB, y))
        y = style.table_note(d, "PCF8575 pins (0x20)", style.table_lines(nets.EXPANDER_PINS, [
            ("pin", "pin"), ("use", "use"), ("note", "note")]), (X_TAB, y - 0.5))
        style.table_note(d, "I2C addresses (Wire, 5 V)", style.table_lines(nets.I2C_ADDRESSES, [
            ("address", "addr"), ("device", "device"), ("note", "note")]), (X_TAB, y - 0.5))

        # ------------------------------------------------ notes, legend
        notes = []
        for group, items in (("mux", nets.MUX_NOTES), ("expander", nets.EXPANDER_NOTES), ("I2C", nets.I2C_NOTES)):
            for it in items:
                notes += textwrap.wrap(f"{group}: {it}", 96, subsequent_indent="   ")
        d += style.note(notes, (X_UNO + 2.2, y_bot - 0.6), fontsize=style.FS_PIN)
        style.legend(d, (x_a1, y_bot - 0.6), ("5V_BOARD", "GND", "SIGNAL", "I2C", "LATER"))

        d += style.title(d, TITLE)
        return style.save(d, STEM)


if __name__ == "__main__":
    print(*build())
