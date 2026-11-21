## Approach

| # | Thing | Type | Why |
|---|---|---|---|
| 1 | requests served | counter | only grows; graph `rate(...)` |
| 2 | jobs waiting in the queue | gauge | goes up and down |
| 3 | time to render a report | histogram | a duration: you want percentiles |
| 4 | memory in use | gauge | a current value |
| 5 | failed requests | counter | only grows; the error **ratio** is `rate(errors) / rate(all)` |
| 6 | jobs in flight | gauge | rises and falls |
| 7 | bytes sent | counter | monotonic total; its rate is the bandwidth |
| 8 | size of each upload | histogram | a distribution: "95% under 5 MB" is a quantile of buckets |

The chapter's answer to "Try it: which metric type?" uses the same reasoning (orders created: counter; jobs waiting: gauge; time to render a report: histogram; bytes sent: counter).

## Cost

Reading only. The choice decides what you can ask later: a gauge of "errors so far" cannot give you the error *rate*, and a counter cannot give you "how many are in the queue right now".

## Another way

Check the rule with the chapter's own metrics: `http_requests_total` (counter), `http_request_duration_seconds` (histogram), `http_requests_in_flight` (gauge). Every metric you add to a service should have a sentence: "I graph it as a rate / a level / a percentile".
