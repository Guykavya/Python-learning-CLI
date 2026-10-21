See the model answer shown when you check. The ideas that must appear:

1. A is LBYL (Look Before You Leap), B is EAFP (Easier to Ask Forgiveness than Permission).
2. Inputs such as `"-5"`, `" 7"`, `"+3"`, `"1_000"` differ; `"²"` makes A crash.
3. The file can change between the check and the open: a race condition (TOCTOU). EAFP detects the
   failure at the moment of use.
4. LBYL fits simple exact checks, frequent failures, and all-or-nothing work.
