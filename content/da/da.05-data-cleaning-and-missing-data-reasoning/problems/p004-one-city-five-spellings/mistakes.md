- **Reporting the original text in `unmapped`.** `" GOA "` and `"goa."` are the same problem; list the key `goa` once.
- **Mapping before normalising.** The mapping has the key `"pune"`; `" PUNE "` is not in it. Normalise first.
- **Keeping unmapped values as they were.** Then `clean` still contains `Goa` next to the official names and the
  "all values are official" check cannot work. Unknown values become missing and are reported.
- **Listing the missing input as unmapped.** A missing value has no key; it simply stays missing.
- **Stripping only before the dot.** `"Pune . "` needs strip, strip the dot, then strip again.
- **`str.title()` instead of the mapping.** `"new delhi"` would become `"New Delhi"`, a different spelling.
