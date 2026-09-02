// Plant Butler manifold v3 — the parameter contract. Every file `include`s this and every
// dimension anywhere is an expression of these names; nothing is typed twice.
//
// Frame: X across the width (0..W), Y up (0 = outside bottom of the main body), Z along the
// manifold; the servo end is the front (−Z), the inlet end the back (+Z).
// Numbers in [brackets] are valveV2's (reference/valveV2.FCStd).

// ---- printer -------------------------------------------------------------------------------
line_w  = 0.4;    // extrusion width: thin frames and skins are multiples of it
layer_h = 0.2;    // heights that must land on a layer are rounded UP to a multiple of it
fn_round = 64;    // $fn for anything that seals or runs: bores, barbs, cages, gears, balls
fn_small = 32;    // $fn for screw holes, bosses and other small round features

// ---- layout [v2] ---------------------------------------------------------------------------
n_gates   = 5;      // number of outputs
gate_len  = 18;     // gallery length per gate [v2 innerBoxLength]
joint_len = 4;      // lap joint length between body, lid, caps [v2 boxConnections]
wall      = 1.6;    // every wall = 4 perimeters; lap joints split it into two half-skins
inner_w   = 18;     // gallery width [v2 innerBoxWidth]
extra_len = 10;     // end cap cavity in front of the body: room for the water to turn [v2 extraLength]
joint_clear = 0.15;       // per-side clearance on lap joints and the lid lip (v2 had 0: does not fit FDM)
lip_chamfer = 4*line_w;   // 45° fillets under the lid lip [v2 internal_chamfer 1.6]
gallery_chamfer = 4*line_w;   // 45° fillets along the gallery's inner floor/wall corners [v2 large_Chamfer 1.6]: 45° so it prints floor-down

// ---- ball gate (new in v3) ------------------------------------------------------------------
ball_d    = 8;      // 440C ball
outlet_id = 4;      // outlet hole through the floor
oring_id  = 4;      // O-ring inner diameter: its ID sits at the outlet hole edge
oring_cs  = 1.5;    // O-ring cross-section
groove_depth_ratio = 0.75;  // groove depth as a fraction of the cross-section: the ball must touch the ring, not the step
groove_clear   = 0.2;       // radial slack on the counterbore so the ring drops in
seat_floor_min = 1.2;       // material left under the groove: 6 layers
seat_boss_wall = 1.2;       // material around the groove: 3 perimeters
lift_factor = 2;            // throat area under the lifted ball = lift_factor × outlet bore area
cage_clear = 0.4;           // radial slack ball ↔ cage bore, so a rough print cannot pinch the ball
cage_wall  = 1.2;           // cage tube wall: 3 perimeters
cage_below_equator = 1.5;   // cage reaches this far below the seated ball centre: it cannot escape sideways
cage_window_min = 1.5;      // minimum gap cage bottom ↔ seat boss for the water to enter
cage_side_gap  = 1.0;       // minimum gap cage OD ↔ gallery wall each side
lid_slot_depth = 0;         // optional groove along the lid top for the magnet (0 = flat top as v2)

// ---- magnet and cart [v2 magDiameter 6.1 was the hole] -------------------------------------
mag_d = 6;  mag_h = 3;      // ø6×3 disc magnet
mag_clear  = 0.1;           // on the hole diameter: press fit
mag_margin = 1.0;           // floor material each side of the magnet hole
ear_h = 7;                  // ear height above the cart floor top
ear_top_w = 7.2;            // ear width at the top [v2 5]: must swallow the nut slot plus 2 perimeters each side
ear_base_inset = 4*line_w;  // ears root this far in from the floor edge [v2 1.6]

// ---- lead screw [v2] -----------------------------------------------------------------------
screw_h = 5.5;              // rod axis above the lid top
screw_d = 3;  screw_hole_d = 3.2;   // M3 rod and its clearance hole
nut_af = 5.5;  nut_clear = 0.1;  nut_t = 2.4;   // M3 nut across flats, slot clearance, thickness

