## Model answer

The overall rate is a **weighted average** of the device rates, and the weights changed. In March mobile was 40% of the carts (rate 50%) and desktop 60% (rate 70%): 0.6 x 70 + 0.4 x 50 = 62%. In April mobile was 70% of the carts:
0.3 x 72 + 0.7 x 52 = 58.0%. The weaker device now carries most of the weight, so the total falls although **each device improved** by about two points.
This is a **mix effect**, an instance of Simpson's paradox: the comparison that is fair is **within** each device.

For the product team: the checkout did not get worse; each device slightly improved. The fall is caused by a change in who arrives (more mobile carts, perhaps from a new campaign), so a redesign aimed at "the" checkout is not justified by this number.
The real question is why mobile converts 20 points below desktop, and that can be tested separately.

Before comparing a funnel between periods, **split it by the segments that can change the mix** (device, channel, new vs returning) and compare within them, or decompose the change into mix and rate.

Two more traps: a **step defined differently** in the two periods (for example a new tracking event for "start checkout") makes the rates incomparable, and counting **sessions instead of users** lets one keen user appear many times
and hides the share of people who never get through.

**Checklist: your answer should mention**
- [ ] the overall rate is a weighted average, and the weights (mix) changed
- [ ] both devices improved: Simpson's paradox / mix effect
- [ ] compare within segments (or decompose into mix and rate) before blaming the checkout
- [ ] steps must be defined the same way in both periods
- [ ] sessions versus users
