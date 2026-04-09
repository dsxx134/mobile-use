# collector doctor should probe searchability without writing data

Updated: 2026-04-09

## Pattern
- For collector session diagnosis, do not infer health from token presence alone. Issue one real search request against a safe keyword and classify the session from the upstream result, while avoiding any DB writes.

## Why
- `_m_h5_tk` only proves signing capability.
- The practical distinction the operator cares about is whether the current session can pass `mtop.taobao.idlemtopsearch.pc.search`.
- Reusing the API client directly gives a low-noise diagnosis path with the same runtime cookie chain as real collection.
