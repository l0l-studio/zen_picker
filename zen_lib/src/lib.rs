use pyo3::prelude::*;

mod color_ops;

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "lib_zen")]
mod zen_lib {
    use super::*;
    use crate::color_ops::{blend_colors, FTuple, Hsv, Rgbf};
    use hsluv::{hsluv_to_rgb, rgb_to_hsluv};

    #[pyfunction()]
    fn clamp(val: f64, val_min: f64, val_max: f64) -> f64 {
        return f64::max(f64::min(val_max, val), val_min);
    }

    #[pyfunction]
    fn color_shift(rgb: FTuple, shift_s: f64, shift_v: f64) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s + shift_s, v + shift_v);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn saturation_shift(rgb: FTuple, shift: f64) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, _, v) = hsv.to_tuple();
        hsv.set(shift, v);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn saturation_shift_uv(rgb: FTuple, shift: f64) -> FTuple {
        let (r, g, b) = rgb;
        let (h, s, v) = rgb_to_hsluv(r, g, b);

        return hsluv_to_rgb(h, shift * 100.0, v);
    }

    #[pyfunction]
    fn value_shift(rgb: FTuple, shift: f64) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, _) = hsv.to_tuple();
        hsv.set(s, shift);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn value_shift_uv(rgb: FTuple, shift: f64) -> FTuple {
        let (r, g, b) = rgb;
        let (h, s, _) = rgb_to_hsluv(r, g, b);

        return hsluv_to_rgb(h, s, shift * 100.0);
    }

    #[pyfunction]
    fn relative_color_shift(rgb: FTuple, shift_s: f64, shift_v: f64) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s - (shift_s * s), v - (shift_v * v));
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn to_hsv(rgb: FTuple) -> FTuple {
        let (r, g, b) = rgb;
        let rgb = Rgbf::new(r, g, b);
        let hsv = Hsv::from(rgb);

        return hsv.to_tuple();
    }

    #[pyfunction]
    fn to_hsluv(rgb: FTuple) -> FTuple {
        let (r, g, b) = rgb;

        let (h, s, v) = rgb_to_hsluv(r, g, b);
        return (h / 360.0, s / 100.0, v / 100.0) as FTuple;
    }

    #[pyfunction]
    fn match_value(stable: FTuple, variable: FTuple) -> FTuple {
        let (r, g, b) = stable;
        let (_r, _g, _b) = variable;

        let (_, _, v) = rgb_to_hsluv(r, g, b);
        let (_h, _s, _) = rgb_to_hsluv(_r, _g, _b);
        let (_r, _g, _b) = hsluv_to_rgb(_h, _s, v);

        return (_r, _g, _b);
    }

    #[pyfunction]
    fn mix(a: FTuple, b: FTuple, t: f64) -> FTuple {
        return blend_colors(Rgbf::from(a), Rgbf::from(b), t).into_tuple();
    }

    #[pyfunction]
    fn generate_color_gradient(a: FTuple, b: FTuple, patch_count: u16) -> Vec<FTuple> {
        let p = patch_count as f64;
        let f_patch_count = if p > 0.0f64 { p } else { 1.0f64 };

        let mut gradient = Vec::<FTuple>::with_capacity(patch_count.into());

        for i in 0..patch_count {
            let i = i as f64 / f_patch_count;

            let r = a.0 + (b.0 - a.0) * i;
            let g = a.1 + (b.1 - a.1) * i;
            let b = a.2 + (b.2 - a.2) * i;

            gradient.push((r, g, b) as FTuple);
        }

        return gradient;
    }

    #[cfg(test)]
    mod test {
        use super::*;
        use hsluv::rgb_to_hsluv;

        #[test]
        fn match_value_works() {
            let colors = vec![
                (
                    (176.0 / 255.0, 95.0 / 255.0, 110.0 / 255.0),
                    (50.0 / 255.0, 95.0 / 255.0, 110.0 / 255.0),
                ),
                (
                    (169.0 / 255.0, 133.0 / 255.0, 102.0 / 255.0),
                    (146.0 / 255.0, 144.0 / 255.0, 39.0 / 255.0),
                ),
                (
                    (146.0 / 255.0, 144.0 / 255.0, 39.0 / 255.0),
                    (168.0 / 255.0, 136.0 / 255.0, 46.0 / 255.0),
                ),
                (
                    (146.0 / 255.0, 144.0 / 255.0, 39.0 / 255.0),
                    (168.0 / 255.0, 136.0 / 255.0, 200.0 / 255.0),
                ),
            ];

            for (stable, variable) in colors {
                let (r, g, b) = stable;
                let (_r, _g, _b) = variable;

                let (h, s, v) = rgb_to_hsluv(r, g, b);
                let (res_r, res_g, res_b) = match_value(stable, variable);
                let (_h, _s, _v) = rgb_to_hsluv(res_r, res_g, res_b);

                let err = 0.0000001;
                assert!((v - _v).abs() < err);
                assert_ne!(h, _h);
                assert_ne!(s, _s);
            }
        }
    }
}
