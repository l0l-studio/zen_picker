use pyo3::prelude::*;

mod color_ops;

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "lib_zen")]
mod zen_lib {
    use super::*;
    use crate::color_ops::{blend_colors, FTuple, Hsv, Rgbf};

    #[pyfunction()]
    fn clamp(val: f32, val_min: f32, val_max: f32) -> f32 {
        return f32::max(f32::min(val_max, val), val_min);
    }

    #[pyfunction]
    fn color_shift(rgb: FTuple, shift_s: f32, shift_v: f32) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s + shift_s, v + shift_v);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn saturation_shift(rgb: FTuple, shift: f32) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, _, v) = hsv.to_tuple();
        hsv.set(shift, v);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn value_shift(rgb: FTuple, shift: f32) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, _) = hsv.to_tuple();
        hsv.set(s, shift);
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn relative_color_shift(rgb: FTuple, shift_s: f32, shift_v: f32) -> FTuple {
        let mut hsv: Hsv = Rgbf::from(rgb).into();
        let (_, s, v) = hsv.to_tuple();
        hsv.set(s - (shift_s * s), v - (shift_v * v));
        return Rgbf::from(hsv).into_tuple();
    }

    #[pyfunction]
    fn mix(a: FTuple, b: FTuple, t: f32) -> FTuple {
        return blend_colors(Rgbf::from(a), Rgbf::from(b), t).into_tuple();
    }

    #[pyfunction]
    fn generate_color_gradient(a: FTuple, b: FTuple, patch_count: u16) -> Vec<FTuple> {
        let p = patch_count as f32;
        let f_patch_count = if p > 0.0f32 { p } else { 1.0f32 };

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
