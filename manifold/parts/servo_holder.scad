// parts/servo_holder.scad — the front plate that carries the SG90 and the front rod bearing
// [v2 Body007: sketches back_plate, supports, servo_spacer].
//
// A plate `wall` thick perpendicular to Z at z∈[z_cap0, z_plate1], its front face flush with
// the end cap's front face, standing on the end cap top (y = top_y). The outline is derived
// from the servo window: `servo_margin` past the left tab hole and above the window, the
// right edge flush with the body at x = W, two rounds on the left corners. On the body (+Z)
// side: a `servo_frame_w` guide frame around the window and ø`servo_boss_d` bosses on the tab
// holes, both `servo_screw_engage − wall` tall (plate + boss = M2 engagement), and two ribs
// on the end cap's side walls with a 45° gusset on the free top corner (v2 Chamfer007: the rib
// keeps its full height for rib_depth − gusset, then falls to rib_h − gusset at the free end).
// The SG90 mounts from the front: tabs on the −Z face, body through the window toward +Z,
// shaft toward −Z into the gears at z∈[gear_z0, gear_z1].

include <../params.scad>
use <../lib/shapes.scad>
$fn = fn_round;
eps = 0.01;

// ---- outline in the plate plane (x, y) ---------------------------------------------------
svh_x0 = tab_x[0] - servo_margin;                  // left edge: margin past the left tab hole [v2 −11.45]
svh_x1 = W;                                        // right edge flush with the body's side
svh_y0 = top_y;                                    // stands on the end cap top
svh_y1 = servo_y + servo_win.y/2 + servo_margin;   // margin above the window [v2 43.5]
svh_boss_h = servo_screw_engage - wall;            // frame and boss height: plate + boss = screw engagement [v2 6.9]
svh_depth = wall + max(rib_depth, svh_boss_h);     // total extent along Z from the front face
svh_win = [win_cx - servo_win.x/2, win_cx + servo_win.x/2, servo_y - servo_win.y/2, servo_y + servo_win.y/2];   // window x0, x1, y0, y1
svh_r = max(holder_r_top, holder_r_bot);           // the outline's rectangle starts past the larger round

// 2D plate outline: the hull of the two left rounds and the rectangle to the right of them.
// Both rounds touch x = svh_x0, so the hull's left edge is the straight line between them.
module servo_holder_outline() {
    hull() {
        translate([svh_x0 + holder_r_top, svh_y1 - holder_r_top]) circle(r=holder_r_top);
        translate([svh_x0 + holder_r_bot, svh_y0 + holder_r_bot]) circle(r=holder_r_bot);
        translate([svh_x0 + svh_r, svh_y0]) square([svh_x1 - svh_x0 - svh_r, svh_y1 - svh_y0]);
    }
}

// One rib on the plate's body side, x∈[0, wall]: full height rib_h for rib_depth − gusset,
// then a 45° gusset down to rib_h − gusset at the free end. Profile drawn in (y, z), extruded
// along +X (rotate([90,0,90]) maps 2D (u, v) and the extrusion w onto (w, u, v)).
module servo_holder_rib() {
    rotate([90, 0, 90]) linear_extrude(wall)
        polygon([[svh_y0, z_plate1], [svh_y0 + rib_h, z_plate1],
                 [svh_y0 + rib_h, z_plate1 + rib_depth - gusset],
                 [svh_y0 + rib_h - gusset, z_plate1 + rib_depth],
                 [svh_y0, z_plate1 + rib_depth]]);
}

// The asserts live inside the module, not at file top level: `use <servo_holder.scad>` (assembly.scad)
// imports modules, functions and variables but does not execute top-level statements, so a
// file-top assert would be silent in the assembly and only fire on a standalone render.
module servo_holder() {
    assert(holder_r_top + holder_r_bot <= svh_y1 - svh_y0 + num_tol, "servo_holder: the two left rounds overlap: lower holder_r_top/holder_r_bot");
    assert(max(holder_r_top, holder_r_bot) <= svh_x1 - svh_x0 + num_tol, "servo_holder: a left round is wider than the plate");
    assert(tab_x[1] + servo_boss_d/2 <= svh_x1 + num_tol, "servo_holder: the right tab boss sticks out past the plate edge x = W");
    assert(svh_win[1] + servo_frame_w <= svh_x1 + num_tol, "servo_holder: the window frame sticks out past the plate edge x = W");
    assert(screw_y + screw_hole_d/2 < svh_win[2] - servo_frame_w - num_tol, "servo_holder: rod hole runs into the window frame: gear_cd too small");
    assert(top_y + rib_h <= svh_win[2] - servo_frame_w + num_tol, "servo_holder: ribs reach the window frame");
    assert(gusset <= min(rib_h, rib_depth) + num_tol, "servo_holder: gusset larger than the rib");
    assert(servo_boss_d > servo_tab_hole_d + num_tol, "servo_holder: tab boss no wider than its hole");
    difference() {
        union() {
            translate([0, 0, z_cap0]) linear_extrude(wall) servo_holder_outline();
            // guide frame and tab bosses on the body side (v2 servo_spacer: one padded sketch).
            // convexity is a preview hint only: a ring is not convex, so without it OpenCSG
            // previews show gaps in its far wall (the export is unaffected).
            translate([0, 0, z_plate1]) linear_extrude(svh_boss_h, convexity=4) {
                translate([win_cx, servo_y]) square(servo_win + 2*servo_frame_w*[1, 1], center=true);
                for (x = tab_x) translate([x, servo_y]) circle(d=servo_boss_d, $fn=fn_small);
            }
            for (x = [0, W - wall]) translate([x, 0, 0]) servo_holder_rib();
        }
        // window for the servo body, through plate and frame
        translate([win_cx, servo_y, z_cap0 - eps]) linear_extrude(svh_depth + 2*eps) square(servo_win, center=true);
        // M2 tab screws through plate and bosses
        for (x = tab_x) translate([x, servo_y, z_cap0 - eps]) cylinder(d=servo_tab_hole_d, h=svh_depth + 2*eps, $fn=fn_small);
        // lead screw
        translate([W/2, screw_y, z_cap0 - eps]) cylinder(d=screw_hole_d, h=svh_depth + 2*eps, $fn=fn_small);
    }
}

// Print: plate front face (z = z_cap0) on the bed; frame, bosses and ribs extrude up, the
// gusset is a 45° overhang.
module servo_holder_print() { translate([0, 0, -z_cap0]) servo_holder(); }

function servo_holder_size() = [svh_x1 - svh_x0, svh_y1 - svh_y0, svh_depth];

for_print = false;
if (is_undef(ASSEMBLY)) {
    echo(servo_holder_size=servo_holder_size(), svh_x0=svh_x0, svh_y1=svh_y1, svh_win=svh_win, svh_boss_h=svh_boss_h);
    if (for_print) servo_holder_print(); else servo_holder();
}
