// parts/cart.scad — the magnet carrier that rides on the lid top [v2 Body009].
//
// A floor `mag_h` thick on the lid top with the magnet press-fitted through it, and two
// trapezoid ears carrying the M3 lead screw at screw_y. The cart is `cart_w` wide (the lid's
// lip lines minus one extrusion each side) and `cart_len` long: two ears plus the magnet hole
// plus `mag_margin` of floor each side of it. The front ear (−Z, toward the servo) traps the
// drive nut in a top-loading slot: v2's hex pocket through the ear held the nut only until
// the rod pushed the cart, so here the slot is closed on the +Z side and open only upward.

include <../params.scad>
use <../lib/shapes.scad>
$fn = fn_round;
eps = 0.01;

cart_x0 = W/2 - cart_w/2;  cart_x1 = W/2 + cart_w/2;   // floor edges [v2 2 .. 19.2]
cart_floor_top = top_y + mag_h;                          // the ears root here
cart_chamfer = 4*line_w;                                 // floor corner chamfers [v2 1.6]: the corners never catch the lid edge
cart_ear_base = [cart_x0 + ear_base_inset, cart_x1 - ear_base_inset];   // ear footprint on the floor
cart_slot_w = nut_af + nut_clear;                        // slot across the flats, flats vertical
cart_slot_t = nut_t + nut_clear;                         // slot along the rod, centred in the ear

// One ear: trapezoid in (x, y) rooted `mag_h` deep in the floor (so the union has no coplanar
// seam), `ear_t` along +Z from z=0.
module cart_ear() {
    linear_extrude(ear_t)
        polygon([[cart_ear_base[0], top_y], [cart_ear_base[1], top_y],
                 [cart_ear_base[1], cart_floor_top], [W/2 + ear_top_w/2, cart_top],
                 [W/2 - ear_top_w/2, cart_top], [cart_ear_base[0], cart_floor_top]]);
}

// The nut trap in the front ear: a hex prism (corners up and down, flats vertical) around the
// rod axis plus a slot of the same width from the axis up through the ear top. The nut drops
// in from above; the lower half of the hexagon is its floor, the flats stop it turning, the
// ear's two walls stop it moving along the rod.
module cart_nut_slot() {
    translate([W/2, screw_y, ear_t/2 - cart_slot_t/2]) {
        rotate([0, 0, 90]) hex(cart_slot_w, cart_slot_t);   // hex() has corners on ±X: turned so the flats are vertical
        translate([-cart_slot_w/2, 0, 0]) cube([cart_slot_w, cart_top - screw_y + eps, cart_slot_t]);
    }
}

// The asserts live inside the module, not at file top level: `use <cart.scad>` (assembly.scad)
// imports modules, functions and variables but does not execute top-level statements, so a
// file-top assert would be silent in the assembly and only fire on a standalone render.
module cart() {
    assert(ear_base_inset >= cart_chamfer - num_tol, "cart: ear base overhangs the floor's corner chamfer: raise ear_base_inset");
    assert(cart_ear_base[0] <= W/2 - ear_top_w/2 + num_tol, "cart: ear top wider than its base");
    assert(mag_d + mag_clear + 2*cart_chamfer <= cart_w + num_tol, "cart: magnet hole reaches the floor's side chamfers");
    assert(screw_y + screw_hole_d/2 < cart_top - num_tol, "cart: rod hole breaks out of the ear top: raise ear_h");
    difference() {
        union() {
            // floor: chamfered rectangle in (x, z), mag_h tall along +Y from the lid top.
            // rotate([90,0,0]) maps the extrusion w onto −y, so it runs from −mag_h to 0 first.
            translate([0, top_y, 0]) rotate([90, 0, 0]) translate([0, 0, -mag_h]) linear_extrude(mag_h)
                translate([cart_x0, 0]) chamfered_rect([cart_w, cart_len], cart_chamfer);
            cart_ear();
            translate([0, 0, cart_len - ear_t]) cart_ear();
        }
        // magnet, press fit through the floor
        translate([W/2, top_y - eps, cart_len/2]) rotate([-90, 0, 0]) cylinder(d=mag_d + mag_clear, h=mag_h + 2*eps);
        // lead screw through both ears
        translate([W/2, screw_y, -eps]) cylinder(d=screw_hole_d, h=cart_len + 2*eps, $fn=fn_small);
        cart_nut_slot();
    }
}

// Print: floor bottom (y = top_y) on the bed; ears up, nut slot open upward.
// rotate([90,0,0]) maps (x, y, z) onto (x, −z, y).
module cart_print() { rotate([90, 0, 0]) translate([0, -top_y, 0]) cart(); }

function cart_size() = [cart_w, mag_h + ear_h, cart_len];

for_print = false;
if (is_undef(ASSEMBLY)) {
    echo(cart_size=cart_size(), cart_x0=cart_x0, cart_floor_top=cart_floor_top, cart_ear_base=cart_ear_base,
         cart_slot_w=cart_slot_w, cart_slot_t=cart_slot_t, nut_floor_y=screw_y - nut_ac/2, floor_left_under_nut=screw_y - nut_ac/2 - top_y);
    if (for_print) cart_print(); else cart();
}
