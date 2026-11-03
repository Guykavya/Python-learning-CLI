- Stopping when a page is short (`len(data) < per_page`). Real APIs return short or empty pages
  in the middle; you lose the rest of the data without any error.
- Stopping when a page is empty. When the last page is full you pay for one more request
  (and some APIs answer that extra request with 404).
- Computing `page += 1` instead of using `next_page`. It works only until the API skips a number or changes its numbering.
- Starting at `page=0`. Most page-number APIs are 1-based; page 0 is often an error or a copy of page 1.
- Forgetting `raise_for_status()`, or catching the error and returning what you have. A partial
  result that looks complete is the worst kind of bug in a pipeline.
- Using `orders.append(body["data"])`. That builds a list of lists; `extend` adds the orders themselves.
- Hard-coding `per_page=3` in the request instead of using the argument.
