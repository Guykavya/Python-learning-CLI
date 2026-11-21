## Hint 1

For each item, imagine the script running at 3 a.m. under cron on a different machine. Where is its current working directory? Who reads its stdout? What does cron learn from exit code 0? Write the concrete situation first, then the fix.

## Hint 2

Map each problem to a piece of the skeleton of section 2.2: argument (`argparse` + `Path`), `--dry-run` with plan/apply, `logging` to stderr, `return 1` from `main()` plus `sys.exit(main())`, paths built from the input folder, `unique_destination()`. If a problem has no matching piece, it is probably your item 8.
