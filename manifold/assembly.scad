// assembly.scad — every part of the Plant Butler manifold v3 in the valveV2 frame, with ghosts
// (%) for the hardware that is not printed, section views, an explode slider and the report of
// every derived number.
//
//   openscad -o iso.png assembly.scad                            view = "iso" (whole)
//   openscad -o cart.png -D 'view="cart"' -D cart_z=60 assembly.scad
//   openscad -o apart.png -D explode=15 assembly.scad             parts pulled along their assembly directions
//
// Frame: X across the width (0..W), Y up (0 = outside floor of the main body), Z along the
// manifold, servo end at −Z (front), inlet at +Z (back). Only for the screen the whole scene is
// turned by `screen_rot` so that Y points up (OpenSCAD's camera keeps Z up): no part module is
// touched by that, and every coordinate in this file is in the frame.
//
// Views cut the scene with a box (an intersection with the scene's extents, one face moved):
//   length   keep x < W/2                       the gallery along its length, through every gate
//   gate     keep z < gate_z(view_gate)         across gate 1 (gate 0 if it is the only one): seat, O-ring, ball, cage, cart
//   between  keep z < the joint after gate 1    the plain channel, lip and fillets, rod and cart
//   cart     keep z < the cart's middle         through the magnet, the lifted ball and its cage
//   front    keep z < the servo plate's back    the plate, gears, SG90 and the end cap front wall
//
// The parts are `use`d: each one includes params.scad itself, so a -D on this file does not
// reach them (make check substitutes into a copied params.scad instead).

include <params.scad>
use <lib/shapes.scad>
use <lib/oring.scad>
use <parts/main_body.scad>
use <parts/lid.scad>
use <parts/outlet_barb.scad>
use <parts/end_cap.scad>
use <parts/inlet_cap.scad>
use <parts/servo_holder.scad>
use <parts/screw_holder.scad>
use <parts/cart.scad>
use <parts/servo_gear.scad>
use <parts/screw_gear.scad>

ASSEMBLY = true;    // the convention every part file honours when included instead of used
$fn = fn_round;
eps = 0.01;

// ---- controls ------------------------------------------------------------------------------
view    = "iso";                     // iso | length | gate | between | cart | front
explode = 0;                         // 0..20 mm: how far the parts move along their assembly directions
view_gate = min(1, n_gates - 1);     // the gate the sections cut through: gate 1, or gate 0 when there is only one
cart_z  = gate_z(view_gate) - cart_len/2;   // the cart's front face: by default the magnet is centred over view_gate
screen_rot = [90, 0, 180];           // display only: frame Y → screen Z (up), frame −Z (front) toward the viewer

views = ["iso", "length", "gate", "between", "cart", "front"];
assert(len([for (v = views) if (v == view) v]) == 1, str("assembly: view must be one of ", views));
assert(explode >= 0 && explode <= 20, "assembly: explode is 0..20 mm");
assert(cart_z >= z_plate1 && cart_z + cart_len <= body_z1 - wall - sh_foot_len + num_tol,
       "assembly: cart_z puts the cart into the servo plate or the screw holder's feet");

// ---- what the ghosts need -------------------------------------------------------------------
mag_z = cart_z + cart_len/2;                                  // magnet axis
// display rule: the magnet lifts the ball whose gate centre lies under the magnet's face
function lifted(i) = abs(gate_z(i) - mag_z) <= mag_d/2;
sg90_top_z  = z_cap0 - sg90_tab_t - sg90_top_h;               // case top (shaft side), gear_gap in front of the servo gear
sg90_tab_z0 = z_cap0 - sg90_tab_t;                            // tabs lie on the plate's front face
plate_nut_front = z_cap0 - washer_t - nut_t;                  // nut + washer on each face of the servo plate
plate_nut_back  = z_plate1 + washer_t;
spring_z0 = plate_nut_back + nut_t;                           // the spring bears on the back nut
spring_drawn = min(spring_len, cart_z - spring_z0);           // compressed only when the cart is home against it
assert(spring_drawn > spring_turns*spring_wire, "assembly: cart_z squashes the spring solid: it is home already");

// scene extents, ghosts included, for the section boxes (explode moves parts at most explode_far out)
explode_far = 3;
asm_x = [min(tab_x[0] - servo_margin, win_cx - sg90_flange_len/2), max(W, win_cx + sg90_flange_len/2)];
asm_y = [-outlet_barb[3], max(servo_y + servo_win.y/2 + servo_margin, servo_y + gear_od(servo_teeth)/2)];
asm_z = [rod_z[0], body_z1 - joint_len + inlet_barb[3]];

// [axis index, cut coordinate] of the view's section plane, undef for iso
function cut() =
    view == "length"  ? [0, W/2] :
    view == "gate"    ? [2, gate_z(view_gate)] :
    view == "between" ? [2, gate_z(view_gate) + gate_len/2 + joint_len/2] :
    view == "cart"    ? [2, mag_z] :
    view == "front"   ? [2, z_plate1] : undef;

