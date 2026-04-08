# xianyu network error dialog requires ack

Date: 2026-03-19

## Pattern
- When Xianyu shows `无法连接网络，请检查网络！`, the flow must tap `我知道了` to continue.
- Treat this dialog as a transient blocker that can appear right after tapping `发闲置`.
- If the dialog keeps reappearing during preheat, fail fast with a network-specific error so the
  operator can fix device connectivity.

## Why it matters
- The preheat path can stall on this dialog, preventing the listing form from opening.
