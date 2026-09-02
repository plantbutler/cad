"""Shared drawing conventions for the bench wiring drawings.

Every draw_*.py imports this and nothing else for look-and-feel, so the four
drawings share colours, fonts, block geometry, the title line and the output
format. Net names and their colours are the same ones nets.py uses, so a wire's
colour on paper is the colour of the physical wire on the bench.

Toolchain: schemdraw 0.23 on the matplotlib backend (Agg, headless).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import schemdraw  # noqa: E402
from schemdraw import elements as elm  # noqa: E402

schemdraw.use("matplotlib")

DATE = "2026-09-02"
HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- colours
# Net name -> colour. Drawing colour == physical wire colour on the bench.
COLOURS: dict[str, str] = {
    "12V": "#d62728",  # red      12 V brick rail
    "5V_BOARD": "#ff7f0e",  # orange   UNO 5 V pin -> sensors and logic
    "5V_SERVO": "#8c564b",  # brown    UBEC out -> servo red ONLY
    "GND": "#000000",  # black    one star point on the perfboard
    "SIGNAL": "#1f77b4",  # blue     every logic / analog signal
    "I2C": "#2ca02c",  # green    SDA / SCL
    "PUMP_SW": "#9467bd",  # purple   pump switched return (MOSFET drain), NOT ground
    "WATER": "#17becf",  # teal     hydraulic chain (tube), not a wire
    "NOTE": "#555555",  # grey     annotations, frames, later-expansion text
}
LATER_LS = "--"  # linestyle for "bolted on later" (MUX2, manifolds 2-3)

# ---------------------------------------------------------------- fonts
FONT = "monospace"
FS_PIN = 8  # pin labels outside a block
FS_BODY = 9  # pin names inside a block, wire labels, notes
FS_TITLE = 11  # the one title line

# ---------------------------------------------------------------- geometry
PINSPACING = 0.6  # drawing units between pins on one side of a block
EDGEPAD = 0.45  # block edge to first pin
LEADLEN = 0.5  # pin stub length outside the block

PinSpec = tuple[str, str] | tuple[str, str, str | None]


def colour(net: str) -> str:
    """Colour for a net name ("12V", "5V_BOARD", "SIGNAL", ...)."""
    return COLOURS[net]


def drawing() -> schemdraw.Drawing:
    """A new headless Drawing with the shared font, size, line width, white ground.

    Use as a context manager:  with style.drawing() as d: ...
    """
    d = schemdraw.Drawing(file=None, show=False)
    d.config(font=FONT, fontsize=FS_BODY, bgcolor="white", lw=1.4, margin=0.3)
    return d


def block(
    label: str,
    pins: Sequence[PinSpec],
    *,
    size: tuple[float, float] | None = None,
    pinspacing: float = PINSPACING,
    edgepad: float = EDGEPAD,
    leadlen: float = LEADLEN,
    later: bool = False,
    **kw,
) -> elm.Ic:
    """An Ic block.

    pins: (pin_name, side[, outside_label]) tuples. pin_name is printed inside
    the box and becomes the anchor (use pin(ic, name) or getattr); side is
    "left" | "right" | "top" | "bottom"; the optional outside label is printed
    past the stub (silkscreen name, wire colour, ...). Pin names must be unique
    within one block. `size` overrides the auto size (width, height).
    `later=True` dashes the outline (expansion that is not on the bench yet).
    The block label sits above the box. Position with .at((x, y)); rotation is
    pinned to 0 so a block never inherits the direction of the previous wire.
    """
    icpins = []
    for spec in pins:
        name, side = spec[0], spec[1]
        outside = spec[2] if len(spec) > 2 else None
        icpins.append(elm.IcPin(name=name, side=side, pin=outside))
    ic = elm.Ic(
        pins=icpins,
        size=size,
        pinspacing=pinspacing,
        edgepadW=edgepad,
        edgepadH=edgepad,
        leadlen=leadlen,
        lsize=FS_BODY,
        plblsize=FS_PIN,
        **kw,
    )
    ic.theta(0)
    ic.label(label, loc="top", ofst=0.15, fontsize=FS_BODY)
    if later:
        ic.linestyle(LATER_LS).color(COLOURS["NOTE"])
    return ic


def block_at(label: str, pins, size, *, later: bool = False, label_loc: str = "center",
       pinspacing: float = PINSPACING, lblofst: float = 0.15) -> elm.Ic:
    """Like block(), but every pin sits at an ABSOLUTE offset along its side.

    pins: (pin_name, side, z[, outside_label]); z is the pin's distance in
    drawing units from the body's bottom edge (left/right sides) or from its
    left edge (top/bottom sides), so a pin can be lined up with whatever it
    connects to. schemdraw centres the pin group on a side and reads `pos` as a
    fraction of (n-1)*pinspacing, so pos is computed back from z here; a side
    with a single pin is centred whatever z says.

    `label_loc` "center" prints the name inside the box, "top" above it.
    `later=True` dashes the outline (expansion that is not on the bench yet).
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
        span = (n - 1) * pinspacing
        pad = (length - span) / 2
        pos = (z - pad) / span if span else None
        if pos == 0:
            pos = 1e-6
        icpins.append(elm.IcPin(name=name, side=side, pos=pos, pin=(p[3] if len(p) > 3 else None)))
    block = elm.Ic(pins=icpins, size=size, pinspacing=pinspacing, edgepadW=EDGEPAD,
                   edgepadH=EDGEPAD, leadlen=LEADLEN, lsize=FS_BODY, plblsize=FS_PIN)
    block.theta(0)
    block.label(label, loc=label_loc, ofst=lblofst if label_loc == "top" else 0,
                fontsize=FS_BODY, color=COLOURS["NOTE"] if later else "black")
    if later:
        block.linestyle(LATER_LS).color(COLOURS["NOTE"])
    return block


