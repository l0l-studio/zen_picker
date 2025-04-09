use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "lib_zen")]
mod zen_lib {
    use super::*;
    use colors_ops::{blend_colors, hsv_rgb, rgb_hsv, Rgb};
    use std::cmp::{max, min};

    #[pyfunction]
    fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
        Ok((a + b).to_string())
    }

    #[pyfunction()]
    fn clamp(val: i16) -> u8 {
        if val >= 255 {
            return 255;
        } else if val <= 0 {
            return 0;
        }

        return max(min(255, val as u8), 0);
    }

    #[pyfunction]
    fn color_shift(rgb: (i16, i16, i16), shift_s: f32, shift_v: f32) -> (u8, u8, u8) {
        let mut hsv = rgb_hsv(rgb.0, rgb.1, rgb.2);
        hsv.shift(shift_s, shift_v);
        return hsv_rgb(hsv).into_tuple();
    }

    #[pyfunction]
    fn mix(a: (u8, u8, u8), b: (u8, u8, u8), t: f32) -> (u8, u8, u8) {
        return blend_colors(
            Rgb::new(a.0, a.1, a.2).into(),
            Rgb::new(b.0, b.1, b.2).into(),
            t,
        )
        .into_tuple();
    }

    mod colors_ops {
        pub struct Rgb(u8, u8, u8);

        impl Rgb {
            pub fn new(r: u8, g: u8, b: u8) -> Self {
                return Rgb(r, g, b);
            }

            pub fn into_tuple(self) -> (u8, u8, u8) {
                return (self.0, self.1, self.2);
            }
        }

        pub struct Rgbf(f32, f32, f32);

        impl From<Rgb> for Rgbf {
            fn from(Rgb(r, g, b): Rgb) -> Self {
                return Self(r as f32, g as f32, b as f32);
            }
        }

        pub struct Hsv(f32, f32, f32);

        impl Hsv {
            pub fn shift(&mut self, s: f32, v: f32) {
                self.1 += s;
                self.2 += v;
            }
        }

        // Color conversion implementatoins from:
        // https://www.easyrgb.com/en/math.php

        pub fn rgb_hsv(r: i16, g: i16, b: i16) -> Hsv {
            let rgb_max: f32 = 255.0;

            let r = r as f32 / rgb_max;
            let g = g as f32 / rgb_max;
            let b = b as f32 / rgb_max;

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
                3.0 => (_2, _2, v),
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

        pub fn blend_colors(a: Rgbf, b: Rgbf, t: f32) -> Rgb {
            return Rgb(
                blend_color_value(a.0, b.0, t) as u8,
                blend_color_value(a.1, b.1, t) as u8,
                blend_color_value(a.2, b.2, t) as u8,
            );
        }
    }
}
