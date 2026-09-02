# Plant Butler manifold v3

A parametric OpenSCAD (2021.01) model of the watering manifold: one water gallery with
`n_gates` outlets, each closed by an 8 mm steel ball resting on an O-ring, opened by a magnet
that a lead screw parks over the gate. It is a rebuild of the FreeCAD assembly `valveV2`
(`reference/`) with the inverted-nail plungers replaced by ball gates, every dimension derived
from `params.scad`, and every part printable flat with no supports.

Water enters through the inlet barb at the back, fills the gallery and leaves only through a
gate whose ball is lifted. A cart rides on the lid top, pushed along the manifold by an M3
threaded rod through a nut trapped in one of its ears; the rod turns in the servo holder at
the front and the screw holder at the back, driven by an SG90 through two spur gears outboard
of the servo holder. The magnet in the cart floor rides on the lid: parked over a gate it
lifts that ball off its O-ring and water flows under the ball into the outlet barb. The pump
is off while the cart moves (firmware). Home is the cart resting on the threadless front of
the rod against a spring.

Printed parts: `main_body`, `lid`, `outlet_barb` (one per gate), `end_cap`, `inlet_cap`,
`servo_holder`, `screw_holder`, `cart`, `servo_gear`, `screw_gear`. Hardware: 440C balls,
O-rings, a ø6×3 magnet, an M3 threaded rod, M3 nuts and washers, an SG90, M2 screws, a small
compression spring.

## Frame

X across the width (0..`W`), Y up (0 = outside floor of the main body), Z along the manifold;
the servo end is the front (−Z), the inlet end the back (+Z). Gate `i` (0-based) is centred at
`gate_z(i) = i·pitch + gate_len/2` — 9, 31, 53, 75, 97 with the defaults. Every part module
builds its part in this frame; `<part>_print()` lays it on z = 0 for export;
`<part>_size()` returns its [x, y, z] extents. `assembly.scad` only turns the whole scene by
`screen_rot` for the screen, so Y is up in the pictures.

## How a gate works

The ball (ø `ball_d`) rests on an O-ring of inner diameter `oring_id` and cross-section
`oring_cs`, whose tube centre-line has radius `r_o = (oring_id + oring_cs)/2`; ball and tube
touch when their centres are `Rb = ball_d/2 + oring_cs/2` apart, so the seated ball centre sits
`sqrt(Rb² − r_o²)` above the ring's centre plane `y_ring`. Lifting the ball opens a
frustum-shaped throat between the ring and the ball, of area `π·r_o·(1 + k/D)·(D − Rb)` with
`k = ball_d/2 − oring_cs/2` and `D` the new centre distance; setting that equal to
`lift_factor` × the outlet bore area gives a quadratic in `D`, `lift` follows from it, and the
gallery height `inner_h` is the smallest number of layers that lets the lifted ball touch the
lid lip.

The O-ring sits in a counterbore ø `groove_od` × `groove_d` in the top of a seat boss on the
floor, its inner diameter at the edge of the outlet hole; the counterbore is `groove_d` deep so
the ball touches rubber, never the step. A cage tube on the lid (ø `cage_bore` inside) reaches
`cage_below_equator` below the seated ball's centre, so the ball cannot leave its seat sideways,
and stops `cage_window_h` above the boss so water can enter under it.

## Parameters (`params.scad`)

Everything else is derived; the derivations are guarded by asserts that fail with a message.

