pub type FTuple = (f64, f64, f64);

impl From<Rgbf> for FTuple {
    fn from(Rgbf(r, g, b): Rgbf) -> Self {
        return (r, g, b) as Self;
    }
}

pub struct Rgbf(f64, f64, f64);

impl Rgbf {
    pub fn new(r: f64, g: f64, b: f64) -> Self {
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

impl From<Hsv> for Rgbf {
    fn from(hsv: Hsv) -> Self {
        return hsv_rgbf(hsv);
    }
}

impl From<FTuple> for Rgbf {
    fn from((r, g, b): FTuple) -> Self {
        return Self(r, g, b);
    }
}

pub struct Hsv(f64, f64, f64);

impl Hsv {
    pub fn new((h, s, v): FTuple) -> Self {
        return Self(h, s, v);
    }

    pub fn set(&mut self, s: f64, v: f64) {
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

impl From<Rgbf> for Hsv {
    fn from(rgbf: Rgbf) -> Self {
        return rgbf_hsv(rgbf);
    }
}

// https://github.com/QuantitativeBytes/qbColor/blob/a0589344c47126705019f8498fe7fa5ae8b19d64/qbColor.cpp#L153
fn rgbf_hsv(Rgbf(r, g, b): Rgbf) -> Hsv {
    let min: f64;
    let max: f64;
    let max_index: u8;

    if r == g && r == b {
        max_index = 0;
        min = r;
        max = r;
    } else if r >= g && r >= b {
        max_index = 1;
        max = r;
        min = if g < b { g } else { b }
    } else if g >= r && g >= b {
        max_index = 2;
        max = g;
        min = if r < b { r } else { b }
    } else {
        max_index = 3;
        max = b;
        min = if r < g { r } else { g }
    }

    let mut h: f64;
    let delta = max - min;

    match max_index {
        1 => h = 60.0 * ((g - b) / delta),
        2 => h = 60.0 * (2.0 + ((b - r) / delta)),
        3 => h = 60.0 * (4.0 + ((r - g) / delta)),
        _ => h = 0.0,
    }

    if h < 0.0 {
        h += 360.0;
    }
    h = h / 360.0;

    let s: f64 = if max_index == 0 {
        0.0
    } else {
        (max - min) / max
    };

    let v: f64 = max;

    return Hsv(h, s, v);
}

// https://github.com/QuantitativeBytes/qbColor/blob/a0589344c47126705019f8498fe7fa5ae8b19d64/qbColor.cpp#L217
fn hsv_rgbf(Hsv(h, s, v): Hsv) -> Rgbf {
    let rgb_range = s * v;
    let max = v;
    let min = v - rgb_range;
    let _h = (h * 360.0) / 60.0;
    let x1 = _h % 1.0;
    let x2 = 1.0 - _h % 1.0;

    let r: f64;
    let g: f64;
    let b: f64;

    if _h >= 0.0 && _h < 1.0 {
        r = max;
        g = (x1 * rgb_range) + min;
        b = min;
    } else if _h >= 1.0 && _h < 2.0 {
        r = (x2 * rgb_range) + min;
        g = max;
        b = min;
    } else if _h >= 2.0 && _h < 3.0 {
        r = min;
        g = max;
        b = (x1 * rgb_range) + min;
    } else if _h >= 3.0 && _h < 4.0 {
        r = min;
        g = (x2 * rgb_range) + min;
        b = max;
    } else if _h >= 4.0 && _h < 5.0 {
        r = (x1 * rgb_range) + min;
        g = min;
        b = max;
    } else if _h >= 5.0 && _h < 6.0 {
        r = max;
        g = min;
        b = (x2 * rgb_range) + min;
    } else {
        r = 0.0;
        g = 0.0;
        b = 0.0;
    }

    return Rgbf::new(r, g, b);
}

// https://stackoverflow.com/a/29641264
fn blend_color_value(a: f64, b: f64, t: f64) -> f64 {
    return f64::sqrt((1.0 - t) * a.powf(2.0) + t * b.powf(2.0));
}

pub fn blend_colors(a: Rgbf, b: Rgbf, t: f64) -> Rgbf {
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

    #[test]
    fn rgbf_to_hsv_works() {
        let rgb_colors = vec![
            Rgbf::new(0.0 / 255.0, 52.0 / 255.0, 52.0 / 255.0),
            Rgbf::new(152.0 / 255.0, 104.0 / 255.0, 163.0 / 255.0),
            Rgbf::new(202.0 / 255.0, 205.0 / 255.0, 35.0 / 255.0),
        ];
        let hsv_colors = vec![
            (0.5, 1.0, 0.2039),
            (0.8022, 0.3620, 0.6392),
            (0.1696, 0.8293, 0.8039),
        ];

        for i in 0..rgb_colors.len() {
            let (_h, _s, _v) = rgbf_hsv(rgb_colors[i].clone()).into_tuple();
            let (h, s, v) = hsv_colors[i];

            let err = 0.0001;
            assert!(_h - h < err);
            assert!(_s - s < err);
            assert!(_v - v < err);
        }
    }

    #[test]
    fn hsv_set_color_works() {
        let rgb_colors = vec![
            Rgbf::new(0.0 / 255.0, 52.0 / 255.0, 52.0 / 255.0),
            Rgbf::new(152.0 / 255.0, 104.0 / 255.0, 163.0 / 255.0),
            Rgbf::new(202.0 / 255.0, 205.0 / 255.0, 35.0 / 255.0),
        ];

        let result_hsv_colors = vec![
            (0.5, 1.0, 0.10195),
            (0.8022, 0.3620, 0.3196),
            (0.1696, 0.8293, 0.40195),
        ];

        let er: f64 = 0.1;
        let shift_s: f64 = 0.0;
        let shift_v: f64 = 0.5;
        for i in 0..rgb_colors.len() {
            let mut hsv = rgbf_hsv(rgb_colors[i].clone());
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
    fn hsv_to_rgbf_works() {
        let rgb_colors = vec![
            Rgbf::new(0.0 / 255.0, 52.0 / 255.0, 52.0 / 255.0),
            Rgbf::new(152.0 / 255.0, 104.0 / 255.0, 163.0 / 255.0),
            Rgbf::new(202.0 / 255.0, 205.0 / 255.0, 35.0 / 255.0),
        ];
        let hsv_colors = vec![
            (0.5, 1.0, 0.2039),
            (0.8022, 0.3620, 0.6392),
            (0.1696, 0.8293, 0.8039),
        ];

        for i in 0..rgb_colors.len() {
            let (_r, _g, _b) = hsv_rgbf(Hsv::new(hsv_colors[i])).into_tuple();
            let (r, g, b) = rgb_colors[i].clone().into_tuple();

            let er: f64 = 0.0001;
            assert!((_r - r) <= er);
            assert!((_g - g) <= er);
            assert!((_b - b) <= er);
        }
    }
}