// ---- gears [gears.FCStd: two identical, OD 16.5, 4 thick, centre distance 15] --------------
gear_module = 0.75;  servo_teeth = 20;  screw_teeth = 20;  gear_t = 4;
gear_backlash = 0.1;        // taken off each tooth thickness so printed gears do not bind
pressure_angle = 20;
servo_spline_d = 4.8;  servo_spline_depth = 3;   // SG90 21T spline: press-fit pocket in the servo gear
servo_screw_d = 2.2;        // horn screw clearance through the rest of the servo gear
gear_gap = 0.5;             // servo body top to gear face

// ---- SG90 [v2 servo_holder] ----------------------------------------------------------------
servo_win = [22.6, 11.6];   // window through the plate for the body, x × y (v2 fits Jacopo's servo; measure yours)
servo_shaft_from_end = 6;   // shaft axis 6 mm from the +X end of the body
servo_tab_spacing = 27.5;  servo_tab_hole_d = 2.5;   // mounting tab holes
servo_boss_d = 4.1;         // bosses around the tab holes on the body side [v2 servo_spacer]
servo_screw_engage = 8.5;   // plate + boss = M2 screw engagement [v2 8.5 − wall pad]
servo_frame_w = 2*line_w;   // guide frame around the window on the +Z side
servo_margin = 3;           // plate outline margin around window and tab holes
holder_r_top = 6;  holder_r_bot = 10;   // plate outline rounds, left top / left bottom
rib_h = 8;  rib_depth = 8;  gusset = 7; // ribs on the plate's body side and their 45° gusset
sg90_tab_t = 2.5;  sg90_top_h = 4.3;  sg90_spline_len = 3.2;   // tab thickness, tab top→body top, spline
sg90_body_len = 22.7;       // case height from its top (shaft side) down along the shaft axis: assembly ghost only
sg90_flange_len = 32.2;     // mounting tabs tip to tip: assembly ghost only

// ---- screw holder [v2] ---------------------------------------------------------------------
sh_side_h = 4;              // plate height at the sides above the lid
sh_foot_len = 2;            // feet toward the body [v2 4: the cart could not reach gate 5 with a longer cart]
sh_foot_chamfer = 2;        // chamfer on the feet's free corner [v2 3 on 4 mm feet: a 45° chamfer cannot exceed sh_foot_len]

// ---- barbs [v2 connector / connector_8mm profiles] -----------------------------------------
outlet_barb = [outlet_id, 6, 7, 14];   // bore, shank OD, ridge OD, length
outlet_barb_prof = [3, 5];             // ridge taper length, tip OD
outlet_flange = [10, 4];               // base cone ø10→shank over 4 mm (v2 exitSupport)
inlet_barb  = [8, 10, 12.5, 22];  inlet_barb_prof = [5, 9.5];
barb_steep = 50;            // ridge face angle from the axis on the flange side [v2 130° interior]
barb_ridges = 2;
barb_ridge_gap = 2;         // shank between one ridge's taper end and the next crest [v2: 2 in both sketches]
end_cap_outlet = false;     // true: an inlet_barb through the end cap's front wall for daisy-chaining

// ---- other non-printed hardware (assembly ghosts and the README only) -----------------------
washer_od = 7;  washer_t = 0.5;                     // M3 washers under the nuts on the servo plate
spring_od = 5.5;  spring_wire = 0.5;  spring_len = 10;  spring_turns = 6;   // compression spring on the threadless front of the rod: ID clears M3

// ============================================================================================
// Derived values. Guarded by asserts: a parameter set that cannot be built fails here with a
// message, never silently. num_tol absorbs floating point noise in ceil() and >= comparisons.
// ============================================================================================
num_tol = 1e-6;
function layers_up(h) = ceil(h/layer_h - num_tol)*layer_h;   // smallest multiple of layer_h >= h
function gate_z(i) = i*pitch + gate_len/2;                    // centre of gate i (0-based) [v2 9, 31, 53, 75, 97]
function gear_od(t) = gear_module*(t + 2);                     // tip diameter of a t-tooth gear

// -- layout
pitch = gate_len + joint_len;                                  // 22
W = inner_w + 2*wall;                                          // 21.2

