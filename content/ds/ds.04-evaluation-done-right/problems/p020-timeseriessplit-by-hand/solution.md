## Walk-through

Test size = 12 // 4 = 3. Test blocks: rows 3-5, 6-8, 9-11.

- gap 0: fold 0 trains on 0-2, fold 1 on 0-5, fold 2 on 0-8.
- gap 1: one row before each test block is left out: 0-1, 0-4, 0-7.

## Why a gap

If the label is known only some time after the event (a default is known after 60 days), the last rows before the test block could not have been used at prediction time. A gap the length of that delay makes the evaluation honest.
