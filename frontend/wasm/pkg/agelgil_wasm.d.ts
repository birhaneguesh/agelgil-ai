/* tslint:disable */
/* eslint-disable */

export function get_state(): any;

export function init(config_js: any): void;

export function reset(): void;

/**
 * Run `n` fixed-`dt` steps and return the full trajectory.
 *
 * **Read-only**: does not advance the module state. Calling `run_trajectory`
 * twice from the same `init()` returns the same trajectory twice. Call
 * `step(dt)` in a loop if state advancement is required.
 *
 * Used by the AC-16 fixture generator in P3.02. Same `(seed, n, dt)` must
 * produce identical bytes on High and Low tiers.
 */
export function run_trajectory(n: number, dt: number): any;

export function step(dt: number): void;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly get_state: () => [number, number, number];
    readonly init: (a: any) => [number, number];
    readonly reset: () => void;
    readonly run_trajectory: (a: number, b: number) => [number, number, number];
    readonly step: (a: number) => [number, number];
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __externref_table_dealloc: (a: number) => void;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