| name | default | why |
|---|---|---|
| `line_w`, `layer_h` | 0.4, 0.2 | printer: thin frames are multiples of `line_w`, heights that must land on a layer round up to `layer_h` |
| `fn_round`, `fn_small` | 64, 32 | `$fn` for sealing/running features and for small holes |
| `n_gates` | 5 | outputs |
| `gate_len`, `joint_len` | 18, 4 | gallery length per gate; lap joint length [v2] |
| `wall` | 1.6 | every wall = 4 perimeters; lap joints split it into two half-skins |
| `inner_w` | 18 | gallery width [v2] |
| `extra_len` | 10 | end cap cavity in front of the first gate, room for the water to turn [v2] |
| `joint_clear` | 0.15 | per-side clearance on lap joints and the lid lip (v2 had 0: does not fit FDM) |
| `lip_chamfer` | 1.6 | 45° fillets under the lid lip [v2 internal_chamfer] |
| `gallery_chamfer` | 1.6 | 45° fillets along the gallery's inner floor/wall corners, between the lap joints [v2 large_Chamfer]; asserted clear of the seat boss |
| `ball_d`, `outlet_id` | 8, 4 | 440C ball; outlet hole through the floor |
| `oring_id`, `oring_cs` | 4, 1.5 | O-ring; its ID sits at the outlet hole edge |
| `groove_depth_ratio` | 0.75 | groove depth as a fraction of the cross-section: the ball must touch the ring, not the step |
| `groove_clear` | 0.2 | radial slack on the counterbore so the ring drops in |
| `seat_floor_min`, `seat_boss_wall` | 1.2, 1.2 | material under the groove (6 layers) and around it (3 perimeters) |
| `lift_factor` | 2 | throat area under the lifted ball = `lift_factor` × outlet bore area |
| `cage_clear`, `cage_wall` | 0.4, 1.2 | radial slack ball ↔ cage; cage wall = 3 perimeters |
| `cage_below_equator` | 1.5 | how far the cage reaches below the seated ball centre |
| `cage_window_min`, `cage_side_gap` | 1.5, 1.0 | minimum gap cage ↔ boss for the water; minimum gap cage ↔ gallery wall |
| `lid_slot_depth` | 0 | optional magnet groove along the lid top (0 = flat, as v2) |
| `mag_d`, `mag_h`, `mag_clear`, `mag_margin` | 6, 3, 0.1, 1.0 | ø6×3 magnet, press-fit hole, floor left each side of it |
| `ear_h`, `ear_top_w`, `ear_base_inset` | 7, 7.2, 1.6 | cart ears: height, top width (swallows the nut slot + 2 perimeters each side) [v2 5], root inset from the floor edge |
| `screw_h` | 5.5 | rod axis above the lid top [v2] |
| `screw_d`, `screw_hole_d` | 3, 3.2 | M3 rod and its clearance hole |
| `nut_af`, `nut_clear`, `nut_t` | 5.5, 0.1, 2.4 | M3 nut across flats, slot clearance, thickness |
| `gear_module`, `servo_teeth`, `screw_teeth`, `gear_t` | 0.75, 20, 20, 4 | two identical gears, OD 16.5, centre distance 15 [gears.FCStd] |
| `gear_backlash`, `pressure_angle` | 0.1, 20 | taken off each tooth thickness so printed gears do not bind |
| `servo_spline_d`, `servo_spline_depth`, `servo_screw_d` | 4.8, 3, 2.2 | SG90 21T spline press-fit pocket; horn screw clearance |
| `gear_gap` | 0.5 | servo body top to gear face |
| `servo_win` | [22.6, 11.6] | window through the plate for the SG90 body (fits Jacopo's servo; measure yours) |
| `servo_shaft_from_end` | 6 | shaft axis from the +X end of the body |
| `servo_tab_spacing`, `servo_tab_hole_d`, `servo_boss_d`, `servo_screw_engage` | 27.5, 2.5, 4.1, 8.5 | mounting tabs; bosses on the body side; plate + boss = M2 engagement |
| `servo_frame_w`, `servo_margin` | 0.8, 3 | guide frame around the window; plate outline margin |
| `holder_r_top`, `holder_r_bot` | 6, 10 | plate outline rounds |
| `rib_h`, `rib_depth`, `gusset` | 8, 8, 7 | ribs on the plate's body side and their 45° gusset |
| `sg90_tab_t`, `sg90_top_h`, `sg90_spline_len`, `sg90_body_len`, `sg90_flange_len` | 2.5, 4.3, 3.2, 22.7, 32.2 | SG90 geometry: tab thickness, tab top → case top, spline, case height, tabs tip to tip (the last two for the assembly ghost only) |
| `sh_side_h`, `sh_foot_len`, `sh_foot_chamfer` | 4, 2, 2 | screw holder plate height at the sides, feet toward the body [v2 4: the cart could not reach the last gate], chamfer on the feet's free corner [v2 3 on 4 mm feet], asserted no larger than the foot |
| `outlet_barb`, `outlet_barb_prof`, `outlet_flange` | [4, 6, 7, 14], [3, 5], [10, 4] | bore, shank OD, ridge OD, length; ridge taper length, tip OD; base cone [v2 connector] |
| `inlet_barb`, `inlet_barb_prof` | [8, 10, 12.5, 22], [5, 9.5] | the same for the inlet [v2 connector_8mm] |
| `barb_steep`, `barb_ridges`, `barb_ridge_gap` | 50, 2, 2 | ridge face angle from the axis, number of ridges, shank between taper end and next crest [v2] |
| `end_cap_outlet` | false | an inlet barb through the end cap's front wall for daisy-chaining (modelled; it clashes with the screw gear, the assembly shows it) |
| `washer_od`, `washer_t` | 7, 0.5 | M3 washers on the servo plate (ghosts only) |
| `spring_od`, `spring_wire`, `spring_len`, `spring_turns` | 5.5, 0.5, 10, 6 | the spring on the threadless front of the rod (ghost only) |

## Derived numbers with the defaults (`make report`)

```
pitch = 22, W = 21.2
groove_d = 1.2, groove_od = 7.2, seat_land = 0, seat_boss_h = 0.8, seat_boss_d = 9.6
r_o = 2.75, y_floor = 1.6, y_boss = 2.4, y_ring = 1.95, Rb = 4.75, ball_y = 5.82
k = 3.25, c = 2.91, b = -4.41, D = 6.71, lift = 2.25, throat_area = 25.13
inner_h = 10.6, top_y = 13.8, body_h = 13, gal_y = 6.9
cage_bore = 8.8, cage_od = 11.2, cage_bottom_y = 4.32, cage_window_h = 1.92, seated_gap = 3.98
body_z0 = -4, body_z1 = 110, z_cap0 = -15.6, z_plate1 = -14
gate_z = [9, 31, 53, 75, 97]
screw_y = 19.3, gear_cd = 15, gear_od = 16.5, servo_y = 34.3, win_cx = 5.3, tab_x = [-8.45, 19.05]
gear_z1 = -22.9, gear_z0 = -26.9, rod_z = [-30.3, 113.4], nut_ac = 6.47
ear_t = 4.1, cart_len = 16.3, cart_w = 17.2, cart_top = 23.8
sh_top = 22.5, sh_flat = 3.2
```

Part extents [x, y, z] in the frame: main_body [21.2, 13, 114], lid [21.2, 9.48, 114],
outlet_barb [10, 14, 10], end_cap [21.2, 13.8, 15.6], inlet_cap [19.3, 12.5, 22],
servo_holder [32.65, 29.3, 9.6], screw_holder [21.2, 8.7, 3.6], cart [17.2, 10, 16.3],
servo_gear and screw_gear [16.5, 16.5, 4].

## What to measure on the bench

- **`seated_gap` = 3.98 mm**: magnet face (the lid top) to the top of the seated ball. It
  already includes the 1.6 mm (= `wall`) of lid plate + lip that sits on the centreline between
  magnet and ball, plus `lift` and the layer rounding — see the `seated_gap` line in
  `params.scad`; nothing is to be added to it. The magnet has to lift the ball across this gap
  against the ball's weight and the water pressure on the seat (π·r_o² ≈ 24 mm²: 0.23 N per
  metre of head). Measure the pull of the ø6×3 magnet on the ball through a non-magnetic spacer
  at 3.98 mm (ball seated) and at 3.98 − `lift` = 1.73 mm (ball lifted) with a scale; if it is
  marginal, raise `groove_depth_ratio` or lower `lift_factor` (both bring the ball closer)
  before changing the magnet.
