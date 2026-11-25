# A documented cleaning pipeline

**The project of the chapter (section 13).** An open-data CSV of hourly air-quality readings from monitoring stations
arrives dirty. The question is simple (what is the average PM2.5 per station, and how often is the limit passed?), the
cleaning is not. Build the pipeline that turns the raw table into a clean one, **and documents what it did**: a log,
a reason for every removed reading, a schema with quarantine, and a report that gives the answer **two ways**.

Write `clean_air(raw, stations=("Hill Road", "Riverside", "Airport"))`. It returns **four things**:
`(clean, flags, log, report)`. The raw table has the columns `station` (text), `ts` (text), `pm25` (float) and
`humidity` (float). It is the table of chapter 13.1 (`make_air`), with three stations and 45 days; the test file builds
it with a copy of `make_air` in `conftest.py`. The dirt, listed:

- station names in several spellings (`"Hill Road"`, `"hill-road"`, `"HILL ROAD "`, `"riverside "` ...);
- two timestamp formats: `2025-03-01 14:00` (year first) and `01/03/2025 14:00` (day first, one station);
- the code `-999` for "sensor error";
- 40 repeated rows (the logger sent them twice);
- 10 **spikes** (a reading 8 times too high), one **stuck sensor** (the same value for 36 hours), one **outage**
  (three days of missing readings) and a **fog effect** (above 85 percent humidity the sensor fails about half of the
  time: MAR).

## What the steps must do, in this order

1. **formats**: clean the station names to the canonical `"Hill Road"`, `"Riverside"`, `"Airport"` (strip, replace `-`
   by a space, title case); parse `ts` into datetimes with the format each value matches; the `-999` code becomes
   missing. Start the reason column `pm25_flag`: `"code"` where the value was `-999`, `"missing"` where it was already
   missing, `"ok"` otherwise.
2. **duplicates**: one row per `(station, ts)`, **first copy kept**; sort by `station`, `ts`.
3. **suspects** (these two rules are fixed; they are the chapter's):
   - **spike**: the reading is more than **3 times** the median of the 7 readings around it of the same station
     (a centred window of 7 hours, at least 3 readings present), or above 500. Flag `"spike"`.
   - **stuck**: the same value in **6 or more consecutive hours** of one station. Flag `"stuck"`.
   Flagged readings become missing (`pm25` is `NaN`), the **reason stays** in `pm25_flag`.
4. **validate** with a pandera schema (columns and types of the dictionary below, `unique=["station", "ts"]`, a check
   that `pm25` is present exactly when the flag is `"ok"`) and a **quarantine**: rows that fail row-wise are removed
   from `clean` (a failure that is not tied to a row, like a missing column, raises the pandera exception).
   A row with `humidity = 150`, or a timestamp in a third format, must be quarantined, not crash the pipeline.

Every step appends one dict to the `log` list (in the order of the steps), with the keys `step`, `rows_before`,
`rows_after`, `na_before`, `na_after` (number of missing cells in the whole table) and `note`; each step's
`rows_before` is the previous step's `rows_after`, and the first one is `len(raw)`.

## The four results

- `clean`: columns `station, ts, pm25, humidity, pm25_flag`; one row per station and hour; sorted by `station`, `ts`;
  index `0, 1, 2, ...`; `ts` is a datetime column; `pm25` is missing exactly when `pm25_flag != "ok"`;
  `pm25_flag` is one of `ok, code, spike, stuck, missing`.
- `flags`: a dict `{flag: number of rows}` of the final `pm25_flag` values (plain `int`s), only for flags that occur.
- `log`: the list described above (at least 4 entries).
- `report`: a text (Markdown) with the headline of the missing-data decision. It must contain **one line per
  station**, exactly in the form `<station> | A: <mean A> | B: <mean B>` (one decimal), where
  **A** is the mean `pm25` after **dropping** the missing hours and **B** is the mean after **repairing** them:
  gaps of up to 3 hours are interpolated along time within the station (`interpolate(method="time", limit=3,
  limit_area="inside")`), and the remaining gaps (where humidity is known) are predicted from a straight line of `pm25`
  on `humidity` fitted per station on the readings that exist (`np.polyfit(humidity, pm25, 1)`). The report also says in
  words that missingness depends on **humidity** (MAR), and lists the steps of the log.

## Data dictionary of `clean`

| column | type | unit | meaning and allowed values | missing allowed |
|---|---|---|---|---|
| `station` | text | - | one of the three stations | no |
| `ts` | datetime | local time | hour start; one row per station and hour | no |
| `pm25` | float | ug/m3 | 0 to 500; fine dust | yes (reason in `pm25_flag`) |
| `humidity` | float | percent | 0 to 100 | yes |
| `pm25_flag` | text | - | `ok`, `code`, `spike`, `stuck`, `missing` | no |

## What the tests check

The test keeps the **truth** (the clean readings, before the dirt) and checks that every injected problem is caught:
no wrong value survives as `"ok"` except at most one spike that sits just under the 3-times line; no honest value is
flagged as a spike; the stuck run is flagged; the duplicates are gone; the `-999` codes are counted; a bad row is
quarantined; running the pipeline twice gives the same result and the raw table is not changed; and the report names
both answers, with B closer to the truth than A.

## Example

With the test data (3,280 raw rows) a correct pipeline gives this log and flags:

```text
formats     3280 -> 3280   missing cells 229 -> 321
duplicates  3280 -> 3240   missing cells 321 -> 321
suspects    3240 -> 3240   missing cells 321 -> 365
validate    3240 -> 3240   missing cells 365 -> 365
{'ok': 2875, 'missing': 229, 'code': 92, 'stuck': 35, 'spike': 9}
```

and report lines like `Airport | A: 34.0 | B: 34.6`.
