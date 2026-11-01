- Printing `A step 0` before `tasks created`. `create_task` only schedules; `main` keeps the
  thread until its first pause.
- Running A to the end before B starts. Every `sleep(0)` hands the turn to the next task
  in the queue.
- Printing `main got A` right after `A done`. `main` is woken at the **back** of the queue,
  and B is already waiting there.
- Printing `C done? True` the first time. The task was only created; it has not run yet.
- Thinking `await t1` makes `main` run A itself. `main` just waits; the loop runs A as a
  separate task.