- **`cage_window_h` = 1.92 mm**: the gap between the cage bottom and the seat boss on the printed
  lid + body; a feeler must pass all round, or the water cannot reach the seat.
- **Magnet release**: with the cart parked one gate away the ball must drop; the display rule
  in the assembly (a ball lifts when its gate centre is within `mag_d/2` of the magnet axis) is
  a guess, not a measurement.
- **Home vs gate 0**: the cart can go no further forward than the servo holder ribs
  (`z_plate1 + rib_depth`), which puts the magnet axis `z_plate1 + rib_depth + cart_len/2 - gate_z(0)`
  = 6.85 mm before gate 0 (defaults): more than `mag_d/2`, so a cart parked there holds no ball up.
  The rod's threadless length and the spring decide where home really is: make it end before the
  magnet gets within `mag_d/2` of gate 0, or gate 0 dribbles at rest. `spring_len` is a ghost.
- **Lap skins**: the body's front side skins are `wall/2 - joint_clear` = 0.65 mm, one Arachne line
  on the P2S; they are located by the end cap's 0.8 mm skins and glued. If a print comes out
  ragged there, raise `wall` to 2.0 (everything above it re-derives) rather than thinning the ring.
- **Seal**: fill to 1 m of head; the lid lip glue line and the outlet barbs are the seams to
  watch (see below).