// the box the view keeps: the scene's extents, one face moved to the section plane. Below
// y = 0 there are only the outlet barbs, so a cut in front of the first one lifts the floor.
function kept_hi() = let(c = cut(), hi = [asm_x[1], asm_y[1], asm_z[1]] + explode_far*explode*[1, 1, 1])
    [for (a = [0 : 2]) !is_undef(c) && a == c[0] ? c[1] : hi[a]];
function kept_lo() = let(barbs_kept = kept_hi().z > gate_z(0) - outlet_flange[0]/2)
    [asm_x[0], barbs_kept ? asm_y[0] : 0, asm_z[0]] - explode_far*explode*[1, 1, 1];

// keep only the side of the section plane the view names (all of it for iso). The box wears
// the part's colour and opacity: in preview a cut face shows the colour of the solid whose
// face it is, and that is the box's. Each call passes its own `id`: the box shrinks by id·eps,
// so no two parts have coplanar cut faces — coplanar ones fight for the pixels in the
// preview's colour pass and every cut face would come out in one part's colour.
module sectioned(col, alpha=1, id=0) {
    if (is_undef(cut())) color(col, alpha) children();
    else intersection() {
        color(col, alpha) children();
        color(col, alpha) translate(kept_lo()) cube(kept_hi() - kept_lo() - [1, 1, 1]*id*eps);
    }
}

// ---- camera for the renders -----------------------------------------------------------------
// The Makefile renders each view with the camera echoed here, because --viewall cannot be
// used: in preview it fits every leaf solid, cut away or not. Eye directions are in screen
// coordinates (after screen_rot, Z up); the zoom fits the kept box's projection with cam_margin
// around it. OpenSCAD's vector camera has a fixed 22.5° field of view and in orthographic
// projection shows a half-height of (eye distance)·tan(fov/2): calibrated, not documented.
img_aspect = 1200/900;                   // the Makefile's IMG
cam_fov = 22.5;
cam_margin = 0.08;
function screen(p) = [-p.x, p.z, p.y];   // rotate(screen_rot) applied to a point
function unit(v) = v/norm(v);
function eye_dir() =
    view == "iso"    ? unit([0.75, -0.75, 0.5]) :    // front, the servo holder's overhang side, above
    view == "length" ? unit([-0.8, -0.7, 0.5]) :     // from the cut face's side (frame +X)
    view == "front"  ? unit([0.45, -0.8, 0.45]) :    // gears and SG90 from the front
    view == "cart"   ? unit([0.45, 0.8, 0.45]) :     // the cut face obliquely, from the back
    [0, 1, 0];                                       // gate, between: true section drawings, seen from the back
cam_f = -eye_dir();
cam_r = unit(cross(cam_f, [0, 0, 1]));   // screen right
cam_u = cross(cam_r, cam_f);             // screen up
cam_pts = [for (i = [0 : 7]) screen([i%2 ? kept_hi().x : kept_lo().x, floor(i/2)%2 ? kept_hi().y : kept_lo().y, i >= 4 ? kept_hi().z : kept_lo().z])];
cam_pr = [for (p = cam_pts) p*cam_r];  cam_pu = [for (p = cam_pts) p*cam_u];  cam_pf = [for (p = cam_pts) p*cam_f];
cam_half_h = max((max(cam_pu) - min(cam_pu))/2, (max(cam_pr) - min(cam_pr))/2/img_aspect)*(1 + cam_margin);
cam_dist = cam_half_h/tan(cam_fov/2);
cam_center = cam_r*(max(cam_pr) + min(cam_pr))/2 + cam_u*(max(cam_pu) + min(cam_pu))/2 + cam_f*(max(cam_pf) + min(cam_pf))/2;
cam_eye = cam_center - cam_f*cam_dist;

// ---- hardware ghosts -----------------------------------------------------------------------
// an M3 nut on the rod, `z0` its −Z face, flats vertical like the cart slot and the gear trap
module nut_on_rod(z0) { translate([W/2, screw_y, z0]) rotate([0, 0, 90]) hex(nut_af, nut_t); }
module washer_on_rod(z0) { translate([W/2, screw_y, z0]) difference() {
    cylinder(d=washer_od, h=washer_t); translate([0, 0, -eps]) cylinder(d=screw_hole_d, h=washer_t + 2*eps); } }

