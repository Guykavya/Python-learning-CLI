1. **Unit.** One pure function and many cheap inputs. Nothing to fake. Twelve cases cost almost
   nothing, so this is the ideal place for lots of edge cases (parametrize them).
2. **Integration.** Two functions and the real file system are involved, and the point is that
   they agree with each other (file format). Keep the disk real but safe: write into pytest's
   `tmp_path`, never into a real folder.
3. **Unit.** Only the discount logic matters, so pass a **fake gateway** (an object with a
   `charge` method that records the amount). That keeps the test fast and means no real money
   moves. Then assert on what was charged.
4. **End-to-end.** The question is "does the whole product work for a user?", so browser, web
   server, database and payment page are all real (the payment provider's test mode). Slow and
   sometimes flaky, so only a few of these (the main happy path).
5. **Integration.** Reader, cleaner, aggregator and writer run together in one process. Use
   `tmp_path` for the input and output files and call `main(argv)` directly. No browser and no
   network, so it is much quicker than an e2e test but still proves the pieces fit.
6. **Integration** against the real service (a contract check), run rarely and separately, for
   example nightly, because it needs the network and can fail for reasons outside your code. In
   the fast suite you test the parsing of a saved sample response instead (unit).

**Why a pyramid.** Unit tests are fast, precise (a failure points at one function) and cheap to
write, so you want hundreds of them. End-to-end tests are slow, break for unrelated reasons and
tell you only "something is wrong", so you keep a handful for the critical paths and let the
layers below do the detailed checking.