## Assembly and sealing

O-rings into the counterbores, balls onto them, lid lowered so the cages capture the balls;
lid, end cap, inlet cap, outlet barbs and screw holder are **bonded** (CA or epoxy for
PLA/PETG): the lap joints (`joint_clear`) and the plate/wall butt joints are glue joints with a
bead of sealant along the lid lip. The lid must resist ≈ 2 kgf per metre of pump head
(9.8 kPa × 18 × 110 mm² ≈ 19 N at 1 m), so no clips or bare press fits. The lid top stays
flat for the cart. Nut into the cart slot, cart onto the lid, rod through screw holder → cart →
servo holder, spring on the threadless front, nuts and washers each side of the servo plate,
screw gear with its nut outboard, servo gear pressed on the spline and held by the horn
screw, SG90 screwed to the plate from the front.

## Printing (P2S, PLA/PETG, 0.2 mm layers, 0.4 nozzle)

Flat face on the bed, no supports, overhangs ≤ 45°, bridges ≤ 8 mm. `make stl` exports
every part in this orientation.

| part | face on bed | check |
|---|---|---|
| main_body | outside floor (y = 0), flat over the full length | walls and seat bosses vertical, counterbores open up, gallery fillets 45° |
| lid | plate top (y = top_y) | cages stand up, lip fillets are 45° |
| outlet_barb | flange (y = 0 face) | ridge steep faces are 0.5 mm steps |
| end_cap | front wall (z = z_cap0) | cavity and ring open up (with `end_cap_outlet` it is turned over: barb up, front wall bridging) |
| inlet_cap | plug front face (z = body_z1 − joint_len) | barb vertical |
| servo_holder | plate front face (z = z_cap0) | frame, bosses, ribs extrude up; gusset 45° |
| screw_holder | plate back face (z = body_z1), flipped | feet up |
| cart | floor bottom (y = top_y) | ears up, nut slot opens up |
| gears | the pocket-free face | pockets open up |

## Rendering and checking

OpenSCAD 2021.01 at `/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD` (`OPENSCAD=`
overrides it).

```
make            # stl + png
make stl        # build/stl/<part>.stl, each verified to be one solid (Simple: yes, Volumes: 2)
make png        # renders/<part>.png and renders/assembly_<view>.png
make check      # params, every part and the assembly with the defaults and with
                # lift_factor=1, lift_factor=3, ball_d=10, oring_cs=2, n_gates=3, inner_w=20, gear_module=1
make report     # echo every derived number
```

