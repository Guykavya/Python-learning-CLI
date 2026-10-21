- Expecting `red -> apple`. The later key overwrites the value.
- Expecting `red` to move to the end when it is assigned again. Re-assigning an existing key
  does not move it.
- Building the inverted dict while also reading input, which mixes up the "later wins" rule
  for repeated original keys.
