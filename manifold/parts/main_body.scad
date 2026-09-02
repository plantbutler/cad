// parts/main_body.scad — the water gallery: a U-channel open at the top with one O-ring seat
// per gate. Reproduces valveV2's main_body (sketches center / extension_outie /
// extension_innie, plunger_hole, LinearPattern 5×pitch) with the brief's changes:
//   - the front lap joint has a full floor standing on the bed (v2's 0.8 skin floated above it)
//     and only the inner half of each side wall, with joint_clear toward the end cap's ring;
//   - the chamfered nail seat is now a seat boss with an O-ring counterbore;
//   - v2's large_Chamfer (the 45° fillets along the inner floor/wall corners) is kept between
//     the lap joints only (v2 ran it through the front lap, into the end cap's square cavity).
// Frame: X across (0..W), Y up (0 = outside floor), Z along (body_z0..body_z1).
include <../params.scad>
use <../lib/shapes.scad>
use <../lib/oring.scad>
$fn = fn_round;
for_print = false;
eps = 0.01;   // overlap between unioned solids / overshoot of cutters: no coincident CGAL faces

// [x, y, z] extents in the assembly frame
function main_body_size() = [W, body_h, body_z1 - body_z0];

module main_body() {
    x_lap  = wall/2 + joint_clear;      // front lap: the end cap's ring is the outer half of the wall
    z_full = body_z1 - joint_len;       // full walls from z=0 to here; laps on either side
    difference() {
        union() {
            // the channel: full walls between the two lap joints, open at the top
            difference() {
                cube([W, body_h, z_full]);
                translate([0, 0, -eps]) linear_extrude(z_full + 2*eps) gallery_section();
            }
            // front lap z∈[body_z0, 0]: full floor (it stands on the bed and butts the end cap
            // block) and the inner half-skins of the side walls; the ring's skins wrap them
            translate([0, 0, body_z0]) {
                translate([x_lap, 0, 0]) cube([W - 2*x_lap, wall, joint_len + eps]);
                for (x = [x_lap, W - wall]) translate([x, 0, 0]) cube([wall - x_lap, body_h, joint_len + eps]);
            }
            // back lap z∈[body_z1 − joint_len, body_z1]: the outer half-skins only, the inlet
            // plug fills the inner half [v2 extension_outie]
            translate([0, 0, z_full - eps]) {
                cube([W, wall/2, joint_len + eps]);
                for (x = [0, W - wall/2]) translate([x, 0, 0]) cube([wall/2, body_h, joint_len + eps]);
            }
            // seat bosses: raise the O-ring groove so seat_floor_min stays under it
            if (seat_boss_h > 0) for (i = [0 : n_gates - 1])
                translate([W/2, wall - eps, gate_z(i)]) rotate([-90, 0, 0])
                    cylinder(d=seat_boss_d, h=seat_boss_h + eps, $fn=fn_small);
        }
        // per gate: outlet hole through floor and boss, counterbore for the O-ring in the top
        // (rotate −90 about X points the cutters' +Z up the +Y axis)
        for (i = [0 : n_gates - 1]) translate([W/2, 0, gate_z(i)]) rotate([-90, 0, 0]) {
            translate([0, 0, -eps]) cylinder(d=outlet_id, h=y_boss + 2*eps);
            translate([0, 0, y_boss]) oring_counterbore(oring_id, oring_cs, groove_clear, groove_d, eps);
        }
    }
}

// The gallery's cross-section (a cutter): x∈[wall, W−wall] from the floor past the open top,
// its two floor corners cut at 45° by gallery_chamfer. What the body keeps in those corners is
// the fillet [v2 large_Chamfer]; at 45° it needs no support printed floor-down. The seat boss
// edge is at W/2 − seat_boss_d/2, beyond the fillet's toe at wall + gallery_chamfer (params.scad asserts it).
module gallery_section() {
    c = gallery_chamfer;
    polygon(c > 0
        ? [[wall + c, wall], [W - wall - c, wall], [W - wall, wall + c],
           [W - wall, body_h + eps], [wall, body_h + eps], [wall, wall + c]]
        : [[wall, wall], [W - wall, wall], [W - wall, body_h + eps], [wall, body_h + eps]]);
}

// outside floor (y=0) on the bed: walls, bosses and fillets vertical, counterbores open up
module main_body_print() { translate([0, body_z1, 0]) rotate([90, 0, 0]) main_body(); }

if (is_undef(ASSEMBLY)) {
    echo(main_body_size=main_body_size());
    if (for_print) main_body_print(); else main_body();
}