module ghost_balls() {
    for (i = [0 : n_gates - 1])
        translate([W/2, ball_y + (lifted(i) ? lift : 0), gate_z(i)]) sphere(d=ball_d);
}
module ghost_orings() {
    for (i = [0 : n_gates - 1]) translate([W/2, y_ring, gate_z(i)]) rotate([90, 0, 0]) oring(oring_id, oring_cs);
}
module ghost_magnet() { translate([W/2, top_y, mag_z]) rotate([-90, 0, 0]) cylinder(d=mag_d, h=mag_h); }
module ghost_rod() { translate([W/2, screw_y, rod_z[0]]) cylinder(d=screw_d, h=rod_z[1] - rod_z[0]); }
module ghost_cart_nut() { nut_on_rod(cart_z + ear_t/2 - nut_t/2); }          // centred in the front ear's slot
module ghost_gear_nuts() {                                                    // trapped in the gear, and the outboard clamp
    nut_on_rod(gear_z0); washer_on_rod(gear_z0 - washer_t); nut_on_rod(gear_z0 - washer_t - nut_t);   // through a washer: the nut alone fits inside the trap outline
}
module ghost_plate_nuts() {
    nut_on_rod(plate_nut_front); washer_on_rod(z_cap0 - washer_t);
    nut_on_rod(plate_nut_back);  washer_on_rod(z_plate1);
}
// coil on the rod from the back plate nut toward the cart, drawn at its free length unless the
// cart is closer (home): a twisted extrusion of the wire's section
module ghost_spring() {
    translate([W/2, screw_y, spring_z0])
        linear_extrude(spring_drawn, twist=-360*spring_turns, slices=spring_turns*fn_small)
            translate([(spring_od - spring_wire)/2, 0]) circle(d=spring_wire, $fn=fn_small);
}
// SG90: case through the window toward +Z, tabs against the plate's front face, spline into the gear
module ghost_sg90() {
    translate([win_cx - servo_win.x/2, servo_y - servo_win.y/2, sg90_top_z]) cube([servo_win.x, servo_win.y, sg90_body_len]);
    difference() {
        translate([win_cx - sg90_flange_len/2, servo_y - servo_win.y/2, sg90_tab_z0]) cube([sg90_flange_len, servo_win.y, sg90_tab_t]);
        for (x = tab_x) translate([x, servo_y, sg90_tab_z0 - eps]) cylinder(d=servo_tab_hole_d, h=sg90_tab_t + 2*eps, $fn=fn_small);
    }
    translate([W/2, servo_y, sg90_top_z - sg90_spline_len]) cylinder(d=servo_spline_d, h=sg90_spline_len, $fn=fn_small);
}

// ---- the scene ------------------------------------------------------------------------------
// Explode directions are the assembly directions: the lid, cart and magnet come down onto the
// body (+Y), the barbs go up under the floor (−Y), the end cap and everything on the servo end
// slide on from the front (−Z), the inlet cap and the screw holder from the back (+Z).
module scene() {
    ex = explode;
    sectioned("royalblue", id=1)        main_body();
    sectioned("pink", id=2)             translate([0, ex, 0]) lid();
    sectioned("deepskyblue", id=3)      for (i = [0 : n_gates - 1]) translate([0, -ex, 0]) outlet_barb(i);
    sectioned("mediumaquamarine", id=4) translate([0, 0, -ex]) end_cap();
    sectioned("orchid", id=5)           translate([0, 0, ex]) inlet_cap();
    sectioned("orange", id=6)           translate([0, 0, -ex]) servo_holder();      // bonded to the end cap: moves with it
    sectioned("gold", id=7)             translate([0, ex, ex]) screw_holder();
    sectioned("gray", id=8)             translate([0, 2*ex, cart_z]) cart();
    sectioned("tomato", id=9)           translate([0, 0, -explode_far*ex]) servo_gear();
    sectioned("yellowgreen", id=10)      translate([0, 0, -explode_far*ex]) screw_gear();

    %sectioned("silver", 0.6, id=11)      translate([0, ex/2, 0]) ghost_balls();
    %sectioned("black", 0.5, id=12)       translate([0, ex/4, 0]) ghost_orings();
    %sectioned("dimgray", 0.6, id=13)     translate([0, 2.5*ex, 0]) ghost_magnet();
    %sectioned("silver", 0.6, id=14)      translate([0, 2.5*ex, 0]) ghost_cart_nut();
    %sectioned("silver", 0.6, id=15)      ghost_rod();
    %sectioned("silver", 0.6, id=16)      translate([0, 0, -explode_far*ex]) ghost_gear_nuts();
    %sectioned("silver", 0.6, id=17)      translate([0, 0, -2*ex]) ghost_plate_nuts();
    %sectioned("silver", 0.6, id=18)      ghost_spring();
    %sectioned("dodgerblue", 0.35, id=19) translate([0, 0, -2*ex]) ghost_sg90();
}

rotate(screen_rot) scene();

// ---- report ---------------------------------------------------------------------------------
report();
echo(main_body_size=main_body_size(), lid_size=lid_size(), outlet_barb_size=outlet_barb_size(),
     end_cap_size=end_cap_size(), inlet_cap_size=inlet_cap_size());
echo(servo_holder_size=servo_holder_size(), screw_holder_size=screw_holder_size(), cart_size=cart_size(),
     servo_gear_size=servo_gear_size(), screw_gear_size=screw_gear_size());
echo(view=view, explode=explode, cart_z=cart_z, mag_z=mag_z, lifted=[for (i = [0 : n_gates - 1]) if (lifted(i)) i],
     spring_drawn=spring_drawn, asm_x=asm_x, asm_y=asm_y, asm_z=asm_z);
// the Makefile reads this line: --camera=eye,center for the view
echo(camera=str(cam_eye.x, ",", cam_eye.y, ",", cam_eye.z, ",", cam_center.x, ",", cam_center.y, ",", cam_center.z));
