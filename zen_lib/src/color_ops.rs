pub type ITuple = (u8, u8, u8);
pub type FTuple = (f32, f32, f32);

impl From<Rgb> for ITuple {
    fn from(Rgb(r, g, b): Rgb) -> Self {
        return (r, g, b) as Self;
    }
}

impl From<Rgbf> for FTuple {
    fn from(Rgbf(r, g, b): Rgbf) -> Self {
        return (r, g, b) as Self;
    }
}

pub struct Rgb(u8, u8, u8);

impl Rgb {
    pub fn new(r: u8, g: u8, b: u8) -> Self {
        return Rgb(r, g, b);
    }

    pub fn into_tuple(self) -> ITuple {
        return (self.0, self.1, self.2);
    }

    pub fn to_tuple(&self) -> ITuple {
        return (self.0, self.1, self.2);
    }
}

impl From<Rgbf> for Rgb {
    fn from(Rgbf(r, g, b): Rgbf) -> Self {
        let max_val: u8 = 255;
        return Self(
            (r as u8) * max_val,
            (g as u8) * max_val,
            (b as u8) * max_val,
        );
    }
}

pub struct Rgbf(f32, f32, f32);

impl Rgbf {
    pub fn new(r: f32, g: f32, b: f32) -> Self {
        return Self(r, g, b);
    }

    pub fn diff(a: &Rgbf, b: &Rgbf) -> FTuple {
        return (b.0 - a.0, b.1 - a.1, b.2 - a.2) as FTuple;
    }

    pub fn into_tuple(self) -> FTuple {
        return (self.0, self.1, self.2);
    }

    pub fn to_tuple(&self) -> FTuple {
        return (self.0, self.1, self.2);
    }
}

impl From<Rgb> for Rgbf {
    fn from(Rgb(r, g, b): Rgb) -> Self {
        let max_val: f32 = 255.0;
        return Self(
            (r as f32) / max_val,
            (g as f32) / max_val,
            (b as f32) / max_val,
        );
    }
}

impl From<FTuple> for Rgbf {
    fn from((r, g, b): FTuple) -> Self {
        return Self(r, g, b);
    }
}

impl From<ITuple> for Rgbf {
    fn from((r, g, b): ITuple) -> Self {
        return Self::from(Rgb(r, g, b));
    }
}

pub struct Hsv(f32, f32, f32);

impl Hsv {
    pub fn new((h, s, v): FTuple) -> Self {
        return Self(h, s, v);
    }

    pub fn set(&mut self, s: f32, v: f32) {
        self.1 = s;
        self.2 = v;
    }

    pub fn into_tuple(self) -> FTuple {
        return (self.0, self.1, self.2) as FTuple;
    }

    pub fn to_tuple(&self) -> FTuple {
        return (self.0, self.1, self.2) as FTuple;
    }
}

// Color conversion implementatoins from:
// https://www.easyrgb.com/en/math.php

pub fn rgbf_hsv(Rgbf(r, g, b): Rgbf) -> Hsv {
    let min_val = r.min(g.min(b));
    let max_val = r.max(g.max(b));
    let delta = max_val - min_val;

    let mut h: f32;
    let s: f32;
    let v: f32 = max_val;

    if delta == 0.0 {
        h = 0.0;
        s = 0.0;
    } else {
        s = delta / max_val;
        let delta_r = (((max_val - r) / 6.0) + (delta / 2.0)) / delta;
        let delta_g = (((max_val - g) / 6.0) + (delta / 2.0)) / delta;
        let delta_b = (((max_val - b) / 6.0) + (delta / 2.0)) / delta;

        if max_val == r {
            h = delta_b - delta_g;
        } else if max_val == g {
            h = (1.0 / 3.0) + delta_r - delta_b;
        } else {
            h = (2.0 / 3.0) + delta_g - delta_r;
        }

        if h < 0.0 {
            h += 1.0
        }
        if h > 1.0 {
            h -= 1.0
        }
    }

    return Hsv(h, s, v);
}

