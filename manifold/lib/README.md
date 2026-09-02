# lib — shared helpers

Every part file starts `include <../params.scad>`, then `use <../lib/...>` for what it needs,
then `$fn = fn_round;`. A `use`d file sees no variables from the caller, only its arguments and
special variables: `$fn` set in the part file reaches every helper (pass `$fn = fn_small` on a
small feature). All lengths in mm, angles in degrees, axes as stated; nothing here reads
params.scad. Name clash to know about: params.scad defines `gear_od(t)` (uses `gear_module`) and
gear.scad defines `gear_od(teeth, module_)`; in a part file the params version wins, so call the
one-argument form there.

## shapes.scad

| signature | what it makes |
|---|---|
| `chamfered_rect(size, c, center=false)` | 2D `[w, h]` rectangle, four corners cut at 45° by `c`; corner at the origin unless centred |
| `rounded_rect(size, r, center=false)` | 2D `[w, h]` rectangle, corners rounded by `r`; corner at the origin unless centred |
| `chamfered_box(size, c, center=false)` | 3D `[x, y, z]` box, all twelve edges chamfered at 45° by `c`; corner at the origin unless centred |
| `hex(af, h, center=false)` | hexagonal prism, across-flats `af`, height `h` along +Z from z=0; corners on ±X, flats at y = ±af/2 |
| `torus(R, r, fn_tube)` | torus about Z, centreline radius `R`, tube radius `r`, tube centre plane z=0; `fn_tube` defaults to the caller's `$fn` |
| `right_triangle(a, b=a)` | 2D right triangle, right angle at the origin, legs `a` along +X and `b` along +Y (a 45° chamfer or gusset profile to extrude) |
| `keep_below(axis, at, big=1000) children` | section: keeps the part of the children with coordinate along `axis` (`"x"`, `"y"`, `"z"`) below `at` |
| `keep_above(axis, at, big=1000) children` | section: keeps the part above `at` |

## barb.scad

| signature | what it makes |
|---|---|
| `barb(bore, shank_d, ridge_d, len, ridges, taper_len, tip_d, steep, flange, gap=2)` | hose barb, axis +Z from z=0 to `len`: shank ø`shank_d`, `ridges` crests ø`ridge_d`, each rising on a face `steep`° from the axis (base side) and tapering back to the shank over `taper_len`, the last one tapering to ø`tip_d` on the end face; bore ø`bore` through; `flange = [d, h]` = cone from ø`d` on z=0 to the shank at z=h, `undef` = none; `gap` = shank between a taper's end and the next crest (v2's 2, = `barb_ridge_gap`) |
| `barb_profile(...)` (same arguments) | the `(r, z)` polygon the barb revolves — for sections or a custom revolve |
| `barb_crest_z(len, ridges, taper_len, gap, i)` | z of crest `i` (0 = nearest the base) |
| `barb_rise_dz(shank_d, ridge_d, steep)` | axial length of a crest's steep rise |

Outlet: `barb(outlet_barb[0], outlet_barb[1], outlet_barb[2], outlet_barb[3], barb_ridges, outlet_barb_prof[0], outlet_barb_prof[1], barb_steep, outlet_flange)`,
rotated so +Z points −Y and placed at (W/2, 0, gate_z(i)). Inlet: the same with `inlet_barb`,
`inlet_barb_prof` and `undef`, at (W/2, wall + inner_h/2, body_z1 − joint_len) along +Z.
Verified against ref connector.stl and connector_8mm.stl: identical radius profiles, except that
v2's outlet valley between the two ridges is ø5.5 while the brief (and this) returns to the shank ø6.

## oring.scad

| signature | what it makes |
|---|---|
| `oring(id, cs)` | ghost O-ring: torus, inner diameter `id`, cross-section `cs`, tube centre plane z=0, axis Z (place at `y_ring`) |
| `oring_counterbore(id, cs, clear, depth, overshoot=0.01)` | cutter: cylinder ø`id + 2 cs + clear` from z = −`depth` to z = +`overshoot`; put z=0 on the face the ring drops into, +Z out of the material |

## gear.scad

Gear centred on the origin, teeth in XY, thickness along +Z from z=0, one tooth centred on +X.
Standard proportions: addendum = m, dedendum = 1.25 m. Two gears mesh when the second is
rotated by `180/teeth` (a gap facing the first).

| signature | what it makes |
|---|---|
| `spur_gear(teeth, module_, thickness, pressure_angle=20, backlash=0, bore=0, flank_pts=8)` | the solid involute gear; `backlash` is taken off the circular tooth thickness; `bore` ø through (0 = none); `flank_pts` segments per flank |
| `gear_2d(teeth, module_, pressure_angle=20, backlash=0, flank_pts=8)` | its 2D outline |
| `gear_tooth(teeth, module_, pressure_angle=20, backlash=0, flank_pts=8)` | one tooth's point list (centred on +X, from `module_/10` inside the root circle to the tip) |
| `gear_pitch_r(teeth, module_)` | pitch radius = m·teeth/2 |
| `gear_base_r(teeth, module_, pressure_angle=20)` | base circle radius |
| `gear_outer_r(teeth, module_)` | tip radius = pitch + m |
| `gear_root_r(teeth, module_)` | root radius = pitch − 1.25 m |
| `gear_od(teeth, module_)` | tip diameter = m·(teeth + 2) (shadowed by params' `gear_od(t)` in part files) |
| `gear_centre_distance(teeth_a, teeth_b, module_)` | m·(teeth_a + teeth_b)/2 |

Verified: a 20-tooth m0.75 gear measures ø16.5 at the tips and two of them at 15 mm centre
distance (second rotated 9°) have an empty intersection with `gear_backlash = 0.1`.