// -- O-ring seat: the counterbore's inner wall is the outlet hole edge
groove_d  = layers_up(oring_cs*groove_depth_ratio);            // 1.2 (lands on a layer)
groove_od = oring_id + 2*oring_cs + groove_clear;              // 7.2
seat_land = (oring_id - outlet_id)/2;                          // 0: ring ID flush with the hole
assert(seat_land >= -num_tol, "oring_id < outlet_id: the O-ring would overhang the outlet hole");
seat_boss_h = layers_up(max(0, groove_d + seat_floor_min - wall));   // 0.8: boss only as tall as the floor is short
seat_boss_d = groove_od + 2*seat_boss_wall;                    // 9.6
assert(gallery_chamfer >= 0 && gallery_chamfer <= inner_w/2 - seat_boss_d/2 + num_tol, "gallery_chamfer negative or reaching the seat boss: shrink it or widen inner_w");
r_o = (oring_id + oring_cs)/2;                                 // 2.75 O-ring centreline radius
y_floor = wall;                                                // 1.6 gallery floor
y_boss  = wall + seat_boss_h;                                  // 2.4 seat boss top
y_ring  = y_boss - groove_d + oring_cs/2;                      // 1.95 O-ring tube centre plane
Rb = ball_d/2 + oring_cs/2;                                    // 4.75 ball centre ↔ tube centre, touching
ball_y = y_ring + sqrt(Rb*Rb - r_o*r_o);                       // 5.82 seated ball centre (abs Y)
assert(Rb > r_o, "ball smaller than the O-ring opening: it falls through");

// -- lift: the throat is the frustum between the closest points of O-ring tube and ball on
//    their line of centres (distance D); throat = π r_o (1 + k/D)(D − Rb) = lift_factor·π(outlet_id/2)²
k = ball_d/2 - oring_cs/2;
c = lift_factor*(outlet_id/2)*(outlet_id/2)/r_o;
b = k - Rb - c;
D = (-b + sqrt(b*b + 4*k*Rb))/2;                               // 6.71
lift = sqrt(D*D - r_o*r_o) - sqrt(Rb*Rb - r_o*r_o);            // 2.25
throat_area = PI*r_o*(1 + k/D)*(D - Rb);
assert(throat_area >= PI*(outlet_id/2)*(outlet_id/2) - num_tol, "lifted throat smaller than the outlet bore");

// -- gallery height: the lifted ball just touches the lid lip
inner_h = layers_up(ball_y + ball_d/2 + lift - wall);          // 10.6
top_y  = 2*wall + inner_h;                                     // 13.8 lid top [v2 13.2]
body_h = top_y - wall/2;                                       // 13.0 main body outer height [v2 12.4]
gal_y  = wall + inner_h/2;                                     // 6.9 gallery axis: the inlet barbs (and the end cap outlet) sit on it

// -- cage
cage_bore = ball_d + 2*cage_clear;                             // 8.8
cage_od   = cage_bore + 2*cage_wall;                           // 11.2
cage_bottom_y  = ball_y - cage_below_equator;                  // 4.32
cage_window_h  = cage_bottom_y - y_boss;                       // 1.92 water enters under the cage here
assert(cage_window_h >= cage_window_min - num_tol, "cage bottom too close to the seat boss: window below cage_window_min");
assert(PI*cage_bore*cage_window_h >= PI*(outlet_id/2)*(outlet_id/2) - num_tol, "cage window area smaller than the outlet bore");
assert(cage_bore > groove_od, "cage bore narrower than the O-ring groove: the cage would sit on the ring");
assert(cage_od + 2*cage_side_gap <= inner_w + num_tol, "cage too wide for the gallery");
assert(cage_bottom_y > y_boss, "cage bottom below the seat boss top");
// magnet face → ball top with the ball seated: the bench number. Equals wall + lift plus the
// layer rounding of inner_h (0.13 with the defaults), measured from the lid top the magnet rides on.
seated_gap = top_y - lid_slot_depth - (ball_y + ball_d/2);     // 3.98

// -- length
body_z0 = -joint_len;  body_z1 = n_gates*pitch;                // −4 .. 110
z_cap0   = -(joint_len + wall + extra_len);                    // −15.6 end cap front face = servo plate front face
z_plate1 = z_cap0 + wall;                                      // −14 servo plate back face

