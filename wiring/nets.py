"""One source of truth for the bench wiring: modules, every wire, tables, parts.

The drawings (draw_*.py) and the README (gen_readme.py) are both generated
from this file, so a pin changes here and nowhere else. Facts come from the
wiring brief (2026-09-02) and umbrella DECISIONS.md #5 and #7. Nothing in
here is firmware: the bench command set is a requirement on the bench sketch.

Net names (and their colours, see style.COLOURS): 12V, 5V_BOARD, GND,
SIGNAL, I2C, PUMP_SW (the pump's switched 12 V leg: NOT ground).

Revision 2026-09-03, after the bench feedback: no UBEC (the R4's own buck
feeds the servo), no 74HC00 and no MOSFET (a relay module switches the pump
and the interlock moves into firmware), the home hall moves onto the I2C
expander. See INTERLOCK_NOTES for what that costs.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Iterable, Sequence

DATE = "2026-09-03"

# Physical wire colour per net: what to reach for on the bench.
COLOUR_NAMES: dict[str, str] = {
    "12V": "red",
    "5V_BOARD": "orange",
    "GND": "black",
    "SIGNAL": "blue",
    "I2C": "green",
    "PUMP_SW": "purple",  # or red with purple tape: switched 12 V out of the relay, not GND
}

# ---------------------------------------------------------------- modules
# id -> (name on the drawings, status). Status: in hand | ASSUME (ordered,
# exact model unknown) | bench (rail, star point, perfboard we build).
MODULES: dict[str, tuple[str, str]] = {
    "UNO": ("Arduino UNO R4 WiFi", "in hand"),
    "PCF8575": ("PCF8575 I2C expander 0x20", "in hand"),
    "MUX1": ("CD74HC4067 mux MUX1", "in hand"),
    "MUX2": ("CD74HC4067 mux MUX2 (later)", "later"),
    "MOIST1": ("moisture 1 (capacitive)", "in hand"),
    "MOIST2": ("moisture 2 (capacitive)", "in hand"),
    "MOIST3": ("moisture 3 (capacitive)", "in hand"),
    "MOIST4": ("moisture 4 (capacitive)", "in hand"),
    "MOIST5": ("moisture 5 (capacitive)", "in hand"),
    "LDR": ("Sensor Kit light (LDR)", "in hand"),
    "DHT": ("Sensor Kit temp/humidity (DHT11)", "in hand"),
    "SERVO": ("SG90 continuous servo", "in hand"),
    "HALL_SCREW": ("WPSE313 hall: screw pulse", "in hand"),
    "HALL_HOME": ("WPSE313 hall: home", "in hand"),
    "HALL_FLOAT": ("WPSE313 hall: float (tank)", "in hand"),
    "FLOW": ("YF-S401 flow meter", "ASSUME"),
    "RELAY": ("1-channel relay module K1", "in hand"),
    "PERFBOARD": ("power board: F1, 12 V terminals, GND star", "bench"),
    "PUMP": ("12 V diaphragm pump", "ASSUME"),
    "BRICK": ("12 V >= 3 A brick", "ASSUME"),
    "RAIL5V": ("5V_BOARD rail (breadboard)", "bench"),
    "RAILGND": ("GND rail (breadboard)", "bench"),
    "STAR": ("GND star (power board)", "bench"),
}


def module_name(mid: str) -> str:
    return MODULES[mid][0]


# ---------------------------------------------------------------- wires
@dataclass(frozen=True)
class Wire:
    frm: str  # module id
    frm_pin: str  # silkscreen / lead name at that end
    to: str
    to_pin: str
    net: str  # key of COLOUR_NAMES
    signal: str = ""  # name printed on the wire in the drawings
    via: str = ""  # series or pull part on the way ("1 k series", "10 k pull-up")
    connector: str = ""
    cable: str = ""  # length / routing note
    later: bool = False  # expansion, drawn dashed, not on the bench

    @property
    def board_pin(self) -> str:
        """The UNO pin this wire lands on, or ''."""
        if self.frm == "UNO":
            return self.frm_pin
        if self.to == "UNO":
            return self.to_pin
        return ""

    @property
    def colour(self) -> str:
        return COLOUR_NAMES[self.net]

    def other_end(self, mid: str) -> tuple[str, str]:
        """(module id, pin) at the end that is not `mid`."""
        return (self.to, self.to_pin) if self.frm == mid else (self.frm, self.frm_pin)


_I2C_PULL = "10 k pull-up on the module (VERIFY; else 4.7 k to 5V_BOARD)"
_HALL_CONN = "3-pin S / + (middle) / -"
_HALL_PULL = "10 k pull-up to 5V_BOARD at the breadboard"
_PH = "JST-PH 2.0 3-pin (VCC, GND, AOUT)"
_GROVE = "Grove 4-pin (VCC, GND, SIG, NC)"

WIRES: list[Wire] = [
    # -- UNO pins ------------------------------------------------------------
    Wire("UNO", "D2", "FLOW", "yellow (pulse)", "SIGNAL", "FLOW",
         via="1 k series at the board", connector="3-wire lead red / black / yellow",
         cable="<= 1 m; away from the servo lead; interrupt pin: pulses are counted, never muxed"),
    Wire("UNO", "D3", "HALL_SCREW", "S", "SIGNAL", "HALL_SCREW",
         via=_HALL_PULL, connector=_HALL_CONN,
         cable="<= 50 cm; hall fixed, magnet on the screw; interrupt pin: a missed edge is lost position"),
    Wire("UNO", "D5", "HALL_FLOAT", "S", "SIGNAL", "HALL_FLOAT",
         via="10 k pull-up to 5V_BOARD at the breadboard (R2)",
         connector=_HALL_CONN + " plug: the one pulled in bring-up 5b",
         cable="to the reservoir, <= 1 m; direct pin, NOT the expander: shortest path for the safety input"),
    Wire("UNO", "D6", "RELAY", "IN", "SIGNAL", "PUMP_EN",
         via="10 k to the module's OFF level (R1): pull-down if active-HIGH, pull-up to 5V_BOARD if active-LOW",
         connector="Dupont", cable="<= 30 cm; the jumper pulled in bring-up 4c"),
    Wire("UNO", "D7", "DHT", "SIG", "SIGNAL", "DHT_DATA",
         connector=_GROVE,
         cable="Grove 20-50 cm; direct pin: us-level one-wire timing cannot cross a mux or the expander. "
               "Free if the kit has the DHT20 (I2C)"),
    Wire("UNO", "D9", "SERVO", "orange (signal)", "SIGNAL", "SERVO_PWM",
         connector="JR 3-pin brown / red / orange",
         cable="servo lead ~25 cm; direct pin: a servo needs its 50 Hz train unbroken (PCA9685 to expand)"),
    Wire("UNO", "A0", "MUX1", "SIG", "SIGNAL", "MUX1_SIG",
         connector="header / Dupont", cable="<= 20 cm; analog, 14-bit"),
    Wire("UNO", "A4", "PCF8575", "SDA", "I2C", "SDA", via=_I2C_PULL,
         connector="header / Dupont", cable="<= 20 cm"),
    Wire("UNO", "A5", "PCF8575", "SCL", "I2C", "SCL", via=_I2C_PULL,
         connector="header / Dupont", cable="<= 20 cm"),
    Wire("UNO", "5V", "RAIL5V", "+", "5V_BOARD", "5V_BOARD",
         connector="header / Dupont",
         cable="<= 20 cm; OUTPUT only, never fed. The board's buck gives 1.2 A total from VIN: see POWER_BUDGET"),
    Wire("UNO", "GND", "STAR", "GND", "GND", "GND",
         connector="screw terminal", cable="<= 30 cm; the pump's 12 V return never passes here"),
    Wire("BRICK", "12V+", "UNO", "VIN (barrel)", "12V", "12V",
         via="1 A fuse F2, + leg only", connector="barrel 5.5/2.1 mm, centre +",
         cable="the servo and the relay coil come out of this: do NOT run them on USB power (500 mA port)"),
    # -- 5V_BOARD rail -> modules -------------------------------------------
    Wire("RAIL5V", "+", "MUX1", "VCC", "5V_BOARD", "5V_BOARD", via="100 nF at the module"),
    Wire("RAIL5V", "+", "PCF8575", "VCC", "5V_BOARD", "5V_BOARD", via="100 nF at the module"),
    Wire("RAIL5V", "+", "HALL_SCREW", "+ (middle)", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("RAIL5V", "+", "HALL_HOME", "+ (middle)", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("RAIL5V", "+", "HALL_FLOAT", "+ (middle)", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("RAIL5V", "+", "FLOW", "red", "5V_BOARD", "5V_BOARD",
         cable="5V_BOARD ONLY, never 12 V: the pulses swing to the supply"),
    Wire("RAIL5V", "+", "DHT", "VCC", "5V_BOARD", "5V_BOARD", connector=_GROVE),
    Wire("RAIL5V", "+", "LDR", "VCC", "5V_BOARD", "5V_BOARD", connector=_GROVE),
    *[Wire("RAIL5V", "+", f"MOIST{i}", "VCC", "5V_BOARD", "5V_BOARD", connector=_PH,
           cable="lead + extension <= 1.5 m") for i in range(1, 6)],
    Wire("RAIL5V", "+", "RELAY", "VCC", "5V_BOARD", "5V_BOARD", connector="Dupont",
         cable="coil ~80 mA (VERIFY); if the module has a JD-VCC jumper, leaving it fitted is what puts "
               "the coil on this rail"),
    Wire("RAIL5V", "+", "SERVO", "red", "5V_BOARD", "5V_BOARD", connector="JR 3-pin",
         cable="its OWN pair from the rail's feed point, plus 470-1000 uF and 100 nF AT THE SERVO PLUG: "
               "that cap, not the rail, is what stops a stall dip resetting the board"),
    # -- GND ----------------------------------------------------------------
    Wire("STAR", "GND", "RAILGND", "-", "GND", "GND", cable="one wire, star -> breadboard GND rail"),
    Wire("RAILGND", "-", "MUX1", "GND", "GND", "GND"),
    Wire("RAILGND", "-", "PCF8575", "GND", "GND", "GND"),
    Wire("RAILGND", "-", "HALL_SCREW", "-", "GND", "GND", connector=_HALL_CONN),
    Wire("RAILGND", "-", "HALL_HOME", "-", "GND", "GND", connector=_HALL_CONN),
    Wire("RAILGND", "-", "HALL_FLOAT", "-", "GND", "GND", connector=_HALL_CONN),
    Wire("RAILGND", "-", "FLOW", "black", "GND", "GND"),
    Wire("RAILGND", "-", "DHT", "GND", "GND", "GND", connector=_GROVE),
    Wire("RAILGND", "-", "LDR", "GND", "GND", "GND", connector=_GROVE),
    *[Wire("RAILGND", "-", f"MOIST{i}", "GND", "GND", "GND", connector=_PH) for i in range(1, 6)],
    Wire("RAILGND", "-", "RELAY", "GND", "GND", "GND", connector="Dupont", cable="coil return"),
    Wire("SERVO", "brown", "STAR", "GND", "GND", "GND", connector="JR 3-pin",
         cable="to the star, not the sensor rail: keeps the stall dip out of the ADC ground"),
    Wire("MUX1", "EN", "RAILGND", "-", "GND", "MUX1_EN",
         cable="EN tied LOW: mux always enabled (breakouts may pull EN down with 10 k)"),
    # -- analog into the mux ------------------------------------------------
    *[Wire(f"MOIST{i}", "AOUT", "MUX1", f"C{i - 1}", "SIGNAL", f"MOIST{i}", connector=_PH,
           cable="~10 k source; 0-3 V") for i in range(1, 6)],
    Wire("LDR", "SIG", "MUX1", "C5", "SIGNAL", "LIGHT", connector=_GROVE, cable="0-5 V"),
    # -- expander: mux select out, home hall in ------------------------------
    *[Wire("PCF8575", f"P{i}", "MUX1", f"S{i}", "SIGNAL", f"MUX_S{i}", cable="<= 20 cm")
      for i in range(4)],
    Wire("HALL_HOME", "S", "PCF8575", "P4", "SIGNAL", "HALL_HOME",
         via="10 k pull-up to 5V_BOARD at the breadboard (R3)", connector=_HALL_CONN,
         cable="<= 50 cm; a level, not a pulse train: the expander is fast enough (a 2-byte read is ~0.3 ms). "
               "Write P4 HIGH before reading it (quasi-bidirectional)"),
    # -- 12 V and the pump loop ---------------------------------------------
    Wire("BRICK", "12V+", "PERFBOARD", "12V_IN", "12V", "12V",
         via="T 3 A slow-blow F1, + leg only", connector="screw terminal", cable=">= 0.5 mm2"),
    Wire("PERFBOARD", "12V_OUT", "RELAY", "COM", "12V", "12V",
         connector="screw terminal", cable=">= 0.5 mm2; the relay switches the + leg"),
    Wire("RELAY", "NO", "PUMP", "+", "PUMP_SW", "PUMP+",
         connector="screw terminal", cable=">= 0.5 mm2; NO, not NC: no coil = no pump"),
    Wire("BRICK", "12V-", "STAR", "GND", "GND", "GND", connector="screw terminal", cable=">= 0.5 mm2"),
    Wire("PUMP", "-", "STAR", "GND", "GND", "GND",
         connector="screw terminal", cable=">= 0.5 mm2; straight to the star, never the board's GND pin"),
    # -- later: second mux, next manifolds (dashed) -------------------------
    *[Wire("PCF8575", f"P{i}", "MUX2", f"S{i}", "SIGNAL", f"MUX_S{i}", later=True,
           cable="select lines shared with MUX1") for i in range(4)],
    Wire("PCF8575", "P6", "MUX2", "EN", "SIGNAL", "MUX2_EN", later=True),
    Wire("MUX2", "SIG", "UNO", "A1", "SIGNAL", "MUX2_SIG", later=True),
]

# Board pins not wired on this bench, and what they are earmarked for.
BOARD_PINS_FREE: list[tuple[str, str]] = [
    ("D0 / D1", "serial: keep free"),
    ("D4", "HALL_SCREW manifold 2 (later; freed when the home hall moved to the expander)"),
    ("D8", "free"),
    ("D10", "HALL_SCREW manifold 3 (later)"),
    ("D11", "free"),
    ("D12", "SERVO_PWM manifold 2 (later)"),
    ("D13", "SERVO_PWM manifold 3 (later)"),
    ("A1", "MUX2 SIG (later)"),
    ("A2", "free (analog)"),
    ("A3", "free (analog)"),
]

# Per-manifold pin plan (manifold 1 is the bench; 2 and 3 are later).
MANIFOLD_PINS: list[dict[str, str]] = [
    {"manifold": "1 (bench)", "servo": "D9", "hall_screw": "D3", "hall_home": "P4 (expander)", "mux_sig": "A0 (MUX1)"},
    {"manifold": "2 (later)", "servo": "D12", "hall_screw": "D4", "hall_home": "P8 (expander)", "mux_sig": "A1 (MUX2)"},
    {"manifold": "3 (later)", "servo": "D13", "hall_screw": "D10", "hall_home": "P9 (expander)",
     "mux_sig": "A1 (MUX2, C6-C15)"},
]
MANIFOLD_NOTE = (
    "What scales where, by signal type, not by habit: analog and slow (moisture, light) on the mux, "
    "16 a piece; a level and slow (home hall, and the one float) on the expander or a spare pin; a "
    "counted pulse train (screw hall, flow meter) on an interrupt pin, because a mux is a switch and "
    "an edge missed while it sits on another channel is lost cart position. Past three manifolds, "
    "route the screw halls through a 74HC4051 into one interrupt pin (only one manifold moves at a "
    "time) and the servos onto a PCA9685 (16 channels of hardware PWM over I2C, its own 5 V supply) "
    "rather than spending a board pin each.")


def pin_map() -> list[Wire]:
    """The wires that land on a UNO pin, in board-pin order (bench first, later last)."""
    order = ["D2", "D3", "D5", "D6", "D7", "D9", "A0", "A1", "A4", "A5", "5V", "GND", "VIN (barrel)"]
    rows = [w for w in WIRES if w.board_pin]
    return sorted(rows, key=lambda w: (w.later, order.index(w.board_pin)))


def wires_of(mid: str, include_later: bool = False) -> list[Wire]:
    """Every wire touching module `mid`."""
    return [w for w in WIRES if mid in (w.frm, w.to) and (include_later or not w.later)]


# ---------------------------------------------------------------- tables
MUX_CHANNELS: list[dict[str, str]] = [
    *[{"channel": f"C{i}", "source": f"moisture {i + 1} AOUT", "signal": f"MOIST{i + 1}",
       "note": "raw counts; the backend maps channel -> pot"} for i in range(5)],
    {"channel": "C5", "source": "Sensor Kit LDR SIG", "signal": "LIGHT", "note": "0-5 V"},
    *[{"channel": f"C{i}", "source": "open", "signal": "spare",
       "note": "next manifolds' pots; leave open"} for i in range(6, 16)],
]
MUX_NOTES = [
    "EN tied to GND (always enabled): some breakouts pull EN down with 10 k, which the expander cannot lift.",
    "Firmware: select, wait >= 1 ms, read twice, keep the second (10 k source + ~70 ohm switch into the ADC sample capacitor).",
    "100 nF across VCC/GND at the module.",
]

EXPANDER_PINS: list[dict[str, str]] = [
    *[{"pin": f"P{i}", "use": f"MUX1 S{i}", "note": "shared with MUX2 later"} for i in range(4)],
    {"pin": "P4", "use": "HALL_HOME manifold 1 (INPUT)", "note": "10 k pull-up (R3); write P4 HIGH before reading"},
    {"pin": "P5", "use": "spare", "note": "MUX1 EN is tied to GND on the board"},
    {"pin": "P6", "use": "MUX2 EN (later)", "note": "dashed on the drawing"},
    {"pin": "P7", "use": "spare", "note": ""},
    *[{"pin": f"P{i}", "use": "spare", "note": "manifold 2-3 home halls (input), P8 then P9"} for i in range(8, 16)],
    {"pin": "INT", "use": "not connected", "note": "the home hall is polled; nothing here needs an edge"},
]
EXPANDER_NOTES = [
    "Quasi-bidirectional: pins power up HIGH, source ~100 uA high, sink 25 mA low.",
    "An input pin must be written HIGH before it is read, and it needs a real 10 k pull-up: 100 uA is "
    "too weak to hold a line next to a pump.",
    "NEVER PUMP_EN or the servo on the expander (power-on HIGH would run them).",
    "A failed or timed-out I2C read is not a zero: the firmware must treat it as 'home unknown' and refuse to move or pump.",
    "Address 0x20 with A0-A2 low; 100 nF across VCC/GND.",
]

I2C_ADDRESSES: list[dict[str, str]] = [
    {"address": "0x20", "device": "PCF8575 expander", "note": "A0-A2 low; Wire (A4/A5, 5 V)"},
    {"address": "0x38", "device": "DHT20 temp/humidity", "note": "only if the kit has the DHT20 (Environment_I2C)"},
    {"address": "0x21-0x27", "device": "more PCF8575", "note": "later manifolds"},
]
I2C_NOTES = [
    "Wire on A4/A5 is 5 V with NO on-board pull-ups: the PCF8575 module's 10 k pull-ups serve (VERIFY, else 4.7 k to 5V_BOARD).",
    "The Qwiic connector is Wire1 at 3.3 V: not for these modules.",
]

# ---------------------------------------------------------------- perfboard
# The power board is now only F1, the two 12 V terminals and the star: the
# switching lives on the bought relay module.
PERFBOARD_TERMINALS: list[dict[str, str]] = [
    {"terminal": "12V_IN", "wire": "brick 12V+ via F1 (T 3 A slow-blow)", "net": "12V", "gauge": ">= 0.5 mm2"},
    {"terminal": "12V_OUT", "wire": "relay COM", "net": "12V", "gauge": ">= 0.5 mm2"},
    {"terminal": "GND (star)", "wire": "brick 12V-, pump -, servo brown, UNO GND, breadboard GND rail",
     "net": "GND", "gauge": ">= 0.5 mm2 for the 12 V returns"},
]

RELAY_TERMINALS: list[dict[str, str]] = [
    {"terminal": "VCC", "wire": "5V_BOARD rail", "net": "5V_BOARD", "gauge": "Dupont"},
    {"terminal": "GND", "wire": "breadboard GND rail", "net": "GND", "gauge": "Dupont"},
    {"terminal": "IN", "wire": "UNO D6, with R1 10 k to the module's OFF level", "net": "SIGNAL", "gauge": "Dupont"},
    {"terminal": "COM", "wire": "power board 12V_OUT (brick + leg, after F1)", "net": "12V", "gauge": ">= 0.5 mm2"},
    {"terminal": "NO", "wire": "pump +", "net": "PUMP_SW", "gauge": ">= 0.5 mm2"},
    {"terminal": "NC", "wire": "not connected", "net": "SIGNAL", "gauge": "-"},
]
RELAY_NOTES = [
    "READ THE MODULE before the first power-up: active-HIGH or active-LOW input, coil current, contact "
    "rating, and whether a JD-VCC jumper separates the coil supply from VCC.",
    "In the sketch, set the level BEFORE the direction: digitalWrite(D6, <OFF level>); pinMode(D6, OUTPUT). "
    "The other order glitches the pin to the ON level at boot and kicks the pump.",
    "R1 (10 k) holds the OFF level while D6 is an input: at reset, during boot, and with the jumper pulled.",
    "NO, never NC: a de-energised coil must leave the pump unpowered.",
    "Never PWM the contacts. ~10^5 mechanical cycles is decades at a few doses a day; a switched-on-and-off "
    "duty cycle is not.",
    "Optional, for contact life: a 100 ohm + 100 nF snubber across COM/NO. Not needed on the bench.",
]

INTERLOCK_PARTS: list[dict[str, str]] = [
    {"ref": "F1", "value": "T 3 A slow-blow, 5x20", "role": "pump branch, + leg only; value fixed after bring-up 7f"},
    {"ref": "F2", "value": "1 A, 5x20", "role": "UNO VIN, + leg only"},
    {"ref": "K1", "value": "1-channel relay module, 5 V coil", "role": "switches the 12 V + leg: COM from F1, NO to pump +"},
    {"ref": "R1", "value": "10 k", "role": "D6 to the module's OFF level: pull-down if active-HIGH, pull-up if active-LOW"},
    {"ref": "R2", "value": "10 k", "role": "float hall S pull-up to 5V_BOARD: unplugged or dead = the 'not OK' level"},
    {"ref": "R3", "value": "10 k", "role": "home hall S pull-up to 5V_BOARD (expander P4)"},
    {"ref": "C1", "value": "470-1000 uF electrolytic", "role": "across the servo's 5 V / GND AT THE PLUG"},
    {"ref": "C2", "value": "100 nF", "role": "beside C1, and one across each of the mux and the expander"},
]

# What actually stops the pump, case by case, and what holds it there. The
# 74HC00 AND-gate is gone: rows marked 'firmware' are now only as good as the
# sketch, which is the price of building this with parts in hand.
TRUTH_TABLE: list[dict[str, str]] = [
    {"case": "watering", "d6": "asserted", "float": "above the line: magnet at the hall",
     "pump": "RUNS", "held_by": "firmware"},
    {"case": "firmware idle", "d6": "at rest", "float": "any",
     "pump": "off", "held_by": "hardware: no coil, no contact"},
    {"case": "level past the margin", "d6": "firmware drops it", "float": "below the line: the magnet has left the hall",
     "pump": "off", "held_by": "FIRMWARE"},
    {"case": "float hall unplugged, GND lead off, or dead", "d6": "firmware drops it",
     "float": "reads 'not OK' (R2)", "pump": "off", "held_by": "FIRMWARE, on a hardware sense path"},
    {"case": "MCU in reset / boot / D6 not yet OUTPUT / jumper pulled", "d6": "input -> OFF level (R1)",
     "float": "any", "pump": "off", "held_by": "hardware"},
    {"case": "board 5 V absent (USB out, board dead)", "d6": "-", "float": "any",
     "pump": "off", "held_by": "hardware: coil unpowered"},
    {"case": "12 V absent", "d6": "any", "float": "any",
     "pump": "off", "held_by": "hardware: pump unpowered"},
    {"case": "I2C hung, home hall unreadable", "d6": "firmware drops it", "float": "any",
     "pump": "off", "held_by": "FIRMWARE: unknown position must refuse"},
    {"case": "firmware hung with D6 already asserted", "d6": "stuck asserted", "float": "any",
     "pump": "RUNS until the IWDT resets the board", "held_by": "WATCHDOG (see the gap below)"},
    {"case": "firmware hung and the watchdog off", "d6": "stuck asserted", "float": "any",
     "pump": "RUNS until someone pulls the plug", "held_by": "nothing"},
]
INTERLOCK_NOTES = [
    "The relay's own failure direction is dry: every open, unplug, power loss and reset de-energises the "
    "coil and the contacts fall open. That part is better than the MOSFET it replaces, which needed a "
    "gate pull-down to manage it.",
    "THE GAP: there is no longer a hardware AND between 'firmware says pump' and 'the tank has water'. A "
    "sketch that hangs with D6 already asserted keeps the pump running. Three things bound it, and all "
    "three are firmware: the RA4M1 IWDT enabled (a hang resets the board, D6 reverts to an input, R1 "
    "opens the relay), a hard maximum run time in the same code path that asserts D6, and a no-flow "
    "abort from the flow meter. Write all three or none of this holds.",
    "The float is mounted so that ALLOW is the active state (magnet present). Every sensor failure - an "
    "open line, a dead hall, an unplugged connector, a lost 5 V - therefore reads as refuse, never as "
    "permission.",
    "A float input that never changes state across a refill is presumed dead: refuse, do not assume OK.",
    "Plan item 4 ('Don't flood the flat') puts a hardware interlock back when the parts are in hand: a "
    "74HC00 (or a 74HC08 plus an inverter) between D6, the float and the relay's IN.",
]

# CHOSEN 2026-09-03: the stop-limited float. What makes it fail-safe is the
# stop, not the sensor: it caps how far up the float can travel, so above the
# trip level the float parks at one fixed height (buoyancy holds it against
# the stop) and the magnet stays at the hall however full the tank is. A free
# float tracks the surface and sails past a fixed sensor, which is why the
# easy build can only see "empty".
FLOAT_SKETCH = [
    "    LEVEL ABOVE THE LINE                     LEVEL BELOW THE LINE",
    "    +-----------------------+                +-----------------------+",
    "    | ~~~~~~~~~~~~~~~~~~~~~ | <- surface     |                       |",
    "    | ~~~~~~~~~~~ ==+== ~~~ | <- STOP        |            ==+==      | <- STOP",
    "    | ~~~~~~~~~~~ +-|-+ ~~~ |                |              |        |    (float no",
    "    | ~~~~~~~~~~~ | F |#=====> hall          |              |   #====> hall",
    "    | ~~~~~~~~~~~ +-|-+ ~~~ |    magnet AT   | ~~~~~~~~~~~~ | ~~~~~~ |     longer",
    "    | ~~~~~~~~~~~   |   ~~~ |    the hall    | ~~~~~~~ +----|----+ ~~ |     near it)",
    "    |               |       |                | ~~~~~~~ |    F    | ~~ |",
    "    +---------------+-------+                +---------+---------+---+",
    "",
    "      magnet present = water OK = allow        magnet away = refuse",
]
FLOAT_MOUNTING: list[dict[str, str]] = [
    {"arrangement": "CHOSEN: float travel capped by a STOP at the trip level, hall at the stop "
                    "(sliding on a stem, or a hinged arm as in a cistern)",
     "magnet at the hall": "whenever the level is above the line",
     "allowed is": "the ACTIVE state", "sensor failure reads as": "refuse (fail-safe)",
     "verdict": "built this way"},
    {"arrangement": "rejected: free float, hall low in the tank",
     "magnet at the hall": "only once the level has dropped to it",
     "allowed is": "the PASSIVE state", "sensor failure reads as": "ALLOW (fail-dangerous)",
     "verdict": "easier, but every dead sensor grants permission"},
]
FLOAT_NOTES = [
    "The stop is the whole mechanism: without it the float rides the surface up and away, and a fixed "
    "sensor can only be placed where it sees 'empty'.",
    "Sense in the sketch: magnet present (hall output LOW on a WPSE313) = water above the line = the only "
    "state in which a dose may start. Everything else - no magnet, an open line, a dead or unplugged hall, "
    "a lost 5 V - is 'not OK', because R2 lifts the line and the firmware reads that as refuse.",
    "Set the stop so the trip level leaves enough water above the pump inlet for one full dose plus the "
    "priming volume; the margin, not the sensor, is what keeps the pump wet.",
    "Wiring: one hall on D5 with a 10 k pull-up (R2). Bring-up 5a and 5b prove both directions.",
]

# ---------------------------------------------------------------- power
POWER_BUDGET: list[dict[str, str]] = [
    {"rail": "12V", "consumer": "pump (via F1)", "current": "<= 1.5 A running, 3-5x inrush",
     "note": "ASSUME: read the label, measure in 7f"},
    {"rail": "12V", "consumer": "UNO VIN (via F2)", "current": "~0.5 A at servo stall",
     "note": "the board and everything on 5V_BOARD, through the on-board buck"},
    {"rail": "5V_BOARD", "consumer": "5x moisture", "current": "~25 mA", "note": ""},
    {"rail": "5V_BOARD", "consumer": "3x hall (LEDs)", "current": "~30 mA", "note": "screw, home, float"},
    {"rail": "5V_BOARD", "consumer": "flow meter", "current": "~15 mA", "note": "never from 12 V"},
    {"rail": "5V_BOARD", "consumer": "MUX, PCF8575, DHT11, LDR", "current": "< 10 mA", "note": "and the pull-ups"},
    {"rail": "5V_BOARD", "consumer": "relay coil", "current": "~80 mA", "note": "VERIFY on the module"},
    {"rail": "5V_BOARD", "consumer": "SG90 continuous", "current": "~250 mA run, ~650 mA stall",
     "note": "its own pair from the rail, C1 470-1000 uF at the plug"},
    {"rail": "5V_BOARD", "consumer": "total", "current": "~410 mA running, ~810 mA at servo stall",
     "note": "the stall is a transient; C1 carries it"},
    {"rail": "5V_BOARD", "consumer": "ceiling", "current": "~1.05 A",
     "note": "1.2 A buck total, less the board's ~150 mA"},
]
FUSES = [
    {"ref": "F1", "value": "T 3 A slow-blow", "branch": "pump: power board 12V_IN -> relay COM", "leg": "+ only"},
    {"ref": "F2", "value": "1 A", "branch": "UNO VIN (barrel)", "leg": "+ only"},
]
NEVER = [
    "12 V to any 5 V rail or to the flow meter: never.",
    "Feed the UNO 5 V pin from outside: never (it is an output).",
    "The pump on a 5 V rail: never (12 V through the relay contacts).",
    "The servo or the pump running on USB power: never (500 mA port against a 650 mA stall; VIN from the brick).",
    "A fuse in a return leg: never (+ leg only).",
    "The pump's 12 V return through the board's GND pin: never (pump - straight to the star).",
    "The relay's NC contact for the pump: never (NO, so a dead coil is a dead pump).",
    "PUMP_EN or the servo on the I2C expander: never (power-on HIGH would run them).",
    "A counted pulse train (screw hall, flow meter) through the mux or the expander: never (missed edges).",
    "Breadboard or Dupont in the 12 V loop: never (screw terminals, >= 0.5 mm2).",
]
BENCH_POWER_ALT = (
    "USB may power the board for the sensor-only steps (bring-up 1-3). From step 4 on, the barrel jack "
    "carries VIN from the 12 V brick: the servo's stall and the relay coil are more than a USB port "
    "will give, and a brown-out mid-dose is the one failure this rig should not have. Grounds common "
    "at the star either way.")

# ---------------------------------------------------------------- hydraulics
HYDRAULIC_CHAIN: list[dict[str, str]] = [
    {"stage": "reservoir", "detail": "ABOVE the pump inlet (gravity-primed); float travel capped by a stop at the trip level, hall at the stop"},
    {"stage": "pump", "detail": "12 V diaphragm, inlet below the reservoir surface"},
    {"stage": "silicone tube 30-50 cm", "detail": "soft: pulsation damper"},
    {"stage": "flow meter", "detail": "vertical, flow UPWARD, tilt <= 5 deg; no pulses below its flow floor"},
    {"stage": "manifold inlet", "detail": "one manifold, 5 outlets"},
    {"stage": "outlets 1-5", "detail": "pots, or the bucket on the bench"},
]

# ---------------------------------------------------------------- parts
# status: in hand | ASSUME (ordered) | to buy | to build
PARTS: list[dict[str, str]] = [
    {"part": "Arduino UNO R4 WiFi", "qty": "1", "status": "in hand", "verify": ""},
    {"part": "PCF8575 I2C expander module", "qty": "1", "status": "in hand",
     "verify": "VERIFY 10 k pull-ups on SDA/SCL (else add 4.7 k to 5V_BOARD); A0-A2 low -> 0x20"},
    {"part": "CD74HC4067 mux module", "qty": "1 (+1 later)", "status": "in hand",
     "verify": "VERIFY EN pull-down on the breakout (EN goes to GND regardless)"},
    {"part": "Whadda WPSE313 hall module", "qty": "3 of 8", "status": "in hand",
     "verify": "VERIFY on-board pull-up (ours is fitted regardless); LED lights at the magnet's south pole"},
    {"part": "SG90 continuous-rotation servo", "qty": "1", "status": "in hand",
     "verify": "on 5V_BOARD with C1 at the plug; board fed from VIN, not USB"},
    {"part": "Sensor Kit temperature/humidity", "qty": "1", "status": "in hand",
     "verify": "READ THE MODULE: DHT11 (D7, Environment.setPin(7)) or DHT20 (I2C 0x38, Environment_I2C)"},
    {"part": "Sensor Kit light (LDR)", "qty": "1", "status": "in hand", "verify": ""},
    {"part": "capacitive soil-moisture sensor v1.2/v2.0", "qty": "5", "status": "in hand", "verify": "AOUT 0-3 V, ~10 k source"},
    {"part": "neodymium magnets (cart, screw, float)", "qty": "3+", "status": "in hand",
     "verify": "VERIFY polarity: south pole toward the hall face"},
    {"part": "relay module, 1 channel, 5 V coil (TRU COMPONENTS TC-9927156 or like)", "qty": "1", "status": "in hand",
     "verify": "READ THE MODULE: active-HIGH or active-LOW IN; coil current; contact rating (>= 2 A at 12 V DC); "
               "JD-VCC jumper fitted = coil on 5V_BOARD. Sets R1's direction and the sketch's OFF level"},
    {"part": "pump, 12 V DC diaphragm", "qty": "1", "status": "ASSUME",
     "verify": "READ THE LABEL: voltage, running current (assume <= 1.5 A), inrush 3-5x; measure in 7f, then fix F1"},
    {"part": "12 V brick", "qty": "1", "status": "ASSUME >= 3 A",
     "verify": "READ THE LABEL: amps (a 2 A brick browns out at pump start)"},
    {"part": "flow meter YF-S401", "qty": "1", "status": "ASSUME",
     "verify": "READ THE SUFFIX: -0207 (0.2-3 L/min) or -3507 (0.3-6 L/min); ~5880 pulses/L; vertical, flow up; 5V_BOARD only"},
    {"part": "74HC00 quad NAND, DIP-14 + 5 V UBEC", "qty": "1 each", "status": "later, not now",
     "verify": "the hardware interlock (plan item 4) and the servo supply once several servos move at once"},
    {"part": "fuse holders 5x20 + T 3 A slow-blow + 1 A", "qty": "2 + spares", "status": "to buy", "verify": "F1 value fixed after 7f"},
    {"part": "flyback / snubber parts", "qty": "-", "status": "not needed",
     "verify": "the relay module carries its own coil diode. No 1N5819 across the pump: contacts take the "
               "kick as an arc, not an avalanche. If a MOSFET ever comes back, use a 3 A part (1N5822 / "
               "SB360), not a 1 A 1N5819 on a 1.5 A pump"},
    {"part": "resistors 1 k x1, 4.7 k x2, 10 k x4", "qty": "set", "status": "to buy",
     "verify": "10 k: R1, R2, R3 and a spare; 1 k: flow-meter series; 4.7 k only if the I2C pull-ups are missing"},
    {"part": "470-1000 uF electrolytic (C1, >= 10 V) + 100 nF ceramic x4", "qty": "1 + 4", "status": "to buy",
     "verify": "C1 at the SERVO PLUG, not at the board; 100 nF for mux, expander, servo, spare"},
    {"part": "perfboard, screw terminals (>= 6 positions), wire >= 0.5 mm2 red/black/purple", "qty": "1 set", "status": "to buy",
     "verify": "F1, the two 12 V terminals and the star; soldered; never breadboard in the 12 V loop"},
    {"part": "breadboard, Dupont jumpers (colours per the table), JST-PH 2.0 leads x5, Grove cables x2", "qty": "1 set", "status": "to buy", "verify": ""},
    {"part": "silicone tube 30-50 cm + tube for the meter's 7 mm outlet and the manifold inlet", "qty": "1 set", "status": "to buy", "verify": "meter variant sets the intake bore"},
    {"part": "reservoir with a keyed float carrying a magnet; bucket", "qty": "1", "status": "to build",
     "verify": "the float's UP travel must be capped by a stop at the trip level, with the hall at that "
               "stop: magnet present = water above the line = the only state that allows a dose"},
]

# ---------------------------------------------------------------- bench firmware contract
BENCH_FIRMWARE_NOTE = ("The bench sketch is not part of this deliverable (pitch: 'Bench rig'); "
                       "it must provide these commands over serial.")
BENCH_COMMANDS: list[dict[str, str]] = [
    {"command": "i2c", "does": "scan Wire, list addresses (expect 0x20; 0x38 if DHT20)"},
    {"command": "mux <0-15>|all", "does": "select, wait >= 1 ms, read twice, print the second (14-bit raw)"},
    {"command": "hall", "does": "stream screw (D3), home (expander P4) and float (D5) states; an I2C read error prints 'home unknown'"},
    {"command": "flow", "does": "pulses per second on D2 and total since reset"},
    {"command": "servo <+-us> <ms>", "does": "bounded: pulse offset for <= cap ms, then stop"},
    {"command": "home", "does": "run toward home until HALL_HOME, bounded time, zero the count"},
    {"command": "goto <1-5>", "does": "step to the outlet counting screw pulses, bounded"},
    {"command": "pump <ms>", "does": "assert D6 for <= cap ms; refused when the float reads 'not OK'; aborts on no flow within the timeout; the cap lives in the same code path that asserts D6"},
    {"command": "status", "does": "pins, counts, last error, uptime, and whether the IWDT is enabled"},
]

BRINGUP: list[dict[str, str]] = [
    {"step": "0", "do": "Continuity before power: 12 V to every 5 V rail OPEN; relay COM-NO OPEN with the coil off; every GND common at the star; barrel plug centre +.",
     "proves": "nothing is crossed"},
    {"step": "1", "do": "Board alone on USB: `i2c` sees 0x20 (and 0x38 if the kit has the DHT20).",
     "proves": "I2C, pull-ups"},
    {"step": "2", "do": "Mux + one moisture sensor: `mux all` reads all 16 channels, the wired one moves when wetted.",
     "proves": "select lines, ADC path"},
    {"step": "3", "do": "Halls on USB: screw (D3) and float (D5) follow a magnet; home changes through expander P4.",
     "proves": "both pull-ups and the expander as an input"},
    {"step": "4a", "do": "Relay DRY, no 12 V on COM: `pump 2000` clicks; meter COM-NO closed while it holds, open after.",
     "proves": "polarity of IN and the sketch's OFF level"},
    {"step": "4b", "do": "Still dry: press RESET mid-click -> contacts open.", "proves": "R1 holds the OFF level"},
    {"step": "4c", "do": "Still dry: pull the D6 jumper mid-click -> contacts open. Only now wire 12 V onto COM.",
     "proves": "no hidden path to the coil"},
    {"step": "5a", "do": "Float in the 'below the line' state -> `pump 2000` is refused.", "proves": "the firmware interlock"},
    {"step": "5b", "do": "Unplug the float hall mid-dose -> stops; meter S in that state (>= 4 V).",
     "proves": "an open reads as 'not OK' (R2)"},
    {"step": "6", "do": "Move power to the barrel jack from the 12 V brick. Servo: `servo`, `home`, `goto`, then repeat with WiFi connected and the cart stalled against an end stop.",
     "proves": "the buck carries stall + TX; a reset here means C1 is missing or too small"},
    {"step": "7a", "do": "Bucket only: prime with `pump`, then `pump 2000` runs.", "proves": "the pump loop"},
    {"step": "7b", "do": "Pump a weighed 500 ml through outlet 1 counting pulses = ml/pulse; record the lowest flow that still pulses and set the no-flow timeout from it.",
     "proves": "meter variant, calibration, floor"},
    {"step": "7c", "do": "RESET mid-dose -> stops. Then force a hang (a command that spins) -> the IWDT must reset the board and drop the pump inside its window.",
     "proves": "the watchdog, now the ONLY thing between a hung sketch and a running pump"},
    {"step": "7d", "do": "Measure pump start and dead-head current; fix the F1 value.", "proves": "fuse value"},
]


# ---------------------------------------------------------------- rendering
def md_table(rows: Sequence[Any], columns: Sequence[tuple[str, str]] | None = None) -> str:
    """Render rows (dicts or dataclasses) as a GitHub markdown table.

    columns: (key, header) pairs; default = every key of the first row. A key
    may be a dataclass property (e.g. Wire.board_pin). Pipes are escaped, bools
    become yes/no, tuples are joined with ", ".
    """
    if not rows:
        return ""

    def get(row: Any, key: str) -> Any:
        return row[key] if isinstance(row, dict) else getattr(row, key)

    if columns is None:
        first = rows[0]
        keys = list(first.keys()) if isinstance(first, dict) else [f.name for f in fields(first)]
        columns = [(k, k) for k in keys]

    def cell(v: Any) -> str:
        if isinstance(v, bool):
            return "yes" if v else "no"
        if v is None:
            return ""
        if isinstance(v, (tuple, list)):
            v = ", ".join(str(x) for x in v)
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(h for _, h in columns) + " |"
    sep = "|" + "|".join(" --- " for _ in columns) + "|"
    body = ["| " + " | ".join(cell(get(r, k)) for k, _ in columns) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def md_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {it}" for it in items)


def _check() -> None:
    """Self-consistency: every wire's modules and nets exist; anchors are unique per block."""
    for w in WIRES:
        assert w.frm in MODULES, w
        assert w.to in MODULES, w
        assert w.net in COLOUR_NAMES, w
    pins = [w.board_pin for w in pin_map()]
    assert len(pins) == len(set(pins)), pins
    assert not [w for w in WIRES if w.net == "5V_SERVO"], "the servo rail is gone: one 5 V rail"
    ins = [w for w in WIRES if w.to == "RELAY" and w.to_pin == "IN"]
    assert len(ins) == 1 and ins[0].frm_pin == "D6", "exactly one wire drives the relay's IN"
    no = [w for w in WIRES if w.frm == "RELAY" and w.frm_pin == "NO"]
    assert len(no) == 1 and no[0].to == "PUMP", "the pump hangs off NO, never NC"
    assert not [w for w in WIRES if w.frm == "PUMP" and w.to == "UNO"], "the pump return goes to the star"


_check()

if __name__ == "__main__":
    print(md_table(pin_map(), [("board_pin", "board pin"), ("signal", "signal"), ("to", "module"),
                               ("to_pin", "module pin"), ("connector", "connector"), ("colour", "colour"),
                               ("cable", "cable / note"), ("later", "later")]))
    print()
    print(md_table(MUX_CHANNELS))
    print()
    print(md_table(EXPANDER_PINS))
    print()
    print(md_table(TRUTH_TABLE))
    print()
    print(md_table(PARTS))
    print(f"\n{len(WIRES)} wires, {len([w for w in WIRES if not w.later])} on the bench")
