# xianyu dismiss system overlays before preheat

Date: 2026-03-19

## Pattern
- When the device is on the notification shade or lock screen (no app package),
  dismiss the overlay with BACK/HOME and an upward swipe before opening Xianyu.

## Why it matters
- Preheat fails if the app is launched while the system overlay is still present.
