## Approach

Read a test by asking "which change to the code would turn it red?". If very different
implementations pass, the test checks nothing about the logic. Mocks with fixed return values cut the
connection between input and output, so the formula in the middle is untested. Replace the mocks that
stand in for **data and logic** with fakes, and compute the expected value by hand.

See `answer.md` for the full model answer.

## Complexity

Not applicable.

## Another way

A property-style check: for any cart, `checkout(repo, identity_tax, cart + cart)` equals twice
`checkout(repo, identity_tax, cart)`. It would also catch the broken version.
