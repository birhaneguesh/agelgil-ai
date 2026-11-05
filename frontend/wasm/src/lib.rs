//! Agelgil-AI pendulum physics.
//!
//! Deterministic: the trajectory produced by N `step(dt)` calls depends only on
//! the state, the config, and `dt`. No wall clock, no random, no thread. Same
//! input sequence on the same machine -> bit-identical trajectory; this is what
//! AC-16's cross-tier comparison relies on.
//!
//! Precision: f64. Cross-device bit-identity is not required. Same-device
//! repeatability is.

use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

const TWO_PI: f64 = std::f64::consts::TAU;

#[derive(Clone, Copy, Debug, Deserialize)]
pub struct Config {
    /// gravitational acceleration, m/s^2
    pub g: f64,
    /// pendulum length, m
    pub l: f64,
    /// initial angle from vertical, radians
    pub theta0: f64,
    /// initial angular velocity, rad/s
    pub omega0: f64,
    /// angular damping coefficient, 1/s (0 = undamped)
    pub damping: f64,
}

impl Default for Config {
    fn default() -> Self {
        Self { g: 9.81, l: 1.0, theta0: 0.5, omega0: 0.0, damping: 0.0 }
    }
}

#[derive(Clone, Copy, Debug, Serialize)]
pub struct State {
    pub theta: f64,
    pub omega: f64,
    pub time: f64,
    pub steps: u64,
}

#[derive(Clone, Copy, Debug, Serialize)]
pub struct TrajectorySample {
    pub t: f64,
    pub theta: f64,
    pub omega: f64,
}

/// One semi-implicit Euler step of the nonlinear pendulum:
///   theta'' = -(g/L) sin(theta) - damping * theta'
fn step_state(state: State, cfg: Config, dt: f64) -> State {
    let alpha = -(cfg.g / cfg.l) * state.theta.sin() - cfg.damping * state.omega;
    let new_omega = state.omega + alpha * dt;
    let new_theta = state.theta + new_omega * dt;
    // keep theta in (-pi, pi] so long runs don't accumulate magnitude and lose precision
    let wrapped = ((new_theta + std::f64::consts::PI).rem_euclid(TWO_PI)) - std::f64::consts::PI;
    State {
        theta: wrapped,
        omega: new_omega,
        time: state.time + dt,
        steps: state.steps + 1,
    }
}

// ---------------------------------------------------------------------------
// wasm-bindgen surface (P3.01 locked API)
// ---------------------------------------------------------------------------

thread_local! {
    static INSTANCE: std::cell::RefCell<Option<(Config, State)>> =
        const { std::cell::RefCell::new(None) };
}

#[wasm_bindgen]
pub fn init(config_js: JsValue) -> Result<(), JsValue> {
    let cfg: Config = serde_wasm_bindgen::from_value(config_js)
        .map_err(|e| JsValue::from_str(&format!("init: bad config: {e}")))?;
    if cfg.l <= 0.0 {
        return Err(JsValue::from_str("init: l must be > 0"));
    }
    if cfg.g <= 0.0 {
        return Err(JsValue::from_str("init: g must be > 0"));
    }
    if cfg.damping < 0.0 {
        return Err(JsValue::from_str("init: damping must be >= 0"));
    }
    let state = State { theta: cfg.theta0, omega: cfg.omega0, time: 0.0, steps: 0 };
    INSTANCE.with(|c| *c.borrow_mut() = Some((cfg, state)));
    Ok(())
}

#[wasm_bindgen]
pub fn reset() {
    INSTANCE.with(|c| {
        // Bind the snapshot to a local so the immutable borrow ends before the
        // mutable borrow begins. Without this, the `Ref` from `c.borrow()` lives
        // through the if-let body, and `c.borrow_mut()` panics with BorrowMutError.
        let snapshot: Option<(Config, State)> = *c.borrow();
        if let Some((cfg, _)) = snapshot {
            *c.borrow_mut() = Some((
                cfg,
                State { theta: cfg.theta0, omega: cfg.omega0, time: 0.0, steps: 0 },
            ));
        }
    });
}

#[wasm_bindgen]
pub fn step(dt: f64) -> Result<(), JsValue> {
    if !(dt > 0.0) || !dt.is_finite() {
        return Err(JsValue::from_str("step: dt must be finite and > 0"));
    }
    INSTANCE.with(|c| {
        let mut g = c.borrow_mut();
        match g.as_mut() {
            Some((cfg, st)) => {
                *st = step_state(*st, *cfg, dt);
                Ok(())
            }
            None => Err(JsValue::from_str("step: call init() first")),
        }
    })
}

#[wasm_bindgen]
pub fn get_state() -> Result<JsValue, JsValue> {
    INSTANCE.with(|c| match *c.borrow() {
        Some((_, st)) => serde_wasm_bindgen::to_value(&st)
            .map_err(|e| JsValue::from_str(&format!("get_state: {e}"))),
        None => Err(JsValue::from_str("get_state: call init() first")),
    })
}

/// Run `n` fixed-`dt` steps and return the full trajectory.
///
/// **Read-only**: does not advance the module state. Calling `run_trajectory`
/// twice from the same `init()` returns the same trajectory twice. Call
/// `step(dt)` in a loop if state advancement is required.
///
/// Used by the AC-16 fixture generator in P3.02. Same `(seed, n, dt)` must
/// produce identical bytes on High and Low tiers.
#[wasm_bindgen]
pub fn run_trajectory(n: u32, dt: f64) -> Result<JsValue, JsValue> {
    if !(dt > 0.0) || !dt.is_finite() {
        return Err(JsValue::from_str("run_trajectory: dt must be finite and > 0"));
    }
    INSTANCE.with(|c| {
        // Immutable borrow + copy out: the function is read-only by construction.
        let snapshot: Option<(Config, State)> = *c.borrow();
        let (cfg, mut s) = match snapshot {
            Some(x) => x,
            None => return Err(JsValue::from_str("run_trajectory: call init() first")),
        };
        let mut samples = Vec::with_capacity(n as usize + 1);
        samples.push(TrajectorySample { t: s.time, theta: s.theta, omega: s.omega });
        for _ in 0..n {
            s = step_state(s, cfg, dt);
            samples.push(TrajectorySample { t: s.time, theta: s.theta, omega: s.omega });
        }
        serde_wasm_bindgen::to_value(&samples)
            .map_err(|e| JsValue::from_str(&format!("run_trajectory: {e}")))
    })
}

// ---------------------------------------------------------------------------
// Native test surface. Not exported to wasm. The wasm-bindgen API is a thin
// wrapper over step_state and sample_trajectory.
// ---------------------------------------------------------------------------

pub fn step_state_pub(state: State, cfg: Config, dt: f64) -> State {
    step_state(state, cfg, dt)
}

pub fn sample_trajectory(state: State, cfg: Config, n: u32, dt: f64) -> Vec<TrajectorySample> {
    let mut s = state;
    let mut out = Vec::with_capacity(n as usize + 1);
    out.push(TrajectorySample { t: s.time, theta: s.theta, omega: s.omega });
    for _ in 0..n {
        s = step_state(s, cfg, dt);
        out.push(TrajectorySample { t: s.time, theta: s.theta, omega: s.omega });
    }
    out
}
