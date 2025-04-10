use pyo3::prelude::*;

mod color_ops;

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "lib_zen")]
mod zen_lib {
    use super::*;
    use crate::color_ops::{blend_colors, hsv_rgb, rgbf_hsv, FTuple, Rgbf};
    use std::cmp::{max, min};

    #[pyfunction()]
    fn clamp(val: i16) -> u8 {
        return max(min(255, val as u8), 0);
    }

    #[pyfunction]
    fn color_shift(rgb: FTuple, shift_s: f32, shift_v: f32) -> FTuple {
        let mut hsv = rgbf_hsv(Rgbf::from(rgb));
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s + shift_s, v + shift_v);
        return Rgbf::from(hsv_rgb(hsv)).into_tuple();
    }
    #[pyfunction]
    fn relative_color_shift(rgb: FTuple, shift_s: f32, shift_v: f32) -> FTuple {
        let mut hsv = rgbf_hsv(Rgbf::from(rgb));
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s - (shift_s * s), v - (shift_v * v));
        return Rgbf::from(hsv_rgb(hsv)).into_tuple();
    }

    #[pyfunction]
    fn mix(a: FTuple, b: FTuple, t: f32) -> FTuple {
        return blend_colors(Rgbf::from(a), Rgbf::from(b), t).into_tuple();
    }

    #[pyfunction]
    fn generate_color_gradient(a: FTuple, b: FTuple, patch_count: u16) -> Vec<FTuple> {
        let f_patch_count = patch_count as f32;
        let mut gradient = Vec::<FTuple>::with_capacity(patch_count.into());

        for i in 0..patch_count {
            let i = i as f32 / f_patch_count;

            let r = a.0 + (b.0 - a.0) * i;
            let g = a.1 + (b.1 - a.1) * i;
            let b = a.2 + (b.2 - a.2) * i;

            gradient.push((r, g, b) as FTuple);
        }

        return gradient;
    }
}