// -- rod, gears, servo
screw_y = top_y + screw_h;                                     // 19.3 rod axis
gear_cd = gear_module*(servo_teeth + screw_teeth)/2;           // 15 centre distance
servo_y = screw_y + gear_cd;                                   // 34.3 servo shaft axis
win_cx  = W/2 - servo_win.x/2 + servo_shaft_from_end;          // 5.3 window centre x (shaft on x = W/2)
tab_x   = [win_cx - servo_tab_spacing/2, win_cx + servo_tab_spacing/2];   // −8.45, 19.05
gear_z1 = z_cap0 - sg90_tab_t - sg90_top_h - gear_gap;         // −22.9 gear face nearest the servo
gear_z0 = gear_z1 - gear_t;                                    // −26.9 outer gear face
// The spline must not bottom in the pocket before the gear reaches gear_gap (the brief wrote
// this the other way round, which no SG90 satisfies: the spline is shorter than gap + pocket).
assert(sg90_spline_len <= gear_gap + servo_spline_depth + num_tol, "SG90 spline longer than gear_gap + servo_spline_depth: the gear cannot seat");
rod_z = [gear_z0 - nut_t - 1, body_z1 + nut_t + 1];            // −30.3 .. 113.4: a nut and 1 mm of thread past each end
nut_ac = (nut_af + nut_clear)/cos(30);                         // 6.47 across corners with clearance

// -- cart
ear_t = nut_t + nut_clear + 4*line_w;                          // 4.1 nut slot plus 2 perimeters each side
cart_len = 2*ear_t + mag_d + mag_clear + 2*mag_margin;         // 16.3
cart_w   = inner_w - 2*line_w;                                 // 17.2 rides between the lid's lip lines
cart_top = top_y + mag_h + ear_h;                              // 23.8
assert(ear_top_w + num_tol >= nut_af + nut_clear + 4*line_w, "ear_top_w too narrow for the nut slot plus 2 perimeters each side");
assert(screw_h - nut_ac/2 >= 1.2 - num_tol, "nut slot would cut through the cart floor: raise screw_h");
assert(servo_y - servo_win.y/2 >= cart_top + 1 - num_tol, "servo body would hit the cart ears");
assert(screw_y - gear_od(screw_teeth)/2 > 0, "screw gear would hit the bed plane: gears must hang free outboard");

// -- screw holder
sh_top  = screw_y + screw_hole_d/2 + wall;                     // 22.5 plate apex: one wall above the rod hole
sh_flat = screw_hole_d/2 + wall;                               // 3.2 half-width of the flat apex
assert(body_z1 - wall - sh_foot_len - cart_len/2 >= gate_z(n_gates-1) - num_tol, "cart cannot reach the last gate: shorten sh_foot_len or the cart");
assert(z_plate1 + rib_depth + cart_len/2 <= gate_z(0) + num_tol, "cart cannot reach the first gate: shorten rib_depth or the cart");

// Echo every derived number with its name (ECHO: name = value).
module report() {
    echo(pitch=pitch, W=W);
    echo(groove_d=groove_d, groove_od=groove_od, seat_land=seat_land, seat_boss_h=seat_boss_h, seat_boss_d=seat_boss_d);
    echo(r_o=r_o, y_floor=y_floor, y_boss=y_boss, y_ring=y_ring, Rb=Rb, ball_y=ball_y);
    echo(k=k, c=c, b=b, D=D, lift=lift, throat_area=throat_area);
    echo(inner_h=inner_h, top_y=top_y, body_h=body_h, gal_y=gal_y);
    echo(cage_bore=cage_bore, cage_od=cage_od, cage_bottom_y=cage_bottom_y, cage_window_h=cage_window_h, seated_gap=seated_gap);
    echo(body_z0=body_z0, body_z1=body_z1, z_cap0=z_cap0, z_plate1=z_plate1);
    echo(gate_z=[for (i=[0:n_gates-1]) gate_z(i)]);
    echo(screw_y=screw_y, gear_cd=gear_cd, gear_od=gear_od(screw_teeth), servo_y=servo_y, win_cx=win_cx, tab_x=tab_x);
    echo(gear_z1=gear_z1, gear_z0=gear_z0, rod_z=rod_z, nut_ac=nut_ac);
    echo(ear_t=ear_t, cart_len=cart_len, cart_w=cart_w, cart_top=cart_top);
    echo(sh_top=sh_top, sh_flat=sh_flat);
}
