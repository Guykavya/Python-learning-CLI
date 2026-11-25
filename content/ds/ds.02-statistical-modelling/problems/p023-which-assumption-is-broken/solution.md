## Walk-through

- A: funnel 2.9 > 2, so `non-constant variance`.
- B: funnel 1.1 is not > 2; dw 0.9 < 1.5, so `correlated errors`.
- C: funnel 1.2 no; dw 2.1 inside [1.5, 2.5], no; max_cooks 1.4 > 1, so `influential point`.
- D: funnel 1.0 no; dw 2.0 no; cooks 0.04 no; jb_p 0.01 < 0.05, so `non-normal errors`.
- E: funnel 1.3 no; dw 2.6 > 2.5, so `correlated errors` (a negative correlation, a very small DW would show positive).
- F: funnel 2.2 > 2 wins first, so `non-constant variance`, although dw, Cook's distance and JB also look bad.
- G: nothing triggers: `no problem found`.

## Another way

A real report prints **all** flags, not only the first. The first-match rule here is only a teaching device for order of checks.
