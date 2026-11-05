//! Native determinism test (runs under `cargo test`, not in wasm).
//!
//! AC-16 requires that two runs of the same seed produce the same trajectory
//! to within 1e-6. This test verifies the stronger property — bit-identical —
//! on 100 fixed-step runs, twice, from the same initial state. If this passes,
//! AC-16's 1e-6 tolerance is trivially satisfied for the same-code-path case.
//!
//! What this test does NOT do: it does not compare High vs Low tier. That is
//! P3.02's job, using the fixture produced here.

use agelgil_wasm::{sample_trajectory, step_state_pub, Config, State, TrajectorySample};

fn initial(cfg: Config) -> State {
    State { theta: cfg.theta0, omega: cfg.omega0, time: 0.0, steps: 0 }
}

fn bytes_of(samples: &[TrajectorySample]) -> Vec<u8> {
    // Canonical bit representation: little-endian f64 triples. Not JSON, so
    // formatting/rounding cannot mask a real difference.
    let mut v = Vec::with_capacity(samples.len() * 24);
    for s in samples {
        v.extend_from_slice(&s.t.to_le_bytes());
        v.extend_from_slice(&s.theta.to_le_bytes());
        v.extend_from_slice(&s.omega.to_le_bytes());
    }
    v
}

#[test]
fn same_seed_same_trajectory_bit_identical() {
    let cfg = Config { g: 9.81, l: 1.0, theta0: 0.5, omega0: 0.0, damping: 0.0 };
    let dt = 1.0 / 240.0;

    let a = sample_trajectory(initial(cfg), cfg, 100, dt);
    let b = sample_trajectory(initial(cfg), cfg, 100, dt);

    assert_eq!(a.len(), 101);
    assert_eq!(a.len(), b.len());
    assert_eq!(bytes_of(&a), bytes_of(&b), "trajectory bytes differ between two runs");
}

#[test]
fn step_counter_matches_call_count() {
    let cfg = Config::default();
    let dt = 1.0 / 240.0;
    let mut s = initial(cfg);
    for _ in 0..100 {
        s = step_state_pub(s, cfg, dt);
    }
    assert_eq!(s.steps, 100);
    assert!((s.time - 100.0 * dt).abs() < 1e-12);
}

#[test]
fn damping_reduces_amplitude() {
    // A physics sanity check, not a determinism check: with damping, the
    // amplitude after 10 s must be smaller than the initial amplitude.
    let cfg = Config { g: 9.81, l: 1.0, theta0: 0.5, omega0: 0.0, damping: 0.5 };
    let dt = 1.0 / 240.0;
    let samples = sample_trajectory(initial(cfg), cfg, 2400, dt); // 10 s
    let max_after = samples.iter().skip(1200).map(|s| s.theta.abs()).fold(0.0_f64, f64::max);
    assert!(max_after < 0.5 * 0.9, "damped amplitude did not decay: {max_after}");
}