pub fn hsv_rgb(Hsv(h, s, v): Hsv) -> Rgb {
    let rgb_max: f32 = 255.0;

    if s == 0.0 {
        return Rgb(
            (v * rgb_max) as u8,
            (v * rgb_max) as u8,
            (v * rgb_max) as u8,
        );
    }

    let mut _h = h * 6.0;
    if _h == 6.0 {
        _h = 0.0;
    }

    let _i = _h.floor();

    let _1 = v * (1.0 - s);
    let _2 = v * (1.0 - s * (_h - _i));
    let _3 = v * (1.0 - s * (1.0 - (_h - _i)));

    let _rgb = match _i {
        0.0 => (v, _3, _1),
        1.0 => (_2, v, _1),
        2.0 => (_1, v, _3),
        3.0 => (_1, _2, v),
        4.0 => (_3, _1, v),
        _ => (v, _1, _2),
    };

    return Rgb(
        (_rgb.0 * rgb_max) as u8,
        (_rgb.1 * rgb_max) as u8,
        (_rgb.2 * rgb_max) as u8,
    );
}

// https://stackoverflow.com/a/29321264
fn blend_color_value(a: f32, b: f32, t: f32) -> f32 {
    return f32::sqrt((1.0 - t) * a.powf(2.0) + t * b.powf(2.0));
}

pub fn blend_colors(a: Rgbf, b: Rgbf, t: f32) -> Rgbf {
    return Rgbf(
        blend_color_value(a.0, b.0, t),
        blend_color_value(a.1, b.1, t),
        blend_color_value(a.2, b.2, t),
    );
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::clone::Clone;

    impl Clone for Rgbf {
        fn clone(&self) -> Self {
            let (r, g, b) = self.to_tuple();
            return Self::new(r, g, b);
        }
    }

    impl Clone for Rgb {
        fn clone(&self) -> Self {
            let (r, g, b) = self.to_tuple();
            return Self::new(r, g, b);
        }
    }

    #[test]
    fn rgb_to_hsv_works() {
        let rgb_colors = vec![
            Rgbf::from(Rgb::new(0, 53, 53)),
            Rgbf::from(Rgb::new(153, 105, 164)),
            Rgbf::from(Rgb::new(202, 206, 35)),
        ];
        let hsv_colors = vec![
            (0.5, 1.0, 0.2078),
            (0.8022, 0.3597, 0.6431),
            (0.1705, 0.8300, 0.8078),
        ];

        let factor = 10.0f32.powi(4 as i32);

        for i in 0..rgb_colors.len() {
            let (_h, _s, _v) = rgbf_hsv(rgb_colors[i].clone()).into_tuple();
            let (h, s, v) = hsv_colors[i];

            assert_eq!(
                (
                    (_h * factor).trunc(),
                    (_s * factor).trunc(),
                    (_v * factor).trunc(),
                ),
                (
                    (h * factor).trunc(),
                    (s * factor).trunc(),
                    (v * factor).trunc()
                )
            );
        }
    }

    #[test]
    fn hsv_set_color_works() {
        let rgb_colors = vec![
            Rgb::new(0, 52, 52),
            Rgb::new(152, 104, 163),
            Rgb::new(202, 205, 35),
        ];

        let result_hsv_colors = vec![
            (0.5, 1.0, 0.1039),
            (0.8022, 0.3597, 0.32155),
            (0.1705, 0.8300, 0.4039),
        ];

        let er: f32 = 0.01;
        let shift_s: f32 = 0.0;
        let shift_v: f32 = 0.5;
        for i in 0..rgb_colors.len() {
            let mut hsv = rgbf_hsv(Rgbf::from(Rgbf::from(rgb_colors[i].clone())));
            let (_, s, v) = hsv.to_tuple();
            hsv.set(s - (shift_s * s), v - (shift_v * v));

            let (_h, _s, _v) = hsv.into_tuple();
            let (h, s, v) = result_hsv_colors[i];

            assert!((_h - h).abs() <= er);
            assert!((_s - s).abs() <= er);
            assert!((_v - v).abs() <= er);
        }
    }

    #[test]
    fn hsv_to_rgb_works() {
        let rgb_colors = vec![
            Rgb::new(0, 52, 52),
            Rgb::new(152, 104, 163),
            Rgb::new(202, 205, 35),
        ];
        let hsv_colors = vec![
            (0.5, 1.0, 0.2078),
            (0.8022, 0.3597, 0.6431),
            (0.1705, 0.8300, 0.8078),
        ];

        for i in 0..rgb_colors.len() {
            let (_r, _g, _b) = hsv_rgb(Hsv::new(hsv_colors[i])).into_tuple();
            let (r, g, b) = rgb_colors[i].clone().into_tuple();

            let er: u8 = 1;
            assert!((_r.abs_diff(r)) <= er);
            assert!((_g.abs_diff(g)) <= er);
            assert!((_b.abs_diff(b)) <= er);
        }
    }
}