def dot(xy, net: str = "SIGNAL", open_: bool = False, radius: float = 0.08) -> elm.Dot:
    """A junction dot in the net's colour (open=True for a rail tap / test point)."""
    return elm.Dot(radius=radius, open=open_).at(xy).color(COLOURS[net])


def ground(xy, net: str = "GND", later: bool = False) -> elm.Ground:
    """A ground symbol at xy (the star point on the perfboard, electrically)."""
    g = elm.Ground().at(xy).theta(0).color(COLOURS["NOTE" if later else net])
    if later:
        g.linestyle(LATER_LS)
    return g


def pin(ic: elm.Ic, name: str):
    """Anchor point of pin `name` on a placed block (works for names like "5V")."""
    return getattr(ic, name)


def wire(
    start,
    end,
    net: str = "SIGNAL",
    shape: str = "-|",
    label: str | None = None,
    loc: str = "top",
    later: bool = False,
    **kw,
) -> elm.Wire:
    """Orthogonal wire from anchor `start` to anchor `end` in the net's colour.

    shape: "-" straight, "-|" horizontal then vertical, "|-" vertical then
    horizontal, "n"/"c" u-shapes (see schemdraw Wire). Never diagonal.
    label is placed at `loc` ("top" | "bottom" | "left" | "right" | "start" | "end").
    """
    w = elm.Wire(shape, **kw).at(start).to(end).color(COLOURS[net])
    if later:
        w.linestyle(LATER_LS)
    if label:
        w.label(label, loc=loc, fontsize=FS_BODY, color=COLOURS[net])
    return w


def line(direction: str, length: float, net: str = "SIGNAL", label: str | None = None,
         loc: str = "top", later: bool = False, **kw) -> elm.Line:
    """A straight Line segment: direction "right" | "left" | "up" | "down".

    Chain from the previous element's end, or call .at(anchor) on the result.
    """
    ln = elm.Line(**kw).color(COLOURS[net])
    getattr(ln, direction)(length)
    if later:
        ln.linestyle(LATER_LS)
    if label:
        ln.label(label, loc=loc, fontsize=FS_BODY, color=COLOURS[net])
    return ln


