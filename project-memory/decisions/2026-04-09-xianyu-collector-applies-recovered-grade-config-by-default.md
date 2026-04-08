# xianyu collector applies recovered gradeConfig by default

Date: 2026-04-09

## Decision
- The vendored Xianyu collector in `mobile-use` should read recovered collector settings from `gradeConfig` by default instead of ignoring them.

## Applied behavior
- `gather_tiao_jian` now maps into collector filter defaults.
- `is_kai_qi_duo_gui_ge_cai_ji` now becomes the default multi-spec toggle.
- `lineEdit_guan_jian_ci_cai_ji_xian_zhi` now becomes the keyword-mode success cap.
- `dian_pu_cai_ji_fa_bu_tian_shu_text` now becomes the shop-mode recent-publish preset filter.

## Why
- This keeps the collector aligned with the recovered behavior of the original tool and lets a reused DB/config actually affect collection runs.
