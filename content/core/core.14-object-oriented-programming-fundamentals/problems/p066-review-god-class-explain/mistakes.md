- Only listing style issues (long lines, missing type hints). The real problems are shared state,
  hidden errors and too many responsibilities.
- Missing the class attribute `students = []`. It is the most dangerous line: data leaks between
  objects.
- Saying "add more `elif`s" for new kinds. That is exactly the growth the redesign should stop.
- Splitting into many classes that still all print and all talk to SMTP. The point is to separate
  calculation, presentation and side effects.
- Choosing subclasses of `Student` without noticing that a student's kind can change at run time.
- A design that is still impossible to test without a real mail server, because the class creates
  `smtplib.SMTP` itself instead of receiving a mailer.