`assembly.scad` takes `-D 'view="iso|length|gate|between|cart|front"'` (sections: keep
x < W/2; z < gate_z(1); z < the joint after gate 1; z < the cart's middle; z < the servo plate's
back face), `-D explode=0..20` (parts move along their assembly directions) and `-D cart_z=`
(the cart's front face; the ball under the magnet is drawn lifted). Each view renders with the
camera the file echoes (`ECHO: camera = "eye,center"`), because `--viewall` fits the uncut
leaves of a sectioned preview. Part files take `-D for_print=true` for the print orientation
and any parameter as `-D name=value`; the assembly `use`s the parts, so a `-D` on it does not
reach them — `make check` substitutes into a copied `params.scad` instead. The assembly pass
runs the asserts of `params.scad` (`include`d) and those inside each part's module — every
part keeps its asserts there because a `use`d file's top-level statements never execute — so
a part-file top-level statement is only exercised by `make check`'s per-part STL exports or by
rendering that part on its own, not by `assembly.scad` in the GUI or by `make png`.

## What differs from valveV2 and why

- Ball gates on O-ring seats replace the inverted-nail plungers: a seat boss with a counterbore
  per gate on the body, cage tubes on the lid instead of plunger guides. The gallery height is
  derived from ball + lift: `top_y` 13.8 (v2 13.2), `body_h` 13.0 (v2 12.4).
- `joint_clear` 0.15 mm per side on every lap joint and the lid lip (v2: 0, does not fit FDM).
- The body's front lap has a full-thickness floor on the bed and only the inner half of each
  side wall; the end cap's ring is just two side skins, no floor skin and no top bar (v2's
  0.8 mm floor skin there floated above the bed); the lid plate extends over the front lap,
  narrowed by `joint_clear`, and closes the ring's top, so the lip and its fillets lie on the
  bed over their whole length instead of hanging 4 mm past the plate.
- The cart's drive nut drops into a top-loading slot in the front ear and cannot turn or move
  axially (v2's through-hex let the rod push the nut out); `ear_top_w` 7.2 (v2 5) to swallow
  it, ears rooted 1.6 mm in from the floor edge, `cart_w` = `inner_w` − 2·`line_w`.
- Screw holder feet 2 mm long (v2 4): with the longer cart the magnet could not reach gate 5.
  Their chamfer is 2 (v2 3): a 45° chamfer cannot exceed the foot, an assert says so. Apex
  half-width 3.2 = hole radius + wall (v2 hard-coded 3.1).
- Gears: same 20T m0.75 pair at 15 mm centres; their plane is derived from the SG90 (tab
  thickness, tab top → case top, `gear_gap`), giving z −26.9..−22.9.
- Outlet barb: the valley between the two ridges returns to the ø6 shank (v2 ø5.5); everything
  else on both barbs matches v2's profiles.
- The body's 1.6 mm fillets along the inner floor/wall corners (`gallery_chamfer`, v2
  large_Chamfer) stop at the lap joints; v2 ran them through the front lap into the end cap's
  square cavity.
- Not reproduced: v2's 0.4 mm lead-in on the ring's inner edges and the 0.4 mm chamfer on the
  wall tops.
- Everything is a parameter or derived from one; a set that cannot be built fails an assert
  with a message.

## Reference files

- `reference/valveV2.FCStd`, `reference/valveV2.step` — the FreeCAD assembly this reproduces.
  Every sketch, constraint and feature was dumped from the FCStd and each body meshed in the
  assembly frame to overlay against these parts; the numbers in [brackets] in `params.scad`
  are v2's.
- `renders/` — one preview per part and the six assembly views, regenerated by `make png`
  (kept under 150 KB each).
- `lib/README.md` — the shared helpers (shapes, barb, O-ring, involute gear).
