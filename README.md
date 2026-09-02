# plantbutler / cad

Everything physical about Plant Butler, reproducible from source: OpenSCAD parts, the KiCad
wiring diagram, the bill of materials and the bench notes.

- [`manifold/`](manifold/README.md) — the watering manifold: a lead screw moves a magnet cart
  over five ball gates on O-ring seats. Parametric OpenSCAD, ten printed parts, `make stl` for
  the print files. The FreeCAD design it replaces is kept in `manifold/reference/`.

What comes next and in which order is in the [plan](https://github.com/plantbutler/plan); the
decisions it is built on are in the
[umbrella](https://github.com/plantbutler/plantbutler/blob/main/DECISIONS.md).
