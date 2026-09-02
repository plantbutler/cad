// lib/gear.scad — involute spur gears built from points. Standard proportions: addendum = m,
// dedendum = 1.25 m, so the tip diameter is m (teeth + 2) and two gears mesh at
// m (t1 + t2)/2. The gear is centred on the origin, teeth in XY, thickness along +Z from
// z=0, one tooth centred on +X. Two gears mesh when the second is rotated by 180/teeth
// (a gap facing the first) — see the assembly. The caller's $fn rounds the root and the bore.

function gear_pitch_r(teeth, module_) = module_*teeth/2;
function gear_base_r(teeth, module_, pressure_angle=20) = gear_pitch_r(teeth, module_)*cos(pressure_angle);
function gear_outer_r(teeth, module_) = gear_pitch_r(teeth, module_) + module_;
function gear_root_r(teeth, module_) = gear_pitch_r(teeth, module_) - 1.25*module_;
function gear_od(teeth, module_) = 2*gear_outer_r(teeth, module_);
function gear_centre_distance(teeth_a, teeth_b, module_) = module_*(teeth_a + teeth_b)/2;

// involute function, degrees in and out: inv(phi) = tan(phi) − phi
function _inv(phi) = tan(phi)*180/PI - phi;

// half of the tooth's angular thickness at radius r (degrees): the involute thins outward
function _half_angle(r, rb, half_p, pressure_angle) =
    half_p + _inv(pressure_angle) - _inv(acos(min(1, rb/r)));

// One tooth centred on +X: a radial root below the base circle, `flank_pts` involute segments
// per flank, the tip land. Starts module_/10 inside the root circle so the union with the root
// disc leaves no sliver. backlash comes off the circular tooth thickness at the pitch circle.
function gear_tooth(teeth, module_, pressure_angle=20, backlash=0, flank_pts=8) =
    let(rp = gear_pitch_r(teeth, module_), rb = gear_base_r(teeth, module_, pressure_angle),
        ro = gear_outer_r(teeth, module_), rr = gear_root_r(teeth, module_),
        r0 = max(rb, rr),                                  // the involute exists only above the base circle
        thick = PI*module_/2 - backlash,                   // circular tooth thickness at the pitch circle
        half_p = thick/2/rp*180/PI,                        // its half-angle
        a0 = _half_angle(r0, rb, half_p, pressure_angle),
        a_tip = _half_angle(ro, rb, half_p, pressure_angle),
        r_in = rr - module_/10,
        ok = assert(a_tip > 0, "gear: pointed tooth tip — more teeth, or less backlash")
             assert(rr > 0, "gear: root radius <= 0") true,
        right = [for (j = [0 : flank_pts]) let(r = r0 + (ro - r0)*j/flank_pts, a = -_half_angle(r, rb, half_p, pressure_angle)) r*[cos(a), sin(a)]],
        left  = [for (j = [flank_pts : -1 : 0]) let(r = r0 + (ro - r0)*j/flank_pts, a = _half_angle(r, rb, half_p, pressure_angle)) r*[cos(a), sin(a)]])
    concat([r_in*[cos(-a0), sin(-a0)]], right, left, [r_in*[cos(a0), sin(a0)]]);

// 2D outline: root disc plus `teeth` teeth
module gear_2d(teeth, module_, pressure_angle=20, backlash=0, flank_pts=8) {
    union() {
        circle(r=gear_root_r(teeth, module_));
        for (i = [0 : teeth - 1])
            rotate(i*360/teeth) polygon(gear_tooth(teeth, module_, pressure_angle, backlash, flank_pts));
    }
}

// The solid gear, `thickness` along +Z from z=0, with a through bore of diameter `bore` (0 = none).
module spur_gear(teeth, module_, thickness, pressure_angle=20, backlash=0, bore=0, flank_pts=8) {
    difference() {
        linear_extrude(thickness) gear_2d(teeth, module_, pressure_angle, backlash, flank_pts);
        if (bore > 0) translate([0, 0, -0.01]) cylinder(d=bore, h=thickness + 0.02);
    }
}