def note(text: str | Iterable[str], xy, net: str = "NOTE", fontsize: float = FS_BODY,
         halign: str = "left", valign: str = "top") -> elm.Label:
    """Monospace text (a str or lines) with its top-left corner at xy."""
    if not isinstance(text, str):
        text = "\n".join(text)
    return elm.Label().at(xy).theta(0).label(text, halign=halign, valign=valign,
                                             fontsize=fontsize, color=COLOURS[net])


def frame(xy, width: float, height: float, label: str | None = None,
          net: str = "NOTE", later: bool = False) -> elm.Rect:
    """A thin rectangle with corner xy (lower-left), optionally titled at its top-left."""
    x, y = xy
    # .at((0, 0)) pins the element's origin: Rect's corners are then absolute,
    # not relative to wherever the previous element happened to end.
    r = elm.Rect(corner1=(x, y), corner2=(x + width, y + height),
                 lw=1.0, ls=LATER_LS if later else "-").at((0, 0)).theta(0).color(COLOURS[net])
    if label:
        r.label(label, loc="top", halign="left", ofst=(-width / 2 + 0.1, 0.1),
                fontsize=FS_BODY, color=COLOURS[net])
    return r


# ---------------------------------------------------------------- tables on a drawing
CH, LH = 0.145, 0.265  # drawing units per character / per line at FS_PIN


def table_lines(rows, columns) -> list[str]:
    """Monospace text table as a list of lines. columns = ((key, header), ...)."""
    cells = [[h for _, h in columns]] + [[str(r[k]) for k, _ in columns] for r in rows]
    widths = [max(len(c[i]) for c in cells) for i in range(len(columns))]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    out = [fmt.format(*cells[0]).rstrip(), "  ".join("-" * w for w in widths)]
    out += [fmt.format(*c).rstrip() for c in cells[1:]]
    return out


def table_note(d, title: str, lines: Sequence[str], xy) -> float:
    """Framed monospace table with a title above it; returns the y of its bottom edge."""
    x, y = xy
    w = max(len(ln) for ln in lines) * CH + 0.4
    h = len(lines) * LH + 0.35
    d += frame((x, y - h), w, h, label=title)
    d += note(lines, (x + 0.2, y - 0.15), fontsize=FS_PIN)
    return y - h


def legend(d: schemdraw.Drawing, xy,
           nets: Sequence[str] = ("12V", "5V_BOARD", "5V_SERVO", "GND", "SIGNAL", "I2C"),
           step: float = 0.45) -> None:
    """Colour key added to `d`: a short swatch per net, stacked downwards from xy (top-left).

    "LATER" in `nets` draws the dashed later-expansion sample. Adds to d itself
    (a batch of elements must not be re-added by the caller).
    """
    x, y = xy
    for i, net in enumerate(nets):
        yy = y - i * step
        if net == "LATER":
            sw = elm.Line().at((x, yy)).right(0.7).color(COLOURS["NOTE"]).linestyle(LATER_LS)
            text = "later"
        else:
            sw = elm.Line().at((x, yy)).right(0.7).color(COLOURS[net]).linewidth(2.5)
            text = net
        sw.label(text, loc="right", halign="left", fontsize=FS_PIN, color=COLOURS["NOTE"])
        d.add(sw)


def title(d: schemdraw.Drawing, text: str, xy=None, pad: float = 0.5) -> elm.Label:
    """The one title line: `text` plus the date, above the drawing's top-left.

    Call it LAST (after every element is placed) so the bounding box is final;
    pass xy to place it explicitly instead.
    """
    if xy is None:
        bb = d.get_bbox()
        xy = (bb.xmin, bb.ymax + pad)
    return elm.Label().at(xy).theta(0).label(f"{text} — {DATE}", halign="left", valign="bottom",
                                             fontsize=FS_TITLE, color="black")


def save(d: schemdraw.Drawing, stem: str, out_dir: Path = HERE, dpi: int = 150) -> tuple[Path, Path]:
    """Write <out_dir>/<stem>.svg and <stem>.png (150 dpi, white ground). Returns both paths."""
    svg = out_dir / f"{stem}.svg"
    png = out_dir / f"{stem}.png"
    d.save(str(svg), transparent=False)
    d.save(str(png), transparent=False, dpi=dpi)
    return svg, png
