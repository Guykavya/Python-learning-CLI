- "The GIL makes my code thread-safe." It makes single bytecodes safe. Any read-modify-write
  that spans several bytecodes can be interrupted in the middle.
- "My counter test gave the right answer, so it is safe." Without a forced gap, lost updates
  are rare and random. Rare is still wrong; it fails in production under load.
- "Threads are useless in Python." They are very useful for I/O, because waiting releases the
  GIL.
- "Free-threading fixes races." It removes the GIL, so threads run at the same time and races
  show up **more** often. Locks are still needed.
- Mixing up `sys._is_gil_enabled()` (is the GIL on **right now**) with the build option
  `Py_GIL_DISABLED` (was this Python built so that it can run without it). A free-threaded
  build can re-enable the GIL, for example when it imports an extension that is not ready.
