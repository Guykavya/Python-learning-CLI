## Walk-through

| feature | day | `day <= 100` | printed |
|---|---|---|---|
| created_at | 10 | yes | usable |
| last_login | 98 | yes | usable |
| support_calls_30d | 99 | yes | usable |
| plan_change | 100 | yes | usable |
| refund_issued | 115 | no | future |
| cancelled_at | 130 | no | future |

Four usable of six.

## plan_change

A value written on the prediction day is risky: was it written **before** or **after** the moment we score? If the scoring job runs at 6 a.m. and plan changes are entered during the day, the value is from the future. Ask for the exact timestamp and the time the scoring runs.
