/* tslint:disable */
/* eslint-disable */
export const memory: WebAssembly.Memory;
export const get_state: () => [number, number, number];
export const init: (a: any) => [number, number];
export const reset: () => void;
export const run_trajectory: (a: number, b: number) => [number, number, number];
export const step: (a: number) => [number, number];
export const __wbindgen_malloc: (a: number, b: number) => number;
export const __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
export const __wbindgen_free: (a: number, b: number, c: number) => void;
export const __wbindgen_externrefs: WebAssembly.Table;
export const __externref_table_dealloc: (a: number) => void;
export const __wbindgen_start: () => void;
