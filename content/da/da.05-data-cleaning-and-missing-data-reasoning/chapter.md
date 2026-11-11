# Chapter 5 (DA): Data cleaning and missing-data reasoning

Every analyst learns the same lesson the hard way: **the code is easy, the data is not.** In da.03 and da.04 the tables were tidy. Real tables are not. Names are spelled five ways. A date column holds three date formats. An age of `999` means "the person did not answer". A salary was typed with two extra zeros. The same person filled in the form twice. And in almost every column, some values are simply *missing*.

You can fix all of this in a few lines of pandas. That is the easy part. The hard part is **judgement**: which fix is honest? If you delete the rows with a missing income, does your average income go up or down? If you fill the blanks with the mean, what happens to the spread? The same dataset, cleaned by two careful people, can give two different answers, and both people can say "I only did the obvious thing".

By the end of this chapter you reach one outcome: **you can show how two reasonable missing-data choices give two different answers**, and you can say which one to trust and why. On the way you learn the cleaning toolkit: duplicates, outliers, inconsistent formats, regex inside pandas, and validation rules written as code with **pandera**. The chapter ends with a documented cleaning pipeline you can reuse.

Prerequisites: da.04 (groupby, merge, method chaining, categoricals) and core.18 (regular expressions). We use `re` ideas (groups, alternation, quantifiers, anchors) inside pandas string methods, and you should be comfortable with `groupby`, `transform`, `pipe` and `assign`.

> **Offline rule for this chapter.** pandas, NumPy and pandera are installed in the course environment. No internet is needed. Every dataset is **synthetic**: built in code with seeded random numbers (`numpy.random.default_rng`), so you get the same numbers I did. Because *we* make the data, we also keep the **truth** (the clean values before we messed them up). That lets us check a cleaning step against reality, something you almost never can do with real data. Every output block below was produced by running the code above it, in one session from top to bottom. **Timings, versions and temporary paths are machine-specific.** Some blocks show a warning or an error on purpose; for errors we print only the last line. This chapter uses **pandas 3**; where older tutorials say something different, I show what really happens. These are the versions used:

```python run
import sys, platform, re
import numpy as np
import pandas as pd
import pandera
import pandera.pandas as pa

print("python ", sys.version.split()[0])
print("pandas ", pd.__version__)
print("numpy  ", np.__version__)
print("pandera", pandera.__version__)
```
```text
python  3.14.4
pandas  3.1.1
numpy   2.5.4
pandera 0.36.0
```

Two setup lines make the printed tables compact (they change only how tables are *shown*).

```python run
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_rows", 14)
pd.set_option("display.float_format", "{:,.2f}".format)
print("display options set")
```
```text
display options set
```

## Table of contents

1. [Cleaning is analysis, not housekeeping](#1-cleaning-is-analysis-not-housekeeping)
2. [The audit: look before you touch](#2-the-audit-look-before-you-touch)
3. [Inconsistent formats and fake values](#3-inconsistent-formats-and-fake-values)
4. [Regex inside pandas](#4-regex-inside-pandas)
5. [Duplicates](#5-duplicates)
6. [Outliers](#6-outliers)
7. [Missing values: the mechanics](#7-missing-values-the-mechanics)
8. [Why values are missing](#8-why-values-are-missing)
9. [When dropping or filling changes the answer](#9-when-dropping-or-filling-changes-the-answer)
10. [Validation by hand](#10-validation-by-hand)
11. [Validation with pandera](#11-validation-with-pandera)
12. [A cleaning pipeline you can trust](#12-a-cleaning-pipeline-you-can-trust)
13. [Project: a documented cleaning pipeline](#13-project-a-documented-cleaning-pipeline)
14. [Common traps](#14-common-traps)
15. [Summary](#15-summary)

## 1. Cleaning is analysis, not housekeeping

### 1.1 Four rules before any code

Beginners treat cleaning as a chore to finish quickly. Experienced analysts treat it as the part of the job where most wrong answers are born. Four rules keep you safe.

1. **Never edit the raw data.** Keep the original file untouched. Your cleaning is a *script* that reads the raw file and writes a new clean file. If you find a mistake next week, you fix the script and run it again. If you had edited by hand, you could never reproduce it.
2. **Every change must be countable.** "I removed duplicates" is not a log entry. "I removed 45 rows (7%) because the whole row was repeated" is. If a step changes many rows, you should know it and say it.
3. **Flag before you delete.** Adding a column `is_outlier` costs nothing and can be undone. Deleting the row cannot. Delete only when you have a reason you can write down.
4. **A missing value is information.** *Why* it is missing often matters more than the value you could put there. Section 8 is about this.

### 1.2 A messy survey with a known truth

Our dataset is a **customer survey** with 600 respondents in six cities. The factory below first builds the clean **truth** table, then makes a **raw** copy and breaks it in the ways real data breaks. Read the comments: they list every kind of dirt we plant. Later sections clean them one by one.

```python run
FIRST = ["asha", "ravi", "meera", "kabir", "isha", "dev", "nina", "omar", "tara", "arjun"]
CITIES = ["Pune", "Delhi", "Mumbai", "Chennai", "Kolkata", "Jaipur"]


def make_survey(n=600, seed=11):
    rng = np.random.default_rng(seed)
    # ---------- the truth: clean values ----------
    truth = pd.DataFrame({
        "resp_id": np.arange(1001, 1001 + n),
        "age": rng.integers(18, 76, n),
        "city": rng.choice(CITIES, n, p=[.2, .25, .25, .1, .1, .1]),
        "income": (rng.lognormal(10.6, 0.5, n)).round(-2).astype(int),  # monthly, rupees
        "satisfaction": rng.integers(1, 11, n),
        "signup": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 600, n), unit="D"),
    })
    truth["phone"] = [str(x) for x in rng.integers(6_000_000_000, 9_999_999_999, n)]
    truth["email"] = [f"{rng.choice(FIRST)}{i}@mail.example" for i in truth["resp_id"]]

    # ---------- the raw copy: plant the dirt ----------
    raw = truth.copy()
    # (a) city: lower case, UPPER with spaces, trailing space, a dot, two typos
    style = rng.choice(["ok", "lower", "upper", "space", "dot"], n, p=[.55, .15, .1, .15, .05])
    c = raw["city"].astype(object)
    c = np.where(style == "lower", c.str.lower(), c)
    c = np.where(style == "upper", " " + pd.Series(c).str.upper() + "  ", c)
    c = np.where(style == "space", pd.Series(c) + " ", c)
    c = np.where(style == "dot", pd.Series(c) + ".", c)
    c = pd.Series(c).replace({"Mumbai": "Mumbay", "Delhi": "Dehli"}).where(rng.random(n) < 0.04, pd.Series(c))
    raw["city"] = c.values
    # (b) income as text: rupee sign, commas, "Rs.", "N/A", a -999 code, empty; 8 values keyed with 2 extra zeros
    inc = raw["income"].copy()
    big = rng.choice(n, 8, replace=False)
    inc.iloc[big] = inc.iloc[big] * 100
    kind = rng.choice(["plain", "rupee", "rs", "na", "code", "empty"], n, p=[.55, .22, .1, .05, .04, .04])
    txt = []
    for v, k in zip(inc, kind):
        txt.append({"plain": str(v), "rupee": f"₹{v:,}", "rs": f"Rs. {v}", "na": "N/A",
                    "code": "-999", "empty": ""}[k])
    raw["income"] = txt
    # (c) age: -1 / 999 codes, a few real blanks, two impossible values
    age = raw["age"].astype(float)
    age[rng.random(n) < 0.03] = 999
    age[rng.random(n) < 0.02] = np.nan
    age.iloc[[5, 77]] = [0, 150]
    raw["age"] = age
    # (d) signup date as text in three styles
    d = truth["signup"]
    sty = rng.choice([0, 1, 2], n, p=[.5, .3, .2])
    raw["signup"] = [x.strftime(["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"][s]) for x, s in zip(d, sty)]
    # (e) phone: five formats and a few too-short values
    ph = []
    for p, s in zip(truth["phone"], rng.choice(range(6), n, p=[.4, .15, .15, .1, .1, .1])):
        ph.append([p, f"{p[:5]} {p[5:]}", f"+91-{p[:5]}-{p[5:]}", f"(+91) {p}", f"0{p[:5]}-{p[5:]}", p[:7]][s])
    raw["phone"] = ph
    # (f) email: upper case, spaces around, a missing @
    em = truth["email"].copy()
    s2 = rng.choice(["ok", "upper", "pad", "noat"], n, p=[.8, .08, .08, .04])
    em = np.where(s2 == "upper", em.str.upper(), em)
    em = np.where(s2 == "pad", " " + pd.Series(em) + " ", em)
    em = np.where(s2 == "noat", pd.Series(em).str.replace("@", "", regex=False), em)
    raw["email"] = em
    # (g) duplicates: 20 exact repeats + 15 re-submissions (new id, same email, newer score)
    exact = raw.sample(20, random_state=1)
    resub = raw.sample(15, random_state=2).copy()
    resub["resp_id"] = np.arange(2001, 2016)
    resub["satisfaction"] = rng.integers(1, 11, 15)
    raw = pd.concat([raw, exact, resub], ignore_index=True)
    return truth, raw


truth, raw = make_survey()
print("truth:", truth.shape, " raw:", raw.shape)
print(raw.head(6).to_string())
```
```text
truth: (600, 8)  raw: (635, 8)
   resp_id   age        city income  satisfaction        signup            phone                   email
0     1001 25.00        pune  49900             1    2024-10-30      78742 73841  kabir1001@mail.example
1     1002 25.00   CHENNAI    66000             9    2024-07-12       8235979882  MEERA1002@MAIL.EXAMPLE
2     1003 64.00      Delhi.    N/A             6    2024-11-01      78466 39686   NINA1003@MAIL.EXAMPLE
3     1004 46.00        pune  40600             2    15/10/2024  +91-97265-12225    dev1004@mail.example
4     1005 52.00     Mumbai   21800             7    2024-11-12      66073 75246   nina1005@mail.example
5     1006  0.00     Chennai  45400             5  Mar 30, 2025       7088191626   tara1006@mail.example
```

The raw table has 635 rows: the 600 real respondents plus 35 extra rows we planted as duplicates. Look at the first rows. You can already see three kinds of dirt before running a single check. We do not trust our eyes for a whole table, though. We build an audit.

> **Predict the output.** The truth has 600 respondents. Which will be *larger* for the cleaned data: the number of rows (635 now), or the number of cities (how many distinct spellings are there)? Make a guess for the number of distinct city strings before you run the audit in section 2.

<details><summary>Answer</summary>

Rows will become **smaller** (back near 600) and distinct city strings will also become smaller (down to the 6 real cities). Section 2 counts the spellings: there are far more than 6, because lower case, upper case, spaces, dots and typos each create a new string. Cleaning *reduces* both numbers. A rising count after a cleaning step is a sign that something went wrong.

</details>

### 1.3 The change log

Rule 2 says every change must be countable. We make that automatic with a tiny helper. It records, for each step, how many rows and how many missing cells there were before and after. We use it for the rest of the chapter.

```python run
LOG = []


def log_step(name, before, after, note=""):
    """Record what a cleaning step did to the table."""
    LOG.append({
        "step": name,
        "rows_before": len(before), "rows_after": len(after),
        "na_before": int(before.isna().sum().sum()), "na_after": int(after.isna().sum().sum()),
        "note": note,
    })
    return after


def show_log():
    return pd.DataFrame(LOG)


_ = log_step("load raw file", raw, raw, "no change; start of the log")
print(show_log().to_string(index=False))
```
```text
         step  rows_before  rows_after  na_before  na_after                        note
load raw file          635         635         14        14 no change; start of the log
```

A log like this is also the start of the **documentation** that the project (section 13) requires. A cleaning pipeline nobody can read is a pipeline nobody can trust.

## 2. The audit: look before you touch

### 2.1 The standard first look

Run the same five questions on every new table.

1. **Shape**: how many rows and columns?
2. **Types**: what did pandas guess, and is it right?
3. **Missing**: how many `NaN`, per column?
4. **Distinct values**: how many unique values, per column? (A column with 6 expected cities and 40 unique strings has a problem.)
5. **Ranges and samples**: minimum, maximum, the most common values.

```python run
print(raw.shape)
print(raw.dtypes)
```
```text
(635, 8)
resp_id           int64
age             float64
city                str
income              str
satisfaction      int64
signup              str
phone               str
email               str
dtype: object
```

Note the dtypes. `income` is text (it contains `₹`, commas and `N/A`), `signup` is text (three formats), and `age` is `float64` because it has `NaN`. In pandas 3 the text columns have the dtype `str`; in older versions you would see `object`. The `signup` column being text, not a date, is the first thing to fix.

```python run
def audit(df):
    """One row per column: type, missing count, distinct count, and one example."""
    out = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing": df.isna().sum(),
        "pct_missing": (df.isna().mean() * 100).round(1),
        "distinct": df.nunique(),
        "example": df.iloc[0],
    })
    return out


print(audit(raw).to_string())
```
```text
                dtype  missing  pct_missing  distinct                 example
resp_id         int64        0         0.00       615                    1001
age           float64       14         2.20        61                   25.00
city              str        0         0.00        32                    pune
income            str        0         0.00       448                   49900
satisfaction    int64        0         0.00        10                       1
signup            str        0         0.00       500              2024-10-30
phone             str        0         0.00       600             78742 73841
email             str        0         0.00       600  kabir1001@mail.example
```

Read it column by column. `city` has far more than 6 distinct values. `resp_id` has 615 distinct values, not 635: the 20 exact repeats carry the same id twice, so the id column alone already reveals them. `age` shows 14 missing values and `income` shows none, but the *text* codes (`N/A`, `-999`, empty text, `999`) are not counted as missing yet, because pandas does not know they mean "missing". That is the central trap of the next section: **missing values hide behind fake values.**

### 2.2 Looking at the values, not only the counts

`value_counts` is the best cleaning tool in pandas. A single call shows every spelling at once.

```python run
print(raw["city"].value_counts().to_string())
```
```text
city
Delhi         100
Mumbai         85
Pune           76
Kolkata        30
Chennai        28
delhi          28
Jaipur         26
Mumbai         25
Delhi          24
mumbai         24
pune           19
Jaipur         15
 DELHI         15
Delhi.         14
Chennai        14
 MUMBAI        12
 PUNE          12
kolkata        11
Pune           11
Pune.           9
 JAIPUR         8
jaipur          7
Mumbay          7
Kolkata         6
chennai         5
 KOLKATA        5
Mumbai.         5
 CHENNAI        4
Kolkata.        4
Dehli           3
Chennai.        2
Jaipur.         1
```

Every row of that table is a spelling someone typed. Count how many of them are really `Pune`. Now a numeric column: `describe` shows the range, and the range is where fake values give themselves away.

```python run
print(raw["age"].describe().round(1).to_string())
print()
print("ages above 100:", sorted(float(a) for a in raw.loc[raw["age"] > 100, "age"].unique()))
print("ages below 18 :", sorted(float(a) for a in raw.loc[raw["age"] < 18, "age"].unique()))
```
```text
count   621.00
mean     64.70
std     132.40
min       0.00
25%      31.00
50%      47.00
75%      62.00
max     999.00

ages above 100: [150.0, 999.0]
ages below 18 : [0.0]
```

The survey was for adults from 18 to 75. A maximum of 999 and a minimum of 0 are not ages. They are **sentinel values** (a special number that means "no answer" or "error") and **data entry mistakes**. If you now compute the mean age, the 999s drag it far up. We will measure the damage in section 3.

> **Try it.** Write a one-line expression that shows how many rows have an `income` text of exactly `"N/A"`, `"-999"` or `""` (empty text). Hint: `isin`.

<details><summary>Answer</summary>

```python run
codes = ["N/A", "-999", ""]
print(raw["income"].isin(codes).sum())
print(raw["income"].isin(codes).mean().round(3))
```
```text
86
0.135
```

These rows are *missing* in meaning, but pandas counts them as ordinary text. About one row in seven (13.5 percent) has no usable income, even though `isna()` reports almost none.

</details>

## 3. Inconsistent formats and fake values

### 3.1 Text: strip, case, and a mapping table

The `str` accessor does the cheap fixes. Three methods solve most spelling problems: `strip` (remove spaces at both ends), `lower` / `title` (one case), and `replace`.

```python run
city = raw["city"].str.strip().str.rstrip(".").str.title()
print(city.value_counts().to_string())
```
```text
city
Delhi      181
Mumbai     151
Pune       127
Jaipur      57
Kolkata     56
Chennai     53
Mumbay       7
Dehli        3
```

Down to eight spellings. The remaining odd ones are real **typos** (`Mumbay`, `Dehli`). Do not try to fix typos with clever code first. The safest method is a **mapping table** that you write down: it is explicit, reviewable, and you can reuse it next month.

```python run
CITY_FIX = {"Mumbay": "Mumbai", "Dehli": "Delhi"}
city = city.replace(CITY_FIX)
unknown = sorted(set(city) - set(CITIES))
print("cities not in the official list:", unknown)
print(city.nunique(), "distinct cities")
```
```text
cities not in the official list: []
6 distinct cities
```

The empty list is the **check**. After a mapping, always test that everything now belongs to the allowed set. If it does not, the leftover values are printed and you extend the table. This is a tiny version of validation, which we grow into pandera in section 11.

### 3.2 Numbers stored as text

`income` is text such as `"₹45,200"`, `"Rs. 31000"` and `"N/A"`. We need a number. The recipe has three steps: **remove the decoration, turn the codes into missing, convert.**

```python run
def parse_income(s):
    s = s.str.replace(r"[₹,]|Rs\.\s*", "", regex=True).str.strip()   # drop symbols, commas, "Rs. "
    s = s.replace({"": pd.NA, "N/A": pd.NA, "-999": pd.NA})           # codes mean "missing"
    return pd.to_numeric(s, errors="raise")                            # raise: any leftover is a bug


income = parse_income(raw["income"])
print(income.dtype, " missing:", income.isna().sum())
print(income.describe().round(0).to_string())
```
```text
float64  missing: 86
count         549.00
mean      118,614.00
std       593,946.00
min         7,800.00
25%        28,800.00
50%        39,700.00
75%        55,700.00
max     5,820,000.00
```

We used `errors="raise"` on purpose. With `errors="coerce"`, anything that cannot be parsed silently becomes `NaN`, and you lose the chance to learn *what* was unparseable. Use `raise` while you build the cleaner and learn the dirt; switch to `coerce` only if you also count how many values it turned into missing.

```python run
bad = pd.to_numeric(pd.Series(["120", "1,200", "N/A"]), errors="coerce")
print(bad.tolist())
try:
    pd.to_numeric(pd.Series(["120", "1,200", "N/A"]), errors="raise")
except ValueError as e:
    print("ValueError:", e)
```
```text
[120.0, nan, nan]
ValueError: Unable to parse string '1,200' at position 1
```

With `coerce`, `"1,200"` became `NaN` too, a perfectly good number that we threw away because of the comma. That is why we removed decoration first.

Look at the `max` of the parsed income. It is more than 100 times the median. Those are the 8 values with two extra zeros. They are **outliers**, and section 6 deals with them. Parsing is not the place to fix them.

### 3.3 Sentinel codes in numbers

Age used `999` for "no answer". The rule is the same: replace a code that *means missing* by a real missing value, so that `mean`, `isna` and every other tool treat it properly. First measure the damage.

```python run
age_raw = raw["age"]
print("mean age with the 999 codes :", round(age_raw.mean(), 1))
age = age_raw.mask(age_raw.isin([999, 0, 150]))     # impossible values become missing
print("mean age after masking      :", round(age.mean(), 1))
print("truth mean age (600 people) :", round(truth["age"].mean(), 1))
```
```text
mean age with the 999 codes : 64.7
mean age after masking      : 46.2
truth mean age (600 people) : 46.2
```

Fewer than three fake values per hundred rows moved the mean by 18 years. `mask` keeps the values where the condition is false and writes `NaN` where it is true; the opposite is `where`. Keep an eye on the choice between *replace with missing* and *drop the row*. We replace with missing, because the row may still hold good information in the other columns.

> **Predict the output.** The ages `0` and `150` appear once each. If we had used the rule "valid ages are 18 to 75" instead of listing the three bad values, how many ages would we have masked? Would the result differ from the list?

<details><summary>Answer</summary>

```python run
rule = age_raw.where(age_raw.between(18, 75))
print("masked by list:", age.isna().sum() - age_raw.isna().sum())
print("masked by rule:", rule.isna().sum() - age_raw.isna().sum())
print("same result   :", rule.equals(age))
```
```text
masked by list: 14
masked by rule: 14
same result   : True
```

The range rule masks exactly the same values here, but it is better: it also catches `-1`, `17` or `200` if they ever show up next month. A list of known bad values only catches the bad values you have already seen. **Describe what valid looks like, not what invalid looks like.** Pandera (section 11) is built on this idea.

</details>

### 3.4 Dates: three formats in one column

`signup` holds `"2024-03-05"`, `"05/03/2024"` and `"Mar 05, 2024"`. `pd.to_datetime` can parse many formats, but mixing them is dangerous because of one ambiguity: is `05/03/2024` the 5th of March or the 3rd of May? pandas does not know. Without a hint it assumes month first for slash dates, which is wrong for our survey (day first, Indian style).

```python run
sample = pd.Series(["2024-03-05", "05/03/2024", "Mar 05, 2024"])
print(pd.to_datetime(sample, format="mixed", dayfirst=True).tolist())
print(pd.to_datetime(sample, format="mixed", dayfirst=False).tolist())
```
```text
[Timestamp('2024-05-03 00:00:00'), Timestamp('2024-03-05 00:00:00'), Timestamp('2024-03-05 00:00:00')]
[Timestamp('2024-03-05 00:00:00'), Timestamp('2024-05-03 00:00:00'), Timestamp('2024-03-05 00:00:00')]
```

Each setting gets one string wrong. With `dayfirst=True`, the ISO date `2024-03-05` is read as 3 May (year, day, month!). With `dayfirst=False`, the slash date `05/03/2024` is read as 3 May instead of 5 March. Both calls ran without error, and **neither warns you**. A date parser that works is not a date parser that is right. The safest method is to parse each format with an **explicit format string** and check that every row was claimed by exactly one format.

```python run
def parse_signup(s):
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    patterns = [(r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
                (r"^\d{2}/\d{2}/\d{4}$", "%d/%m/%Y"),
                (r"^[A-Z][a-z]{2} \d{2}, \d{4}$", "%b %d, %Y")]
    claimed = pd.Series(0, index=s.index)
    for rx, fmt in patterns:
        m = s.str.match(rx)
        out[m] = pd.to_datetime(s[m], format=fmt)
        claimed += m.astype(int)
    assert (claimed == 1).all(), f"{(claimed != 1).sum()} rows matched no format or two formats"
    return out


signup = parse_signup(raw["signup"])
print(signup.dtype, signup.min().date(), signup.max().date())
same = (signup.iloc[:600].values == truth["signup"].values).mean()
print("matches the truth for the first 600 rows:", round(same * 100, 1), "%")
```
```text
datetime64[ns] 2024-01-01 2025-08-22
matches the truth for the first 600 rows: 100.0 %
```

Because we kept the truth, we can prove that all 600 dates are right. In real life you cannot compare to a truth, so you rely on the assertion: *every row matched exactly one known pattern*. If next month's file contains a fourth format, the `assert` stops the pipeline and tells you how many rows are unclaimed. A loud failure beats a silent wrong answer.

> **Try it.** Which dates would be wrong (and not raise an error) if you parsed the whole column with `pd.to_datetime(..., dayfirst=False, format="mixed")`? Count how many rows have a slash date whose first number is 13 or more. Those would fail or be misread.

<details><summary>Answer</summary>

```python run
slash = raw["signup"].str.match(r"^\d{2}/\d{2}/\d{4}$")
first = raw.loc[slash, "signup"].str[:2].astype(int)
print("slash dates:", slash.sum())
print("first number above 12 (cannot be a month):", (first > 12).sum())
print("first and second number both <= 12 (ambiguous):", (first.le(12) & raw.loc[slash, "signup"].str[3:5].astype(int).le(12)).sum())
```
```text
slash dates: 182
first number above 12 (cannot be a month): 108
first and second number both <= 12 (ambiguous): 74
```

The "above 12" rows would be impossible months and give an error or a wrong guess. The "ambiguous" rows are the dangerous ones: they parse without any complaint and silently swap day and month.

</details>

### 3.5 Units and categories

Two more format problems appear everywhere. First, **mixed units**: one source reports height in cm, another in inches; one reports money in rupees, another in thousands. The only cure is to find the unit per source and convert to one unit, then write the unit in the column name (`income_inr`, `height_cm`). Second, **category labels**: `Yes`, `Y`, `yes`, `1`, `True` all mean one thing.

```python run
answers = pd.Series(["Yes", "y", "NO", "no ", "1", "True", "maybe", None, "N"])
yes = {"yes", "y", "1", "true"}
no = {"no", "n", "0", "false"}
norm = answers.str.strip().str.lower()
clean = pd.Series(np.select([norm.isin(yes), norm.isin(no)], [True, False], default=None), index=answers.index, dtype="object")
clean[norm.isna()] = None
print(pd.DataFrame({"raw": answers, "clean": clean}).to_string())
```
```text
     raw  clean
0    Yes   True
1      y   True
2     NO  False
3    no   False
4      1   True
5   True   True
6  maybe   None
7    NaN   None
8      N  False
```

`maybe` is neither yes nor no, so it falls to the default and stays missing. Notice what we did *not* do: we did not guess. A value we cannot interpret becomes missing (and is counted in the log), instead of becoming a wrong `True`.

## 4. Regex inside pandas

In core.18 you used `re.search`, `re.sub` and groups on one string at a time. pandas gives you the same tools for a whole column at once, through the `str` accessor. The patterns are exactly the ones you know; only the calling style changes.

### 4.1 The `str` methods that take a regex

| Method | Question it answers | Returns |
|---|---|---|
| `s.str.contains(rx)` | does the pattern appear anywhere? | bool Series |
| `s.str.match(rx)` | does the pattern match at the **start**? | bool Series |
| `s.str.fullmatch(rx)` | does the pattern match the **whole** string? | bool Series |
| `s.str.extract(rx)` | give me the first match's groups | DataFrame (one column per group) |
| `s.str.extractall(rx)` | give me **all** matches | DataFrame with a `match` level |
| `s.str.replace(rx, new, regex=True)` | substitute | Series |
| `s.str.split(rx, regex=True)` | cut on the pattern | Series of lists, or a DataFrame with `expand=True` |
| `s.str.count(rx)` | how many matches? | int Series |

Two details cause most bugs. First, since pandas 2, `str.replace` treats the pattern as plain text unless you write `regex=True`; always write it, so the reader knows. Second, `contains` and `match` differ: `contains` searches anywhere, `match` anchors at the start. For validation, prefer **`fullmatch`**, because it cannot be fooled by extra characters after the pattern.

```python run
s = pd.Series(["98765 43210", "9876543210", "98765x43210", "12345", None])
print(pd.DataFrame({
    "text": s,
    "contains": s.str.contains(r"\d{10}"),
    "match": s.str.match(r"\d{10}"),
    "fullmatch": s.str.fullmatch(r"\d{10}"),
}).to_string())
```
```text
          text  contains  match  fullmatch
0  98765 43210     False  False      False
1   9876543210      True   True       True
2  98765x43210     False  False      False
3        12345     False  False      False
4          NaN     False  False      False
```

Two things to see. `98765 43210` has 10 digits but a space in the middle, so none of the three tests accept it: we need to clean first and then test. And the `None` row gives `False` in every column. That is the pandas 3 `str` dtype at work; with the old `object` dtype the same call returns `NaN` for missing text, and the next step (using it as a mask) fails. The `na=` argument sets what to return for missing text on purpose, for example `s.str.contains(rx, na=False)`. Write it, so your code means the same on every version.

### 4.2 Phone numbers: normalise, then validate

The raw phones have six styles. The plan: remove everything that is not a digit, drop a leading country code `91` or a leading `0` when the result is too long, and finally keep only 10-digit numbers.

```python run
def clean_phone(s):
    digits = s.str.replace(r"\D", "", regex=True)                  # keep digits only
    digits = digits.str.replace(r"^(?:91|0)(?=\d{10}$)", "", regex=True)   # drop country code / trunk 0
    return digits.where(digits.str.fullmatch(r"[6-9]\d{9}"))        # valid mobile or missing


phone = clean_phone(raw["phone"])
print("valid phones :", phone.notna().sum(), "of", len(phone))
print("invalid      :", phone.isna().sum())
print(raw.loc[phone.isna(), "phone"].head(5).tolist())
```
```text
valid phones : 582 of 635
invalid      : 53
['8654355', '9063087', '8744977', '7795266', '9831774']
```

The invalid ones are the 7-digit cut-off numbers we planted, plus anything that cannot be a mobile number. We did not delete those rows; the phone just becomes missing. The pattern `(?=\d{10}$)` is a **lookahead**: it says "only remove the `91` or `0` if exactly ten digits follow". Without it, a real number that *starts* with 9 and 1 (like `9123456789`) would lose its first two digits. Test it:

```python run
tests = pd.Series(["+91 98765 43210", "9123456789", "09876543210", "91234"])
print(clean_phone(tests).tolist())
```
```text
['9876543210', '9123456789', '9876543210', nan]
```

`9123456789` survived intact: after the leading `91` there are 8 digits, not 10, so the lookahead refused to remove it. `+91 98765 43210` and `09876543210` lost their prefix, and `91234` (too short) became missing. A small test set of tricky inputs like this one is the best way to trust a regex. In section 12 we move such tests into the pipeline.

### 4.3 Emails: clean first, then check

```python run
def clean_email(s):
    e = s.str.strip().str.lower()
    return e.where(e.str.fullmatch(r"[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+"))


email = clean_email(raw["email"])
print("valid emails:", email.notna().sum(), " invalid:", email.isna().sum())
print(raw.loc[email.isna(), "email"].head(4).tolist())
```
```text
valid emails: 610  invalid: 25
['meera1042mail.example', 'asha1044mail.example', 'omar1103mail.example', 'nina1109mail.example']
```

The invalid ones are the 4 percent that lost their `@`. We made the pattern simple on purpose. The full rules for email addresses are very complicated, and a "perfect" regex is not worth chasing. For analysis, the goal is "looks like an email, so it can be used as a key". Do not use regex to check whether an address *exists*; only sending mail can do that.

### 4.4 `extract`: pull pieces out

`extract` with **named groups** gives a DataFrame whose columns carry the group names. This turns text into columns in one step.

```python run
em = email.dropna()
parts = em.str.extract(r"^(?P<name>[a-z]+)(?P<number>\d+)@(?P<domain>.+)$")
print(parts.head(4).to_string())
print(parts["name"].value_counts().head(4).to_string())
```
```text
    name number        domain
0  kabir   1001  mail.example
1  meera   1002  mail.example
2   nina   1003  mail.example
3    dev   1004  mail.example
name
kabir    69
nina     64
dev      64
isha     63
```

If the pattern does not match a row, all its group columns are `NaN`. That makes `extract` a handy checker too: `parts.isna().any(axis=1).sum()` counts the rows that did not follow the expected shape. With `extractall`, a string with several matches gives several rows, indexed by `(original_row, match_number)`:

```python run
notes = pd.Series(["paid 450 and 120", "nothing here", "refund 80"], name="note")
nums = notes.str.extractall(r"(\d+)")
print(nums.to_string())
print(nums[0].astype(int).groupby(level=0).sum().to_string())
```
```text
           0
  match     
0 0      450
  1      120
2 0       80
0    570
2     80
```

Row 1 ("nothing here") has no matches, so it is simply absent from `extractall`'s result. When you group back by `level=0` it is missing from the totals as well, which is a classic way to lose rows. Reindex to the original index if you need every row.

### 4.5 Regex performance and safety

`str` methods on a million rows run a Python loop under the hood; they are fine for cleaning but slower than numeric code. Two habits help. Run the regex on the **unique values** and map back, when the column has few distinct values (like `city`). And compile your thinking, not your pattern: a pattern you cannot explain in one sentence is a pattern that should be split into two steps (as we did for phones: first remove non-digits, then check the shape).

```python run
uniq = raw["phone"].drop_duplicates()
mapping = dict(zip(uniq, clean_phone(uniq)))
phone2 = raw["phone"].map(mapping)
print("same result via unique values:", phone2.equals(phone) or phone2.fillna("").equals(phone.fillna("")))
print("distinct raw phones:", len(uniq), "of", len(raw))
```
```text
same result via unique values: True
distinct raw phones: 600 of 635
```

Here almost every phone is unique, so there is no saving. The trick pays off for columns such as city, country or product code.

> **Try it.** Write a pattern with `str.extract` that pulls the **year** out of a text such as `"order-2024-0042"`, and use it on `pd.Series(["order-2024-0042", "order-2023-0007", "n/a"])`. What do you get for `"n/a"`?

<details><summary>Answer</summary>

```python run
ids = pd.Series(["order-2024-0042", "order-2023-0007", "n/a"])
print(ids.str.extract(r"-(\d{4})-")[0].tolist())
```
```text
['2024', '2023', nan]
```

The result for `"n/a"` is `NaN`: no match gives a missing value, never an error and never an empty string. Remember to convert with `astype(int)` only after you dealt with the `NaN`, or use `"Int64"`.

</details>


## 5. Duplicates

### 5.1 Put the cleaned columns together

So far we cleaned columns one by one. Before we hunt for duplicates, we assemble the cleaned columns into one table, `step1`. Duplicates are easier to find in clean data: `"Pune"` and `"pune "` are different strings but the same city.

```python run
step1 = pd.DataFrame({
    "resp_id": raw["resp_id"],
    "age": age.astype("Int64"),
    "city": city.astype("category"),
    "income": income,
    "satisfaction": raw["satisfaction"],
    "signup": signup,
    "phone": phone,
    "email": email,
    "email_key": raw["email"].str.strip().str.lower(),      # kept for matching, see 5.4
})
_ = log_step("clean formats", raw, step1, "text -> numbers, dates; codes -> missing")
print(step1.dtypes.to_string())
print(step1.head(4).to_string())
```
```text
resp_id                  int64
age                      Int64
city                  category
income                 float64
satisfaction             int64
signup          datetime64[ns]
phone                      str
email                      str
email_key                  str
   resp_id  age     city    income  satisfaction     signup       phone                   email               email_key
0     1001   25     Pune 49,900.00             1 2024-10-30  7874273841  kabir1001@mail.example  kabir1001@mail.example
1     1002   25  Chennai 66,000.00             9 2024-07-12  8235979882  meera1002@mail.example  meera1002@mail.example
2     1003   64    Delhi       NaN             6 2024-11-01  7846639686   nina1003@mail.example   nina1003@mail.example
3     1004   46     Pune 40,600.00             2 2024-10-15  9726512225    dev1004@mail.example    dev1004@mail.example
```

Note `age` is now the nullable integer type `Int64` (capital I): whole numbers *and* a proper missing value. Section 7 explains why this type exists.

### 5.2 Exact duplicates

`duplicated()` returns a Boolean Series that is `True` for every row that repeats an **earlier** row. The `keep` argument decides which copy counts as "the original".

| `keep=` | Which rows are marked `True` |
|---|---|
| `"first"` (default) | every repeat after the first copy |
| `"last"` | every repeat before the last copy |
| `False` | **all** copies, including the first |

```python run
cols = ["resp_id", "age", "city", "income", "satisfaction", "signup", "phone", "email_key"]
print("repeats after the first copy:", step1.duplicated(subset=cols).sum())
print("rows in a duplicate group   :", step1.duplicated(subset=cols, keep=False).sum())
print("expected: 20 repeats -> 40 rows in groups of two")
```
```text
repeats after the first copy: 20
rows in a duplicate group   : 40
expected: 20 repeats -> 40 rows in groups of two
```

Use `keep=False` when you want to **look at** the duplicate groups (every copy), and the default when you want to **remove** the repeats. Here the groups are of size two, so 20 repeats involve 40 rows.

```python run
dups = step1[step1.duplicated(subset=cols, keep=False)].sort_values("resp_id")
print(dups.head(4)[["resp_id", "city", "income", "satisfaction", "signup"]].to_string())
```
```text
     resp_id   city    income  satisfaction     signup
0       1001   Pune 49,900.00             1 2024-10-30
612     1001   Pune 49,900.00             1 2024-10-30
605     1024  Delhi 48,600.00             9 2024-07-19
23      1024  Delhi 48,600.00             9 2024-07-19
```

Always look at some duplicate groups before removing them. If the two copies differ in a column you left out of `subset`, they are not exact copies, and the question "which one do I keep?" appears (section 5.4).

```python run
step2 = step1.drop_duplicates(subset=cols, keep="first")
_ = log_step("drop exact duplicates", step1, step2, "whole row repeated")
print(show_log().to_string(index=False))
```
```text
                 step  rows_before  rows_after  na_before  na_after                                     note
        load raw file          635         635         14        14              no change; start of the log
        clean formats          635         635         14       192 text -> numbers, dates; codes -> missing
drop exact duplicates          635         615        192       190                       whole row repeated
```

The log already tells a story. The step "clean formats" removed no rows, but the number of missing cells jumped from 14 to 192. Nothing was lost: the 178 new missing cells are the `N/A`, `-999`, empty text, `999` and invalid phones that *were* missing all along, hidden behind fake values. Cleaning made the real missingness visible, and that is exactly what we want.

### 5.3 Duplicates by key

Often the real question is not "is the whole row repeated" but "does the same *thing* appear twice": the same customer, the same order, the same email. Then `subset` is the key columns only.

```python run
print("resp_id unique now?       ", step2["resp_id"].is_unique)
print("duplicated email keys      ", step2.duplicated(subset=["email_key"]).sum())
```
```text
resp_id unique now?        True
duplicated email keys       15
```

The IDs are unique, but 15 email keys repeat. These are the re-submissions: the same person filled the form again and got a new `resp_id`. A uniqueness check on the ID would have passed and **missed them**. The lesson: *choose the key from the meaning of the data, not from the column that happens to be called id.*

There is a trap in `duplicated` with missing values: **`NaN` equals `NaN` for `duplicated`**. Two rows that both have a missing value in the key column are called duplicates of each other.

```python run
t = pd.DataFrame({"email": ["a@x.com", None, None, "b@x.com"], "n": [1, 2, 3, 4]})
print(t.duplicated(subset=["email"]).tolist())
```
```text
[False, False, True, False]
```

Rows 1 and 2 are two different unknown people, but `duplicated` flags row 2 as a repeat. That is why we built `email_key` from the raw text (even a broken email like `meera1042mail.example` is still a good key). If your key column can be missing, either filter first (`t[t["email"].notna()].duplicated(...)`) or choose a different key.

> **Predict the output.** How many rows will be left after dropping duplicates by `email_key`? How does it compare with the 600 respondents of the truth?

<details><summary>Answer</summary>

```python run
step3 = step2.drop_duplicates(subset=["email_key"], keep="last")
print(len(step2), "->", len(step3))
print("equals the truth count:", len(step3) == len(truth))
```
```text
615 -> 600
equals the truth count: True
```

615 rows become 600, matching the truth exactly. Be careful when you cannot check against a truth: dropping by a single key can remove two *different* people who share an email address (a family sharing one email, say). Look at the groups first, and decide with the people who own the data.

</details>

### 5.4 Which copy survives?

`drop_duplicates(keep="first")` keeps the first copy in the *current row order*. That is arbitrary unless you sorted first. A responsible rule says which row is the better one and sorts accordingly. For the survey: the newest submission wins, and the newer submission has the higher `resp_id`.

```python run
twice = step2[step2.duplicated(subset=["email_key"], keep=False)].sort_values(["email_key", "resp_id"])
print(twice.head(4)[["resp_id", "email_key", "satisfaction"]].to_string())
```
```text
     resp_id              email_key  satisfaction
449     1450  arjun1450mail.example             3
620     2001  arjun1450mail.example             7
131     1132  asha1132@mail.example             3
622     2003  asha1132@mail.example             3
```

Each pair has the old answer and the new answer. We keep the new one: sort by `resp_id`, then keep the last of each key.

```python run
step3 = (step2.sort_values("resp_id")
              .drop_duplicates(subset=["email_key"], keep="last")
              .sort_index())
_ = log_step("drop re-submissions", step2, step3, "same email key; newest resp_id wins")
print(len(step3), "rows;", step3["email_key"].is_unique, "unique keys")
```
```text
600 rows; True unique keys
```

`sort_index()` at the end puts the table back in its original row order, so the cleaning does not shuffle the data as a side effect.

A different survival rule is **most complete row wins**: keep the copy with the fewest missing cells. Another is **merge the copies**: for each column, take the first non-missing value. The groupby `first()` method does exactly that, because `first` skips missing values.

```python run
pair = pd.DataFrame({"id": [7, 7], "phone": [None, "9876543210"], "city": ["Pune", None]})
print(pair.groupby("id").first().to_string())
```
```text
         phone  city
id                  
7   9876543210  Pune
```

Both columns of the merged row are filled, although neither original row was complete. Merging is powerful and also risky: it can produce a row that never existed. Use it only when the copies describe the same fact at different times of knowing it.

### 5.5 Near duplicates and fuzzy matching

Sometimes no clean key exists: `John Smith` and `Jon  Smith` are probably one person. Python's standard library has `difflib`, which scores how similar two strings are between 0 and 1. It is slow (it compares pairs) but it needs nothing else.

```python run
from difflib import SequenceMatcher


def sim(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


names = ["John Smith", "Jon  Smith", "Joan Smythe", "Priya Nair", "Priya Nayar"]
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        score = sim(names[i], names[j])
        if score > 0.8:
            print(f"{names[i]!r:15} ~ {names[j]!r:15} score {score:.2f}")
```
```text
'John Smith'    ~ 'Jon  Smith'    score 0.90
'Priya Nair'    ~ 'Priya Nayar'   score 0.86
```

Two rules for fuzzy matching. First, **use it to suggest, not to decide**: send the pairs above a threshold to a person. Second, **block first**: compare only rows that already agree on something cheap (same city, same birth year), because comparing all pairs of a million rows is out of reach. Threshold choices are judgement: set the threshold too low and you merge two different people; too high and you keep the duplicate.

## 6. Outliers

### 6.1 What is an outlier?

An outlier is a value far from the rest. That sentence hides the important question: *far because it is wrong, or far because it is real?*

| Kind | Example | What to do |
|---|---|---|
| Entry error | income typed with two extra zeros | fix if you can prove the fix, else set to missing |
| Impossible value | age 150 | set to missing (section 3.3) |
| Real but extreme | a customer who really earns 20 times the median | **keep**; use methods that are not hurt by it |
| Different population | company accounts in a table of persons | split into its own group |

No statistic can tell these four apart. A rule can only **point at suspects**; a human with domain knowledge decides. So the first habit is: flag, look, then act.

### 6.2 See the shape first

Income is right-skewed: many small values, a few large ones. Before using any rule, look at the shape. A text histogram on a **log scale** needs no plotting library.

```python run
def text_hist(x, bins=12, log=False, width=40):
    x = x.dropna()
    x = np.log10(x) if log else x
    counts, edges = np.histogram(x, bins=bins)
    for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
        lo_, hi_ = (10 ** lo, 10 ** hi) if log else (lo, hi)
        print(f"{lo_:>11,.0f} - {hi_:>11,.0f} | {'#' * int(width * c / counts.max())} {c}")


text_hist(step3["income"], bins=10, log=True)
```
```text
      7,800 -      15,114 | ## 16
     15,114 -      29,286 | ################## 117
     29,286 -      56,747 | ######################################## 255
     56,747 -     109,958 | ################# 113
    109,958 -     213,063 | # 8
    213,063 -     412,849 |  0
    412,849 -     799,971 |  0
    799,971 -   1,550,091 |  0
  1,550,091 -   3,003,587 |  1
  3,003,587 -   5,820,000 |  6
```

The bulk of the data sits between roughly 20,000 and 100,000 rupees, and a thin tail reaches the millions. The log scale makes the tail visible. Now the three standard rules.

### 6.3 Three rules for suspects

**Rule 1: IQR fences.** Let Q1 and Q3 be the 25th and 75th percentiles and IQR = Q3 − Q1. Values below `Q1 − 1.5·IQR` or above `Q3 + 1.5·IQR` are suspects. It does not depend on the mean, so a few extreme values do not move the fences.

**Rule 2: z-score.** `z = (x − mean) / std`; suspects have |z| above 3. This is simple and famous. It has a weakness: the outliers themselves inflate the mean and the std, so they hide from the rule. This is called **masking**.

**Rule 3: robust z-score.** Replace the mean by the median and the std by the **MAD** (median absolute deviation). `robust_z = 0.6745 · (x − median) / MAD`. The 0.6745 makes it comparable to a normal z-score. Both the median and the MAD ignore extreme values.

```python run
def flag_iqr(x, k=1.5):
    q1, q3 = x.quantile([.25, .75])
    return (x < q1 - k * (q3 - q1)) | (x > q3 + k * (q3 - q1))


def flag_z(x, t=3):
    return ((x - x.mean()) / x.std()).abs() > t


def flag_mad(x, t=3.5):
    med = x.median()
    mad = (x - med).abs().median()
    return (0.6745 * (x - med) / mad).abs() > t


inc = step3["income"]
# the truth, found by email (re-submissions have new ids, but the same email)
truth_by_key = truth.set_index(truth["email"].str.replace("@", "", regex=False))["income"]
true_income = step3["email_key"].str.replace("@", "", regex=False).map(truth_by_key)
planted = inc.notna() & (inc != true_income)
print("income values typed with extra zeros (we know, from the truth):", planted.sum())
for name, f in [("IQR on income", flag_iqr(inc)),
                ("z-score on income", flag_z(inc)),
                ("robust z on income", flag_mad(inc)),
                ("IQR on log10(income)", flag_iqr(np.log10(inc))),
                ("robust z on log10", flag_mad(np.log10(inc)))]:
    hit = (f & planted).sum()
    print(f"{name:22} flags {int(f.sum()):3d} | planted found {hit} | false alarms {int(f.sum()) - hit}")
```
```text
income values typed with extra zeros (we know, from the truth): 7
IQR on income          flags  22 | planted found 7 | false alarms 15
z-score on income      flags   7 | planted found 7 | false alarms 0
robust z on income     flags  15 | planted found 7 | false alarms 8
IQR on log10(income)   flags  15 | planted found 7 | false alarms 8
robust z on log10      flags   7 | planted found 7 | false alarms 0
```

Of the 8 values typed with extra zeros, one fell into the `N/A` or `-999` codes, so 7 reach this table. Read the results carefully, because they teach three things.

- **The errors here are huge** (100 times too big), so even the plain z-score finds all 7. Do not conclude that z-score is good. Its weakness is **masking**: when several outliers are present they inflate the mean and the standard deviation, and each one hides the others. A tiny example shows it:

```python run
toy = pd.Series([10, 11, 9, 10, 12, 11, 10, 500, 600, 550])
print("z-score flags  :", int(flag_z(toy).sum()), "values")
print("robust z flags :", int(flag_mad(toy).sum()), "values")
print("toy mean / std :", round(toy.mean(), 1), "/", round(toy.std(), 1))
```
```text
z-score flags  : 0 values
robust z flags : 3 values
toy mean / std : 172.3 / 261.7
```

Three clear outliers, and the z-score finds **none**: the mean (172) and std (262) were pulled up by the outliers themselves, so 600 is only 1.7 standard deviations away. The median and MAD do not care.

- **IQR and robust z on the raw scale raise many false alarms** (15 and 8). Income is skewed, so honest high earners fall above the fences. A rule that assumes a symmetric shape is the wrong rule for a skewed variable.
- **Robust z on the log scale finds all 7 with no false alarm.** A multiplication by 100 is an addition of 2 on the log scale, a huge jump. The IQR rule on the log scale still raises 8 false alarms, because its fences are tight (1.5 IQR) and the *low* tail of honest incomes crosses them. No rule is best everywhere: **compare rules on data where you know the answer, then pick one and write down why.**

> **Predict the output.** If you apply the IQR rule to income *inside each city* instead of to the whole table, would you expect more or fewer false alarms? When is that the right thing to do?

<details><summary>Answer</summary>

```python run
by_city = step3.groupby("city", observed=True)["income"].transform(lambda s: flag_iqr(np.log10(s)))
print("flags per city rule:", int(by_city.sum()), " planted found:", int((by_city.astype(bool) & planted).sum()))
```
```text
flags per city rule: 16  planted found: 7
```

The result is almost the same as for the whole table (16 flags instead of 15), because the synthetic cities have the same income distribution by construction. In real data, incomes differ by city (and by job, age, year), and then a value that is normal for Mumbai looks extreme in a small town. Check **within the group that defines "normal"**. The price is that small groups give unstable fences; with fewer than about 30 rows per group, a domain rule (a fixed allowed range) is safer.

</details>

### 6.4 Domain rules beat statistics

A rule written from knowledge needs no distribution: "monthly income above 1,000,000 rupees is not credible for this survey", "age must be 18 to 75", "satisfaction must be 1 to 10". It is easy to explain, easy to audit, and it is what pandera will check in section 11.

```python run
domain_bad = step3["income"] > 1_000_000
print("above 1,000,000:", int(domain_bad.sum()), "| planted errors caught:", int((domain_bad & planted).sum()))
print("planted errors that still slip under the line:", int((planted & ~domain_bad).sum()))
```
```text
above 1,000,000: 7 | planted errors caught: 7
planted errors that still slip under the line: 0
```

The fixed line caught all 7 here. It is simple but not perfect: an error of 100 times a low income of 8,000 is 800,000 and would stay under the line, while an honest millionaire above it would be flagged wrongly. Use the statistical rule to *discover* the right line, then write the domain rule down.

### 6.5 What do you do with a suspect?

Four choices, from the gentlest.

1. **Flag** it with a new Boolean column. Nothing is lost.
2. **Fix** it, only if the cause is proven. Here an error of exactly 100 times is a known data entry habit, so dividing by 100 is defensible, but write down the rule.
3. **Set to missing** if you cannot fix it. Then it is a missing-data question (sections 7 to 9).
4. **Winsorise**: clip to a boundary, for example the 1st and 99th percentile. It keeps the row, and tames its influence on the mean.

Always compare the effect on your statistic.

```python run
inc = step3["income"]
flag = flag_mad(np.log10(inc)) & inc.notna()      # the rule that found all 7 with no false alarm
fixed = inc.where(~flag, inc / 100)                 # option 2: divide the flagged values by 100
as_missing = inc.mask(flag)                          # option 3
lo, hi = inc.quantile([.01, .99])
winsor = inc.clip(lo, hi)                            # option 4
ok_rows = inc.notna()
res = pd.DataFrame({
    "mean": [inc.mean(), fixed.mean(), as_missing.mean(), winsor.mean(), true_income[ok_rows].mean()],
    "median": [inc.median(), fixed.median(), as_missing.median(), winsor.median(), true_income[ok_rows].median()],
}, index=["as parsed", "fixed (/100)", "set to missing", "winsorised 1-99", "truth (same rows)"])
print(res.round(0).to_string())
```
```text
                        mean    median
as parsed         104,397.00 39,900.00
fixed (/100)       44,671.00 39,700.00
set to missing     44,673.00 39,400.00
winsorised 1-99    88,090.00 39,900.00
truth (same rows)  44,671.00 39,700.00
```

The **median** barely moves in any option; it is already robust. The **mean** is the statistic at risk: as parsed it is wrong by about 60,000, more than double the truth. Fix and missing land close to the truth. Winsorising helps but does not fully repair the mean, because the clipped value is still far above the truth. If you only need a "typical" income, report the median and the outliers become a smaller problem. If you need a total (for budgeting), every one of those 7 values matters, and you must resolve them one by one.

> **Try it.** Winsorise at the 5th and 95th percentile instead. The mean looks excellent. Does that mean it is the better method? Count how many **honest** values (not planted errors) each version changed.

<details><summary>Answer</summary>

```python run
lo5, hi5 = inc.quantile([.05, .95])
w5 = inc.clip(lo5, hi5)
print("mean, winsor 1-99 :", round(winsor.mean()))
print("mean, winsor 5-95 :", round(w5.mean()))
print("mean, truth       :", round(true_income[ok_rows].mean()))
honest = inc.notna() & ~planted
print("honest values changed, 1-99 :", int((honest & (winsor != inc)).sum()))
print("honest values changed, 5-95 :", int((honest & (w5 != inc)).sum()))
print("honest values changed, fix  :", int((honest & (fixed != inc)).sum()))
```
```text
mean, winsor 1-99 : 88090
mean, winsor 5-95 : 44879
mean, truth       : 44671
honest values changed, 1-99 : 6
honest values changed, 5-95 : 44
honest values changed, fix  : 0
```

The 5-95 clip gives a mean near the truth, but look at the price: it rewrote dozens of honest incomes, and the match is partly luck (the honest values it cut from the top and bottom happen to cancel). Fixing a proven error changes **only** the wrong values. The wider you clip, the more real information you replace by a boundary; and your standard deviation and your tails are now wrong, even though the mean looks right. A good-looking mean is not proof of a good method.

</details>

## 7. Missing values: the mechanics

Now the heart of the chapter. We start with the mechanics (this section), then the reasoning (sections 8 and 9). Mechanics first, because many "reasoning" bugs are really mechanics bugs.

### 7.1 Four kinds of "missing" in pandas

| Value | Where it lives | Notes |
|---|---|---|
| `np.nan` | float columns, and the `str` dtype | a float "not a number"; `NaN != NaN` |
| `None` | `object` columns | converted to `NaN` or `NA` in most pandas operations |
| `pd.NaT` | datetime / timedelta columns | "not a time" |
| `pd.NA` | nullable dtypes: `Int64`, `boolean`, `string` | a single missing marker for every type |

Why do nullable types exist? An integer column in NumPy cannot hold `NaN`, so one missing age turns the whole column to float (`25.0`, `64.0`). `Int64` keeps whole numbers and still allows a missing value.

```python run
a = pd.Series([25, 64, None])
b = pd.Series([25, 64, None], dtype="Int64")
print(a.dtype, a.tolist())
print(b.dtype, b.tolist())
print("sum  :", a.sum(), "|", b.sum())
print("mean :", a.mean(), "|", b.mean())
```
```text
float64 [25.0, 64.0, nan]
Int64 [25, 64, <NA>]
sum  : 89.0 | 89
mean : 44.5 | 44.5
```

### 7.2 Missing values do not equal anything

The famous rule of `NaN`: it is not equal to anything, **not even itself**. `pd.NA` is stricter: any comparison with `pd.NA` is `pd.NA` ("unknown"), and asking Python to turn "unknown" into True or False raises an error.

```python run
x = np.nan
print("nan == nan :", x == x)
print("nan != nan :", x != x)
s = pd.Series([1, None, 3], dtype="Int64")
print((s > 1).tolist())
try:
    bool(pd.NA)
except TypeError as e:
    print("TypeError:", e)
print("isna works :", s.isna().tolist())
```
```text
nan == nan : False
nan != nan : True
[False, <NA>, True]
TypeError: boolean value of NA is ambiguous
isna works : [False, True, False]
```

So **never** write `df["age"] == np.nan` to find missing values. It returns `False` for every row. Use `isna()` and `notna()`. Inside an `if` or a Boolean mask, a column with `pd.NA` needs `fillna(False)` or `(s > 1).fillna(False)`, or an explicit decision about what "unknown" should do.

### 7.3 Aggregations skip missing values

`sum`, `mean`, `min`, `max`, `std` skip missing values by default (`skipna=True`). This is convenient and dangerous: the mean of the people who answered is silently called "the mean".

```python run
age_s = step3["age"]
print("rows        :", len(age_s))
print("count       :", age_s.count(), "(non-missing)")
print("missing     :", age_s.isna().sum())
print("mean (skip) :", round(age_s.mean(), 2))
print("sum / rows  :", round(age_s.sum() / len(age_s), 2), "<- divides by all rows, so it is wrong as a mean")
print("mean, skipna=False:", age_s.astype("float64").mean(skipna=False))
```
```text
rows        : 600
count       : 572 (non-missing)
missing     : 28
mean (skip) : 46.19
sum / rows  : 44.04 <- divides by all rows, so it is wrong as a mean
mean, skipna=False: nan
```

`count` counts non-missing values; `size` and `len` count all rows. When you report an average, report also **how many values it is based on**. An average of 549 values and one of 600 are different things, even if the number is the same.

Two more places where missing values disappear without a message:

- `groupby` drops rows whose **key** is missing (unless `dropna=False`), as you learned in da.04.
- `merge` matches `NaN` keys with each other (also from da.04). 

### 7.4 Measuring missingness

Before any decision, measure it: how much, in which columns, and in which rows.

```python run
miss = step3.isna()
print((miss.mean() * 100).round(1).to_string())
print()
per_row = miss.sum(axis=1)
print("missing cells per row ->", per_row.value_counts().sort_index().to_dict())
```
```text
resp_id         0.00
age             4.70
city            0.00
income         14.00
satisfaction    0.00
signup          0.00
phone           8.50
email           4.00
email_key       0.00

missing cells per row -> {0: 429, 1: 157, 2: 12, 3: 2}
```

The second view matters: if most rows have zero or one missing cells, dropping rows loses little; if missing cells are spread so that most rows have *at least one*, then `dropna()` would delete nearly everything. Check before you drop.

```python run
print("rows with at least one missing cell:", int(miss.any(axis=1).sum()), "of", len(step3))
print("rows left after dropna()          :", len(step3.dropna()))
print("rows left after dropna(subset=['income']):", len(step3.dropna(subset=['income'])))
```
```text
rows with at least one missing cell: 171 of 600
rows left after dropna()          : 429
rows left after dropna(subset=['income']): 516
```

### 7.5 The `dropna` and `fillna` toolbox

| Tool | What it does |
|---|---|
| `dropna()` | drops rows with any missing cell |
| `dropna(subset=[...])` | only looks at the listed columns |
| `dropna(thresh=k)` | keeps rows with at least `k` non-missing cells |
| `dropna(how="all")` | drops rows that are missing everywhere |
| `fillna(value)` | one constant, or a dict by column |
| `fillna(s.median())` | a statistic |
| `ffill()` / `bfill()` | carry the previous / next value |
| `interpolate()` | draw a line between neighbours (numeric or time index) |
| `groupby(...)[c].transform("median")` | a group statistic, aligned to the rows |

None of these is "correct" in general. Each one is a **claim about the world**. Dropping claims "the missing rows are like the rest". Filling with a constant claims "the unknown is probably this". Forward fill claims "nothing changed since the last reading". Section 9 tests those claims.

Forward fill and interpolation need an order, so they suit time series (a sensor reading, a daily price) and not a survey. A small example:

```python run
temp = pd.Series([20.0, np.nan, np.nan, 26.0, np.nan, 25.0],
                 index=pd.date_range("2025-06-01", periods=6, freq="D"), name="temp_c")
print(pd.DataFrame({"raw": temp, "ffill": temp.ffill(), "bfill": temp.bfill(),
                    "interpolate": temp.interpolate()}).to_string())
```
```text
             raw  ffill  bfill  interpolate
2025-06-01 20.00  20.00  20.00        20.00
2025-06-02   NaN  20.00  26.00        22.00
2025-06-03   NaN  20.00  26.00        24.00
2025-06-04 26.00  26.00  26.00        26.00
2025-06-05   NaN  26.00  25.00        25.50
2025-06-06 25.00  25.00  25.00        25.00
```

Forward fill repeats `20` for two days; interpolation draws a straight line, 22 then 24. Neither is "the truth", and the right one depends on the process. A temperature drifts smoothly, so interpolation is plausible. A shop's closing status (open/closed) jumps, so forward fill is plausible and interpolation makes no sense.

> **Try it.** `ffill` has a `limit` argument. Use it so that a gap longer than one day stays missing. Why is that often the safest default for sensor data?

<details><summary>Answer</summary>

```python run
print(temp.ffill(limit=1).to_string())
```
```text
2025-06-01   20.00
2025-06-02   20.00
2025-06-03     NaN
2025-06-04   26.00
2025-06-05   26.00
2025-06-06   25.00
Freq: D
```

With `limit=1`, only the first missing day after a reading is filled. The second day stays missing. A sensor that has been silent for two days has told us something: it may be broken, and a long run of repeated values would hide that. Limits keep your fills small and your gaps visible.

</details>


## 8. Why values are missing

### 8.1 Three mechanisms

Statisticians (after Donald Rubin) sort missing data into three kinds. The names are unfortunate, but you need them, because they decide whether dropping is harmless, fixable or dangerous. The question is always the same: **what does the chance of being missing depend on?**

| Name | The chance that income is missing depends on... | Example | Dropping the rows |
|---|---|---|---|
| **MCAR**: missing completely at random | nothing; it is a coin flip | a form page was lost in the post | fewer rows, but **no bias** |
| **MAR**: missing at random | other columns you *can see* | people with little schooling skip the income question more often | **biased**, but you can repair it using the other columns |
| **MNAR**: missing not at random | the missing value itself | high earners hide their income | **biased**, and the data alone cannot show you how much |

Note the word "random" in MAR is misleading. MAR is *not* random: missingness has a pattern, but the pattern is explained by columns you have. MNAR is the hard case, because the explanation sits in exactly the value you do not have.

### 8.2 A population where we know everything

To see the three mechanisms work, we need a dataset whose **full truth** we hold. We build 6,000 people with education, age and income. Income grows with education and age. Then we delete about 23 percent of the incomes in three different ways.

```python run
def make_population(n=6000, seed=5):
    rng = np.random.default_rng(seed)
    edu = rng.choice([8, 10, 12, 14, 16, 18], n, p=[.1, .15, .3, .2, .15, .1])
    age = rng.integers(22, 66, n)
    inc = np.exp(8.6 + 0.12 * edu + 0.008 * (age - 22) + rng.normal(0, 0.35, n)).round(-2)
    return pd.DataFrame({"edu_years": edu, "age": age, "income": inc})


pop = make_population()
rng = np.random.default_rng(99)
n = len(pop)

p_mar = np.where(pop["edu_years"] <= 10, .45, np.where(pop["edu_years"] <= 12, .25, .10))
p_mnar = np.where(pop["income"] > pop["income"].quantile(.7), .58, .08)

hide = {
    "MCAR": rng.random(n) < .23,          # a coin flip for everybody
    "MAR": rng.random(n) < p_mar,         # depends on education (a visible column)
    "MNAR": rng.random(n) < p_mnar,       # depends on income itself (the hidden value)
}
variants = {}
for name, m in hide.items():
    d = pop.copy()
    d.loc[m, "income"] = np.nan
    variants[name] = d
    print(f"{name}: {m.mean() * 100:.1f}% of incomes deleted")
```
```text
MCAR: 23.0% of incomes deleted
MAR: 23.4% of incomes deleted
MNAR: 23.0% of incomes deleted
```

All three versions lose about the same share, 23 percent. If missing data were only a question of *how much*, they would behave alike. They do not. The truth, and what each version's observed values say:

```python run
def summary(d, col="income"):
    return {"mean": d[col].mean(), "median": d[col].median(), "std": d[col].std(),
            "corr_with_edu": d["edu_years"].corr(d[col]), "pct_over_50k": (d[col] > 50_000).mean() * 100}


rows = {"TRUTH (all 6,000)": summary(pop)}
for name, d in variants.items():
    rows[f"{name}, observed only"] = summary(d.dropna(subset=["income"]))
print(pd.DataFrame(rows).T.to_string())
```
```text
                         mean    median       std  corr_with_edu  pct_over_50k
TRUTH (all 6,000)   34,340.65 29,900.00 18,729.15           0.64         16.33
MCAR, observed only 34,355.78 30,000.00 18,787.48           0.65         16.45
MAR, observed only  36,270.62 31,700.00 19,169.82           0.63         18.87
MNAR, observed only 30,069.53 26,900.00 15,554.64           0.61          9.01
```

Read the `mean` column.

- **MCAR**: the observed mean is 34,356 against a truth of 34,341. Almost perfect. Deleting rows at random shrinks the sample but does not tilt it.
- **MAR**: 36,271. Too high, because low-education people (who earn less) went missing more often, so the survivors are richer than the population.
- **MNAR**: 30,070. Too low, because high earners hid their income.

Notice that MAR and MNAR are biased in **opposite directions**. There is no general rule such as "missing data makes the average go down". The direction depends on *who* is missing.

### 8.3 What the people who stayed look like

Deleting rows changes *who is in the table*. You can see it in the other columns, even without the income.

```python run
order = [8, 10, 12, 14, 16, 18]
share = pd.DataFrame({
    "truth": pop["edu_years"].value_counts(normalize=True).reindex(order) * 100,
    "MCAR kept": variants["MCAR"].dropna(subset=["income"])["edu_years"].value_counts(normalize=True).reindex(order) * 100,
    "MAR kept": variants["MAR"].dropna(subset=["income"])["edu_years"].value_counts(normalize=True).reindex(order) * 100,
})
share.index.name = "edu_years"
print(share.round(1).to_string())
```
```text
           truth  MCAR kept  MAR kept
edu_years                            
8          10.70      10.40      7.70
10         15.00      14.90     10.70
12         30.70      30.90     30.00
14         19.00      18.90     22.40
16         14.50      14.70     17.20
18         10.10      10.30     11.90
```

Under MCAR the education mix is unchanged (10, 15, 30 ... percent). Under MAR the groups with little education shrink and the university groups grow. The table has become *more educated*, and since education drives income, the average rises. This is the mechanism of MAR, visible in numbers.

### 8.4 Diagnosing: does missingness depend on what I can see?

You can test for MAR (or at least its signs) in the data you have. For each other column, compare the **missing rate** across its values. A flat profile suggests MCAR; a clear slope shows MAR.

```python run
def missing_profile(d, by, col="income"):
    return (d[col].isna().groupby(d[by]).mean() * 100).round(1)


print("MCAR: % income missing, by education")
print(missing_profile(variants["MCAR"], "edu_years").to_string())
print("\nMAR: % income missing, by education")
print(missing_profile(variants["MAR"], "edu_years").to_string())
```
```text
MCAR: % income missing, by education
edu_years
8    25.50
10   23.60
12   22.40
14   23.40
16   22.10
18   21.60

MAR: % income missing, by education
edu_years
8    44.60
10   45.50
12   25.10
14    9.60
16    9.20
18    9.60
```

MCAR: about 23 percent everywhere, with a little random wobble. MAR: 45 percent for the two lowest groups, then falling to about 10 percent at the top. That slope is the evidence of MAR.

For a numeric column, compare the mean of the other column between "income missing" and "income present":

```python run
for name, d in variants.items():
    m = d["income"].isna()
    print(f"{name:5} mean education, income missing: {d.loc[m, 'edu_years'].mean():5.2f} | present: {d.loc[~m, 'edu_years'].mean():5.2f}")
```
```text
MCAR  mean education, income missing: 12.73 | present: 12.87
MAR   mean education, income missing: 11.23 | present: 13.33
MNAR  mean education, income missing: 14.28 | present: 12.41
```

A big gap flags that missingness is linked to education. Look at the MNAR row, though: the gap is just as large, but **in the opposite direction** (the people with a missing income are *more* educated: 14.3 years against 12.4). Nobody in the MNAR variant looked at education. They hid because their income was high, and high income goes with high education, so education carries a shadow of the hidden value.

> **The limit of diagnosis.** From the visible columns, MAR and MNAR can look alike: both show that missingness is linked to education. The difference is what *causes* it, schooling or income, and the cause of the hidden value is not in the data. The test of section 9 proves it: filling by education repaired the MAR variant and failed in the MNAR variant, although the two diagnostics looked similar. So deciding between MAR and MNAR is **reasoning about how the data was collected**, not a statistical test. Ask the people who ran the survey: "Who tends to skip this question? Why?"

> **Predict the output.** In the MNAR variant, would you expect the average *age* of people with a missing income to differ from the age of people with a present income? Think about what drives income, before you run it.

<details><summary>Answer</summary>

```python run
d = variants["MNAR"]
m = d["income"].isna()
print("mean age, income missing:", round(d.loc[m, "age"].mean(), 2))
print("mean age, income present:", round(d.loc[~m, "age"].mean(), 2))
```
```text
mean age, income missing: 45.53
mean age, income present: 43.03
```

Yes, about 2.5 years older. Age raises income a little, so high earners are slightly older, and high earners are the ones who hide. The visible columns that relate to income all carry a faint signal about the hidden one. That is why imputing from them helps a little under MNAR (section 9.3) but never enough.

</details>

### 8.5 More reasons a value is missing

The three mechanisms describe the *statistics*. In practice you also ask the plain-language question, **what is the reason?** The reason often tells you the right handling immediately.

| Reason | Example | What `NaN` really means | Handling |
|---|---|---|---|
| Not applicable (structural) | `spouse_income` for unmarried people | "there is no such thing" | do **not** fill; keep missing, or add a category "not applicable" |
| Zero in disguise | `units_sold` empty on days the shop was closed | "zero" | fill with `0`, after checking that it really is zero |
| Not collected | a question added to the form in June | "unknown, by design" | analyse the later period separately |
| Refused / skipped | income question | "unknown, person-dependent" | the MAR / MNAR reasoning |
| Lost or broken | sensor outage, bad file | "unknown, by accident" | likely MCAR; interpolate only short gaps |
| Entry code | `N/A`, `999`, `-1` | "a code, not a value" | convert to real missing first (section 3) |
| Not yet happened | `end_date` of an ongoing contract | "will exist later" | do **not** fill; this is not missing data, it is *censoring* |

A mistake that looks harmless: filling all missing `units_sold` with the column mean. If the missing days are shop-closed days, you just invented sales for days with no shop.

A cheap but valuable habit is the **missing indicator**: add a column that records *that* the value was missing, before you fill it.

```python run
d = variants["MAR"].copy()
d["income_was_missing"] = d["income"].isna()
d["income_filled"] = d["income"].fillna(d.groupby("edu_years")["income"].transform("median"))
print(d.groupby("income_was_missing")[["edu_years", "age", "income_filled"]].mean().round(1).to_string())
print(d.head(3).to_string())
```
```text
                    edu_years   age  income_filled
income_was_missing                                
False                   13.30 43.60      36,270.60
True                    11.20 43.80      26,513.30
   edu_years  age    income  income_was_missing  income_filled
0         16   25 41,300.00               False      41,300.00
1         16   47 65,300.00               False      65,300.00
2         12   48       NaN                True      27,400.00
```

With the indicator, you (and a model) can still ask "do the people who skipped differ from the others?" Without it, the filled value looks exactly like a real one, and the information that it is an estimate is gone.

## 9. When dropping or filling changes the answer

### 9.1 The strategies

Now we put several reasonable strategies side by side. Each is something a careful analyst might do and defend. For each, the function returns the same five summaries, always computed on **all rows** after the fill (or on the surviving rows, for dropping).

| Strategy | What it does | The claim behind it |
|---|---|---|
| drop rows | analyse only complete rows | the missing rows are like the rest |
| fill mean / fill median | one constant for every gap | the unknown is average |
| fill group mean | the mean of the same education group | unknown people are like their group |
| random draw in group | a random observed income from the same group | the same, and it keeps the spread |
| regression fill | prediction from education and age | income follows a line in those columns |

```python run
def apply_strategies(d, seed=0):
    r = np.random.default_rng(seed)
    out = {}
    obs = d.dropna(subset=["income"])
    out["drop rows"] = summary(obs)

    f = d.assign(income=d["income"].fillna(d["income"].mean()))
    out["fill mean"] = summary(f)
    f = d.assign(income=d["income"].fillna(d["income"].median()))
    out["fill median"] = summary(f)
    f = d.assign(income=d["income"].fillna(d.groupby("edu_years")["income"].transform("mean")))
    out["fill group mean (edu)"] = summary(f)

    def draw(g):                                   # fill the gaps of one group with random observed values
        o = g.dropna().to_numpy()
        g = g.copy()
        g[g.isna()] = r.choice(o, g.isna().sum())
        return g
    f = d.assign(income=d.groupby("edu_years")["income"].transform(draw))
    out["random draw in group"] = summary(f)

    X = np.column_stack([np.ones(len(obs)), obs["edu_years"], obs["age"]])
    beta, *_ = np.linalg.lstsq(X, np.log(obs["income"]), rcond=None)       # log income ~ edu + age
    m = d["income"].isna()
    Xm = np.column_stack([np.ones(m.sum()), d.loc[m, "edu_years"], d.loc[m, "age"]])
    f = d.copy()
    f.loc[m, "income"] = np.exp(Xm @ beta)
    out["regression fill"] = summary(f)
    return pd.DataFrame(out).T


truth_row = pd.DataFrame({"TRUTH": summary(pop)}).T
print("MCAR: income deleted by a coin flip")
print(pd.concat([truth_row, apply_strategies(variants["MCAR"])]).to_string())
```
```text
MCAR: income deleted by a coin flip
                           mean    median       std  corr_with_edu  pct_over_50k
TRUTH                 34,340.65 29,900.00 18,729.15           0.64         16.33
drop rows             34,355.78 30,000.00 18,787.48           0.65         16.45
fill mean             34,355.78 34,355.78 16,485.54           0.57         12.67
fill median           33,353.95 30,000.00 16,587.15           0.57         12.67
fill group mean (edu) 34,232.33 29,200.00 17,519.03           0.69         14.85
random draw in group  34,193.88 29,800.00 18,785.05           0.64         16.27
regression fill       33,761.98 29,900.00 17,458.69           0.68         14.87
```

With MCAR, every strategy is close to the truth on the **mean**, and they differ in other ways. Look at the three columns that are *not* the mean:

- **`std`**: the true spread is 18,729. Dropping keeps it (18,787). Filling with the mean or median cuts it to about 16,500, because 23 percent of the rows now sit at one single value. The data look less varied than the people really are.
- **`corr_with_edu`**: the true relation between education and income is 0.64. Mean-filling drags it down to 0.57: a block of rows with the same income for every education level dilutes the link. A model trained on that table would underestimate the effect of schooling.
- **`pct_over_50k`**: truth 16.3 percent. Mean-filling gives 12.7, because *no one* filled in with the mean can be above 50,000. Any question about a **tail** is spoiled.

So even in the friendly case, "fill with the mean" gets the mean right and the other three answers wrong. That is the first lesson of the section: **a fill can protect the statistic you looked at and damage the ones you did not.**

### 9.2 When the mechanism is MAR

```python run
print("MAR: low-education people skip the income question more often")
print(pd.concat([truth_row, apply_strategies(variants["MAR"])]).to_string())
```
```text
MAR: low-education people skip the income question more often
                           mean    median       std  corr_with_edu  pct_over_50k
TRUTH                 34,340.65 29,900.00 18,729.15           0.64         16.33
drop rows             36,270.62 31,700.00 19,169.82           0.63         18.87
fill mean             36,270.62 36,270.62 16,775.45           0.53         14.45
fill median           35,200.33 31,700.00 16,886.76           0.56         14.45
fill group mean (edu) 34,389.68 29,138.72 17,764.46           0.67         15.42
random draw in group  34,430.73 30,000.00 18,639.55           0.64         16.52
regression fill       33,962.67 29,400.00 17,872.53           0.67         15.30
```

Now the strategies separate on the **mean**, which is the most reported number of all.

| Strategy | Mean | Error against truth (34,341) |
|---|---|---|
| drop rows | 36,271 | +1,930 |
| fill mean | 36,271 | +1,930 |
| fill median | 35,200 | +859 |
| fill group mean (edu) | 34,390 | +49 |
| random draw in group | 34,431 | +90 |
| regression fill | 33,963 | −378 |

Dropping and mean-filling give **the same wrong number**. Mean fill adds the biased mean back into the gaps, so it cannot move the mean; it keeps the bias and also shrinks the spread. The strategies that use **education** (the column that explains the missingness) repair the bias. This is the promise of MAR: *if you condition on the variables that drive missingness, the damage can be undone.*

This is also the place where two honest analysts disagree. One drops the incomplete rows ("I did not invent data"). One fills by education group ("I used what I know"). Their reports read:

- Analyst A: "The average income is **36,271**, and **18.9 percent** earn over 50,000."
- Analyst B: "The average income is **34,390**, and **15.4 percent** earn over 50,000."

Both followed a defensible textbook rule. The difference, 1,880 in the mean and 3.5 points in the share, is large enough to change a decision, such as a loan threshold or a price. And only because we kept the truth can we say B is right. **In real data nobody tells you, and the way to be safe is not to pick a favourite, but to show both and explain the gap** (see 9.6).

> **Predict the output.** In the MAR table, "fill group mean" is almost perfect for the mean (34,390). Which statistic in that row do you expect to be *worst*? Look at the `std` column before you answer.

<details><summary>Answer</summary>

```python run
t = apply_strategies(variants["MAR"])
cmp = pd.DataFrame({"truth": summary(pop), "group mean": t.loc["fill group mean (edu)"], "random draw": t.loc["random draw in group"]})
cmp["gap group mean %"] = ((cmp["group mean"] / cmp["truth"] - 1) * 100).round(1)
cmp["gap random draw %"] = ((cmp["random draw"] / cmp["truth"] - 1) * 100).round(1)
print(cmp.round(2).to_string())
```
```text
                  truth  group mean  random draw  gap group mean %  gap random draw %
mean          34,340.65   34,389.68    34,430.73              0.10               0.30
median        29,900.00   29,138.72    30,000.00             -2.50               0.30
std           18,729.15   17,764.46    18,639.55             -5.20              -0.50
corr_with_edu      0.64        0.67         0.64              4.60               0.30
pct_over_50k      16.33       15.42        16.52             -5.60               1.10
```

The weak points are the spread and the tail: the group-mean fill gives a `std` 5.2 percent too small and a `pct_over_50k` 5.6 percent too low, and the median is 2.5 percent off. The mean is within 0.1 percent. It fixed the average of each education group, but filled every gap inside a group with the *same* number, so the variety inside each group vanished. The random draw keeps the spread (every error is about 1 percent or less), because it fills with real, varied values. The price of the random draw is **randomness**: a different seed gives slightly different numbers (see 9.5).

</details>

### 9.3 When the mechanism is MNAR

```python run
print("MNAR: high earners hide their income")
print(pd.concat([truth_row, apply_strategies(variants["MNAR"])]).to_string())
```
```text
MNAR: high earners hide their income
                           mean    median       std  corr_with_edu  pct_over_50k
TRUTH                 34,340.65 29,900.00 18,729.15           0.64         16.33
drop rows             30,069.53 26,900.00 15,554.64           0.61          9.01
fill mean             30,069.53 30,069.53 13,645.84           0.51          6.93
fill median           29,339.48 26,900.00 13,710.95           0.48          6.93
fill group mean (edu) 31,731.51 28,300.00 15,147.76           0.69         11.82
random draw in group  31,690.73 28,200.00 16,838.10           0.62         11.20
regression fill       31,276.33 28,700.00 14,743.21           0.67          9.48
```

Now every strategy is wrong, and they are wrong in the same direction. The truth for the mean is 34,341. The best answer here is 31,732 (fill by group), and the worst is 29,339. The ones that use education help a little, but they do not recover what is missing, because **the missing values are exactly the high incomes, and nothing in the observed rows says how high**. The group means are built only from the incomes people were willing to give.

Also notice the share over 50,000: truth 16.3 percent, observed rows only 9.0 percent, best fill 11.8 percent. The tail is lost, and no filling method brings it back.

The honest response to MNAR is **not** to find a cleverer fill. It is to say what the data cannot tell, and to show how much the answer depends on an assumption. That is called a **sensitivity analysis**: choose a range of plausible assumptions, and report the range of answers.

For example: "Suppose the people who did not answer earn, on average, `k` times what the model predicts for their education and age." We vary `k`.

```python run
d = variants["MNAR"]
obs = d.dropna(subset=["income"])
X = np.column_stack([np.ones(len(obs)), obs["edu_years"], obs["age"]])
beta, *_ = np.linalg.lstsq(X, np.log(obs["income"]), rcond=None)
m = d["income"].isna()
pred_missing = np.exp(np.column_stack([np.ones(m.sum()), d.loc[m, "edu_years"], d.loc[m, "age"]]) @ beta)

print(" k   mean income   share over 50k")
for k in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
    filled = d["income"].copy()
    filled[m] = pred_missing * k
    print(f"{k:.1f}  {filled.mean():>11,.0f}   {(filled > 50_000).mean() * 100:>10.1f} %")
print("truth:", f"{pop['income'].mean():,.0f}", "|", f"{(pop['income'] > 50_000).mean() * 100:.1f} %")
```
```text
 k   mean income   share over 50k
1.0       31,276          9.5 %
1.1       32,090         11.4 %
1.2       32,903         13.9 %
1.3       33,716         15.3 %
1.4       34,529         17.6 %
1.5       35,343         19.3 %
truth: 34,341 | 16.3 %
```

The truth lies between the rows for `k = 1.3` and `k = 1.4`. A reader of the analysis who knows only the table would see a range: "the average is between 31,000 and 35,500, depending on whether the people who did not answer earn about the same as predicted or a good deal more". Compare that with the single number from a fill: a falsely precise answer. A range that honestly includes the truth is worth more than a point that excludes it.

### 9.4 Mean filling in one picture

The most common fill, and the most damaging for any model, is the mean. A text view of what it does to the distribution makes the point.

```python run
d = variants["MCAR"]
filled = d["income"].fillna(d["income"].mean())
print("Truth (all 6,000 incomes)")
text_hist(pop["income"], bins=8, width=30)
print("\nAfter filling 23% with the mean")
text_hist(filled, bins=8, width=30)
```
```text
Truth (all 6,000 incomes)
      4,900 -      26,500 | ############################# 2424
     26,500 -      48,100 | ############################## 2492
     48,100 -      69,700 | ######### 762
     69,700 -      91,300 | ## 229
     91,300 -     112,900 |  66
    112,900 -     134,500 |  18
    134,500 -     156,100 |  4
    156,100 -     177,700 |  5

After filling 23% with the mean
      4,900 -      26,500 | ################ 1860
     26,500 -      48,100 | ############################## 3300
     48,100 -      69,700 | ##### 592
     69,700 -      91,300 | # 179
     91,300 -     112,900 |  46
    112,900 -     134,500 |  16
    134,500 -     156,100 |  2
    156,100 -     177,700 |  5
```

The second histogram has a tower in the middle bins. A model or a "what share earn between 30,000 and 40,000?" question sees a dense crowd that does not exist in real life. This is called **variance shrinkage**.

### 9.5 Single fills pretend to be certain

A filled value is a guess, but a table with the guess in it looks like data. Anything you compute afterwards, such as a confidence interval, treats the 1,400 filled values as if they were observed. The usual cure is **multiple imputation**: fill several times with random draws, analyse each completed table, and look at how much the answer moves. Here is a lightweight version of the idea, using the group random draw from 9.1 with 200 different seeds.

```python run
means = []
for seed in range(200):
    t = apply_strategies(variants["MAR"], seed=seed)
    means.append(t.loc["random draw in group", "mean"])
means = pd.Series(means)
print("random-draw mean over 200 runs: average", round(means.mean()), "| spread (std)", round(means.std()), "| range", round(means.min()), "to", round(means.max()))
print("one fixed fill (group mean)   :", round(apply_strategies(variants["MAR"]).loc["fill group mean (edu)", "mean"]))
print("truth                          :", round(pop["income"].mean()))
```
```text
random-draw mean over 200 runs: average 34383 | spread (std) 71 | range 34197 to 34548
one fixed fill (group mean)   : 34390
truth                          : 34341
```

Across 200 random fills the mean moves by only about 70 rupees (the standard deviation is 71): here that is small compared with the +1,930 *bias* of dropping the rows, so the bias is the big problem, not the randomness. In smaller or more heavily missing datasets the randomness grows. A real analysis reports that spread.

### 9.6 What to write in your report

Because every choice is a claim, a good analysis records it. For each column with missing values, state:

1. **How many** are missing (count and percent), and the pattern (profile table from 8.4).
2. **Why** you think they are missing (MCAR, MAR, MNAR, or a plain-language reason).
3. **What you did** (dropped, filled with what, flagged).
4. **How it changes the answer**: run the main result at least **two ways**, and show both.

A sentence such as "Mean income is 34,400 (rows with a missing income were filled with their education-group mean; dropping them instead gives 36,300, a difference of 5.5 percent, because low-education respondents skipped the question more often)" lets the reader judge. It costs one extra line of code and protects you from the worst outcome: a decision made on a number nobody can reproduce.

> **Try it.** Write one function `two_ways(d)` that returns, as a dictionary, the mean income by "drop rows" and by "fill group mean", and the percent difference between them. Apply it to the three variants. In which variant is the gap largest, and what does that tell you about the missing data?

<details><summary>Answer</summary>

```python run
def two_ways(d):
    drop = d["income"].mean()
    fill = d["income"].fillna(d.groupby("edu_years")["income"].transform("mean")).mean()
    return {"drop": round(drop), "fill_group": round(fill), "gap_pct": float(round((drop / fill - 1) * 100, 1))}


for name, d in variants.items():
    print(name, two_ways(d))
```
```text
MCAR {'drop': 34356, 'fill_group': 34232, 'gap_pct': 0.4}
MAR {'drop': 36271, 'fill_group': 34390, 'gap_pct': 5.5}
MNAR {'drop': 30070, 'fill_group': 31732, 'gap_pct': -5.2}
```

MCAR: the two ways agree within 0.4 percent, the signal that the choice hardly matters. MAR: drop is 5.5 percent above the group fill. MNAR: drop is 5.2 percent *below* it, the opposite sign, because now the survivors are the poorer ones. A large gap warns you that the choice matters, and its sign hints at who is missing. But the gap cannot say which method is right; in the MNAR variant, even the "better" fill is 7.6 percent under the truth. **A small gap is not proof of safety either**: two methods can agree and be wrong the same way.

</details>

### 9.7 Which rule when?

There is no formula, but there are sensible defaults.

| Situation | Reasonable default |
|---|---|
| Under about 5 percent missing, no sign of pattern | drop the rows; say how many |
| Missing depends on visible columns (MAR) | fill using those columns (group value, regression, random draw), and add an indicator |
| Time series with short gaps | `interpolate` or `ffill(limit=...)`; leave long gaps missing |
| Structural missing (not applicable) | keep missing, or a category such as `"not applicable"` |
| Suspected MNAR | do not hide it: report a range (sensitivity analysis) and say so |
| A target column in a model | do **not** fill it; drop those rows for training |
| A column that is more than about 50 percent missing | ask whether to keep it; often it is better dropped |
| You must report one number | report the headline, plus the same number under a second method |

The common thread: **choose with the mechanism in mind, show what the choice did, and keep the alternative visible.**


## 10. Validation by hand

### 10.1 Cleaning is a claim; validation tests the claim

After cleaning, you believe the table is clean. A belief is not a test. **Validation** writes your beliefs down as rules and checks them, every time, on every file. It answers the question "is this table fit for the next step?" with a number, not a feeling.

A rule has three parts: a **name** (so a person can read the report), a **test** (which rows are fine), and a **severity** (does a failure stop the pipeline, or only warn). First we build a small validator by hand, because that makes the idea clear. In section 11 pandera does the same job with less code and a better report.

```python run
def validate_table(df, rules):
    """rules: {name: (column, test, severity)}. The test sees only the NON-missing values:
    'is it in range?' and 'is it there?' are different questions."""
    rows = []
    for name, (col, test, severity) in rules.items():
        s = df[col]
        ok = pd.Series(True, index=df.index)
        ok[s.notna()] = test(s[s.notna()])
        bad = ~ok
        rows.append({"rule": name, "severity": severity, "failing_rows": int(bad.sum()),
                     "first_bad_index": bad[bad].index[:3].tolist()})
    return pd.DataFrame(rows)


RULES = {
    "resp_id is unique":          ("resp_id", lambda s: ~s.duplicated(keep=False), "error"),
    "age in 18..75":              ("age", lambda s: s.between(18, 75), "error"),
    "city is one of the six":     ("city", lambda s: s.astype(str).isin(CITIES), "error"),
    "income in 1,000..1,000,000": ("income", lambda s: s.between(1_000, 1_000_000), "error"),
    "satisfaction in 1..10":      ("satisfaction", lambda s: s.between(1, 10), "error"),
    "signup in 2024..2025":       ("signup", lambda s: s.between("2024-01-01", "2025-12-31"), "error"),
    "phone is 10 digits":         ("phone", lambda s: s.str.fullmatch(r"[6-9]\d{9}"), "warning"),
    "email contains one @":       ("email", lambda s: s.str.count("@").eq(1), "warning"),
}
print(validate_table(step1, RULES).to_string(index=False))
```
```text
                      rule severity  failing_rows first_bad_index
         resp_id is unique    error            40     [0, 23, 66]
             age in 18..75    error             0              []
    city is one of the six    error             0              []
income in 1,000..1,000,000    error             9   [49, 66, 225]
     satisfaction in 1..10    error             0              []
      signup in 2024..2025    error             0              []
        phone is 10 digits  warning             0              []
      email contains one @  warning             0              []
```

We ran it on `step1`: the table after format cleaning, before deduplication and outlier handling. The report is the "to do" list for the next steps, and it agrees with what we found by hand: 40 rows share a repeated `resp_id` (20 repeats in 20 pairs), and 9 incomes are above a million (7 respondents, two of them among the repeated rows). Everything else passes. Missing values pass every rule, because "is this value in range?" is a different question from "is it there?" — the missingness rule comes separately (below).

The phone and email rules report no failures here, because the cleaning functions of section 4 already turned the broken ones into missing values. (Run the same rules on `raw` and they fail; try it.) Two small design choices matter. First, each test sees only the **non-missing** values, so a missing value never fails a range rule. (Without that, `s.between(...)` returns `False` for `NaN`, and a validator would report all the missing incomes as out of range: our first draft did exactly that and reported 95 failures. Test your tests.) The "is it there?" rule is separate, below. Second, severity: an invalid phone number is a *warning* (the survey is still usable), but an age of 150 is an *error*.

```python run
must_be_present = ["resp_id", "city", "satisfaction", "signup"]
print("missing in required columns:", step1[must_be_present].isna().sum().sum())
print("share of rows complete in all columns:", round(step1.notna().all(axis=1).mean() * 100, 1), "%")
```
```text
missing in required columns: 0
share of rows complete in all columns: 72.3 %
```

### 10.2 Assert, warn, or quarantine?

Three ways to react to a failing rule.

| Reaction | When | Example |
|---|---|---|
| **Stop** (`raise`, `assert`) | the problem makes every result wrong | the file has no `income` column at all |
| **Warn and continue** | the table is usable, but someone should look | 4 percent of emails are broken |
| **Quarantine** the bad rows | a few rows are bad, and the rest are fine | the impossible incomes |

Quarantine is the middle road that analysts often forget. The bad rows go into a separate `rejects` table **with the reason**. Nothing is silently deleted, and the pipeline is able to finish.

```python run
bad_income = ~step1["income"].between(1_000, 1_000_000) & step1["income"].notna()
clean_part, rejects = step1[~bad_income], step1[bad_income].assign(reason="income outside 1,000..1,000,000")
print("kept:", len(clean_part), "| quarantined:", len(rejects))
print(rejects[["resp_id", "income", "reason"]].head(3).to_string(index=False))
```
```text
kept: 626 | quarantined: 9
 resp_id       income                          reason
    1050 3,640,000.00 income outside 1,000..1,000,000
    1067 5,790,000.00 income outside 1,000..1,000,000
    1226 4,660,000.00 income outside 1,000..1,000,000
```

A hand-built validator is not hard but it grows quickly: you also want type checks, uniqueness, column presence, strict column lists and a report. That is what a library is for.

## 11. Validation with pandera

### 11.1 A schema

**Pandera** lets you describe the table you expect, a **schema**, and then check any DataFrame against it. A schema lists the columns, their dtypes and the checks each must pass. Think of it as a contract between the cleaning code and the analysis code.

```python run
survey_schema = pa.DataFrameSchema(
    {
        "resp_id": pa.Column(int, unique=True),
        "age": pa.Column("Int64", pa.Check.in_range(18, 75), nullable=True),
        "city": pa.Column(str, pa.Check.isin(CITIES)),
        "income": pa.Column(float, pa.Check.in_range(1_000, 1_000_000), nullable=True),
        "satisfaction": pa.Column(int, pa.Check.in_range(1, 10)),
        "signup": pa.Column("datetime64[ns]", pa.Check.in_range(pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31"))),
        "phone": pa.Column(str, pa.Check.str_matches(r"^[6-9]\d{9}$"), nullable=True),
        "email": pa.Column(str, pa.Check.str_contains("@"), nullable=True),
    },
    strict=False,
    name="survey_v1",
)
print(survey_schema.name, "| columns:", list(survey_schema.columns))
```
```text
survey_v1 | columns: ['resp_id', 'age', 'city', 'income', 'satisfaction', 'signup', 'phone', 'email']
```

Read it like a sentence: "`age` is a nullable integer between 18 and 75." The word `nullable=True` says a missing value is allowed; the default is `False`, so a missing value in `resp_id` would be an error unless you permit it. That default is a good one: **missing values should be allowed on purpose, column by column.**

### 11.2 Validating, and reading the failure

`schema.validate(df)` returns the table if it passes and **raises at the first error** otherwise.

```python run
try:
    survey_schema.validate(step1.astype({"city": str}))
except pa.errors.SchemaError as e:
    print(str(e).splitlines()[0])
```
```text
series 'resp_id' contains duplicate values:
```

The first line names the column and the check that failed. One error at a time is slow when a table has many problems. Use `lazy=True` to collect **all** failures, and read them from `SchemaErrors.failure_cases`.

```python run
def lazy_report(schema, df):
    try:
        schema.validate(df, lazy=True)
        return pd.DataFrame(columns=["column", "check", "failure_case", "index"])
    except pa.errors.SchemaErrors as e:
        return e.failure_cases[["column", "check", "failure_case", "index"]]


fc = lazy_report(survey_schema, step1.astype({"city": str}))
print(len(fc), "failing cells")
print(fc.groupby(["column", "check"]).size().rename("failures").to_string())
```
```text
49 failing cells
column   check                  
income   in_range(1000, 1000000)     9
resp_id  field_uniqueness           40
```

`failure_cases` is an ordinary DataFrame: one row per failing cell, with the column, the check, the offending value and the row index. That means you can group it, count it, save it, and (importantly) feed the `index` column back to the data to look at the rows.

```python run
print(fc.head(5).to_string(index=False))
```
```text
 column            check  failure_case  index
resp_id field_uniqueness      1,001.00      0
resp_id field_uniqueness      1,024.00     23
resp_id field_uniqueness      1,067.00     66
resp_id field_uniqueness      1,148.00    147
resp_id field_uniqueness      1,166.00    165
```

> **Predict the output.** Before the schema ran, the hand-built validator reported 7 incomes above a million. How many `income` failures do you expect from pandera, and how many `resp_id` failures? Think about what "unique=True" counts.

<details><summary>Answer</summary>

```python run
print(fc.groupby("column").size().to_string())
```
```text
column
income      9
resp_id    40
```

Income: 9, the same rows as the hand-built validator (7 respondents; two of them are in the repeated rows). For `resp_id`, pandera reports **40**, one failure for every row that takes part in a repeated value: each of the 20 repeated ids appears twice, so both rows are reported. A "unique" check marks all the copies, as `duplicated(keep=False)` does, since it cannot know which one you want to keep. (Our hand-built rule used `keep=False` too, so it also said 40.)

</details>

### 11.3 The checks you will use most

| Check | Meaning |
|---|---|
| `Check.ge(0)`, `gt`, `le`, `lt` | comparison with a bound |
| `Check.in_range(lo, hi)` | between two bounds (inclusive by default) |
| `Check.isin([...])`, `notin` | allowed or forbidden values |
| `Check.str_matches(rx)` | the regex must match from the start |
| `Check.str_contains(rx)` | the regex appears somewhere |
| `Check.str_length(min, max)` | length limits |
| `Check(lambda s: ..., error="...")` | a custom rule; returns a Boolean Series |
| `Check(lambda s: ..., element_wise=True)` | custom rule for one value at a time (slower) |
| `unique=True` (on a Column) | no repeats |
| `nullable=True` (on a Column) | missing values allowed |
| `coerce=True` (on a Column) | convert the dtype first, then check |
| `required=False` (on a Column) | the column may be absent |

**Custom checks** receive the whole column as a Series and must return a Boolean Series of the same length (or one Boolean). Always add `error="..."`: it becomes the message in the report.

```python run
income_not_round = pa.Check(lambda s: s % 100 == 0, error="income is a multiple of 100", ignore_na=True)
mini = pa.DataFrameSchema({"income": pa.Column(float, income_not_round, nullable=True)})
print(lazy_report(mini, pd.DataFrame({"income": [45_000.0, 45_050.0, np.nan]})).to_string(index=False))
```
```text
column                       check  failure_case  index
income income is a multiple of 100     45,050.00      1
```

`ignore_na=True` (the default for most checks) skips missing values, which matches our hand-built rule: *validity* and *presence* are separate questions.

### 11.4 Cross-column checks

Many real rules involve two columns: an end date after the start date, a `discount` smaller than the `price`, a `total` equal to the sum of the parts. These are **dataframe-level checks**: you pass them to `checks=` on the schema, and they receive the whole DataFrame.

```python run
bookings = pd.DataFrame({
    "start": pd.to_datetime(["2025-01-01", "2025-03-10", "2025-06-01"]),
    "end":   pd.to_datetime(["2025-01-05", "2025-03-02", "2025-06-09"]),
    "price": [100.0, 80.0, 120.0],
    "discount": [10.0, 5.0, 150.0],
})
trip_schema = pa.DataFrameSchema(
    {"start": pa.Column("datetime64[ns]"), "end": pa.Column("datetime64[ns]"),
     "price": pa.Column(float, pa.Check.ge(0)), "discount": pa.Column(float, pa.Check.ge(0))},
    checks=[pa.Check(lambda d: d["end"] >= d["start"], error="end is not before start"),
            pa.Check(lambda d: d["discount"] <= d["price"], error="discount is at most the price")],
)
print(lazy_report(trip_schema, bookings).to_string(index=False))
```
```text
  column                         check        failure_case  index
   start       end is not before start 2025-03-10 00:00:00      1
     end       end is not before start 2025-03-02 00:00:00      1
   price       end is not before start               80.00      1
discount       end is not before start                5.00      1
   start discount is at most the price 2025-06-01 00:00:00      2
     end discount is at most the price 2025-06-09 00:00:00      2
   price discount is at most the price              120.00      2
discount discount is at most the price              150.00      2
```

A cross-column failure is reported for the columns involved. Row 1 ends before it starts, and row 2 gives a discount larger than the price. Neither value is out of range on its own; only the relation is wrong. These are the errors that single-column cleaning never finds.

### 11.5 Coerce, nullable and strict

Three schema options change how forgiving the validation is.

- **`coerce=True`** tries to convert the column to the declared dtype before checking. It saves a separate `astype` step, but be careful: coercing `"abc"` to a number raises an error, and coercing a float column with `NaN` to a plain `int` fails. Use `"Int64"` for integers that can be missing.
- **`nullable=True`**, as above.
- **`strict=True`** rejects any column the schema does not list (and `strict="filter"` silently drops them). That is a good protection against a new, unexpected column in next month's file.

```python run
loose = pa.DataFrameSchema({"age": pa.Column("Int64", pa.Check.in_range(18, 75), nullable=True, coerce=True)}, strict=True)
data = pd.DataFrame({"age": ["25", "40", None], "surprise": [1, 2, 3]})
print(lazy_report(loose, data).to_string(index=False))
print(loose.validate(data.drop(columns="surprise"))["age"].tolist())
```
```text
column            check failure_case index
  None column_in_schema     surprise  None
[25, 40, <NA>]
```

The text ages `"25"` and `"40"` were coerced to integers and the `None` became `<NA>`. The unexpected column was reported by name. The fix went in the table, not in the schema.

### 11.6 Drop invalid rows and the model style

If you want pandera to remove the failing rows for you, pass `drop_invalid_rows=True` to the schema and use `lazy=True`:

```python run
dropping = pa.DataFrameSchema({"age": pa.Column(float, pa.Check.in_range(18, 75), nullable=True)}, drop_invalid_rows=True)
print(dropping.validate(pd.DataFrame({"age": [20.0, 150.0, np.nan]}), lazy=True)["age"].tolist())
```
```text
[20.0, nan]
```

Use that with care. It deletes rows without writing a reason, which breaks our rule 3 ("flag before you delete"). The pipeline in section 12 does the quarantine ourselves, so that the reason is kept.

Pandera has a second, class-based style that many teams prefer because it reads like a typed class. The columns are annotations, the checks are `Field(...)` arguments, and extra rules are methods marked `@pa.check`.

```python run
from pandera.typing import Series


class SurveyModel(pa.DataFrameModel):
    resp_id: Series[int] = pa.Field(unique=True)
    age: Series["Int64"] = pa.Field(in_range={"min_value": 18, "max_value": 75}, nullable=True)
    city: Series[str] = pa.Field(isin=CITIES)
    income: Series[float] = pa.Field(in_range={"min_value": 1_000, "max_value": 1_000_000}, nullable=True)

    @pa.check("city")
    def city_is_clean(cls, s: Series[str]) -> Series[bool]:
        return s == s.str.strip().str.title()

    class Config:
        strict = False


tiny = pd.DataFrame({"resp_id": [1, 2, 3], "age": pd.array([20, 30, None], dtype="Int64"),
                     "city": ["Pune", "delhi", "Jaipur"], "income": [30_000.0, 40_000.0, np.nan]})
print(lazy_report(SurveyModel.to_schema(), tiny).to_string(index=False))
```
```text
column                                                             check failure_case  index
  city isin(['Pune', 'Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Jaipur'])        delhi      1
  city                                                     city_is_clean        delhi      1
```

Both styles build the same kind of schema object (`to_schema()`); choose one and use it everywhere. The dictionary style is easier to generate from code; the class style is easier to read.

### 11.7 The schema as documentation

A schema is documentation that cannot go out of date, because the pipeline fails when it is. You can export it to YAML to put in the repository next to the data:

```python run
text = survey_schema.to_yaml()
print(text.splitlines()[0:2])
print("lines in the YAML export:", len(text.splitlines()))
print("\n".join(text.splitlines()[6:20]))
```
```text
['schema_type: dataframe', 'api: pandas']
lines in the YAML export: 54
  age:
    dtype: Int64
    nullable: true
    in_range:
      min_value: 18
      max_value: 75
      include_min: true
      include_max: true
  city:
    dtype: string[pyarrow]
    isin:
    - Pune
    - Delhi
    - Mumbai
```

### 11.8 What a schema cannot do

A schema checks **rules you thought of**. It cannot see a mistake you did not think of, and it cannot say that a plausible value is true. An income of 45,000 passes whether or not the person really earns it. Passing validation means "nothing I know to be wrong is wrong". Three rules of thumb:

1. **Validate at the borders.** Check the raw input (loose schema: right columns, right types) and the clean output (strict schema: right ranges, no unexpected missing).
2. **Test your schema with bad data.** Feed it a table you made wrong on purpose, as we did, and check that it fails the right way. A schema that never fails is as useless as one that always fails.
3. **Do not weaken a rule to make the pipeline pass.** If the rule fires, one of two things is true: the data is wrong, or the rule is wrong. Find out which. Then change the right one, and write down why.

## 12. A cleaning pipeline you can trust

### 12.1 The shape of a good pipeline

All the pieces now exist. A pipeline puts them in order, makes each step a small function that takes a DataFrame and returns a DataFrame (so it can be tested alone), and records what happened.

```text
raw file ──► 1 formats ──► 2 duplicates ──► 3 outliers ──► 4 validate ──► clean table
                                                              │
                                                              └──► rejects (rows + reason)
every step writes a line to the LOG; the raw file is never changed
```

The order matters. Fix **formats** first (you cannot compare `"Pune"` with `"pune "`). Remove **duplicates** next (so they do not count twice in any statistic). Handle **outliers** after formats (you cannot compare `"₹45,000"` as text), and before filling missing values (an unfixed outlier would pollute a mean-based fill). **Validate** last, and quarantine what still fails.

### 12.2 The steps as functions

```python run
def step_formats(df):
    out = pd.DataFrame({
        "resp_id": df["resp_id"],
        "age": df["age"].where(df["age"].between(18, 75)).astype("Int64"),
        "city": df["city"].str.strip().str.rstrip(".").str.title().replace(CITY_FIX),
        "income": parse_income(df["income"]),
        "satisfaction": df["satisfaction"],
        "signup": parse_signup(df["signup"]),
        "phone": clean_phone(df["phone"]),
        "email": clean_email(df["email"]),
        "email_key": df["email"].str.strip().str.lower(),
    })
    return out


def step_duplicates(df):
    df = df.drop_duplicates()
    return (df.sort_values("resp_id").drop_duplicates(subset=["email_key"], keep="last").sort_index())


INCOME_MAX = 1_000_000      # a fixed, written-down bound (found with the robust z-score in section 6)


def step_outliers(df, income_max=INCOME_MAX):
    out = df.copy()
    new_flag = (out["income"] > income_max).fillna(False)
    out["income_flag"] = (out["income_flag"] | new_flag) if "income_flag" in out else new_flag   # never erase an old flag
    out["income"] = out["income"].mask(out["income_flag"])          # set to missing, keep the flag
    return out


def step_validate(df, schema):
    """Return (clean rows, rejected rows with a reason). Uses the lazy report so every failure is seen."""
    try:
        schema.validate(df, lazy=True)
        return df, df.iloc[0:0].assign(reason=pd.Series(dtype="str"))
    except pa.errors.SchemaErrors as e:
        fc = e.failure_cases.dropna(subset=["index"])
        why = fc.groupby("index").apply(lambda g: "; ".join(sorted(set(g["column"] + ": " + g["check"].astype(str)))))
        bad = df.loc[why.index.astype(int)]
        return df.drop(index=bad.index), bad.assign(reason=why.astype(str).values)


print("steps defined")
```
```text
steps defined
```

Each step does one job and can be tested on its own. Now chain them with `pipe` and write the log:

```python run
LOG.clear()
t0 = raw.copy()
t1 = log_step("1 formats", t0, step_formats(t0), "text -> typed; codes -> missing")
t2 = log_step("2 duplicates", t1, step_duplicates(t1), "exact repeats and re-submissions (newest wins)")
t3 = log_step("3 outliers", t2, step_outliers(t2), "income above 1,000,000 -> missing + flag")
t4, rejects = step_validate(t3, survey_schema)
_ = log_step("4 validate", t3, t4, f"{len(rejects)} rows quarantined")
print(show_log().to_string(index=False))
print("\nincome flagged and set to missing:", int(t3["income_flag"].sum()))
```
```text
        step  rows_before  rows_after  na_before  na_after                                           note
   1 formats          635         635         14       192                text -> typed; codes -> missing
2 duplicates          635         600        192       187 exact repeats and re-submissions (newest wins)
  3 outliers          600         600        187       194       income above 1,000,000 -> missing + flag
  4 validate          600         600        194       194                             0 rows quarantined

income flagged and set to missing: 7
```

Read the log from top to bottom. The row count falls from 635 to 600 at step 2 and stays there. The missing cells rise at step 1 (hidden codes become visible) and again at step 3 (the 7 outliers become missing on purpose). Step 4 quarantines nothing, because the earlier steps already did the work. The log is the receipt of the whole run.

### 12.3 Test the pipeline against the truth

Because we hold the truth, we can score the pipeline. A real project would test against a small hand-checked sample instead.

```python run
tk = truth.set_index(truth["email"].str.replace("@", "", regex=False))
cl = t4.set_index(t4["email_key"].str.replace("@", "", regex=False))
cmp = cl.join(tk, rsuffix="_true", how="left")
print("rows:", len(cl), "| match the truth rows:", cmp["age_true"].notna().sum())
print("city correct   :", round((cmp["city"] == cmp["city_true"]).mean() * 100, 1), "%")
print("signup correct :", round((cmp["signup"] == cmp["signup_true"]).mean() * 100, 1), "%")
ok_i = cmp["income"].notna()
print("income correct where present:", round((cmp.loc[ok_i, "income"] == cmp.loc[ok_i, "income_true"]).mean() * 100, 1), "%")
ok_a = cmp["age"].notna()
print("age correct where present   :", round((cmp.loc[ok_a, "age"] == cmp.loc[ok_a, "age_true"]).mean() * 100, 1), "%")
print("mean income, clean            :", round(cl["income"].mean()))
print("mean income, truth, same rows :", round(cmp.loc[ok_i, "income_true"].mean()))
print("mean income, truth, all rows  :", round(cmp["income_true"].mean()))
```
```text
rows: 600 | match the truth rows: 600
city correct   : 100.0 %
signup correct : 100.0 %
income correct where present: 100.0 %
age correct where present   : 100.0 %
mean income, clean            : 44673
mean income, truth, same rows : 44673
mean income, truth, all rows  : 45324
```

Everything that is present is correct, and the mean on the same rows matches the truth. The last line differs, because the truth also includes the incomes we cannot see (missing in the raw file, or set to missing as impossible). The pipeline did *not* recover the missing incomes and ages: it cannot invent them. And that brings us back to the main question of the chapter: now that the table is clean, what do we do with the values still missing? That decision is **not** part of the cleaning pipeline's mechanics; it belongs to the analysis, and it has to be named in the report (section 9.6).

### 12.4 Idempotence and reproducibility

Two properties tell you that a pipeline is well built.

**Idempotent**: running the cleaner on already-clean data changes nothing. If it does, a step is doing something unstable.

**Deterministic**: the same input gives the same output. Any step that uses random numbers (a random fill) must take a seed.

Why does the pipeline use a **fixed bound** for outliers, and not the robust z-score directly? Because a rule relative to the data (median, MAD, percentile) **moves when the data move**. Look at the income limit that the robust z-score implies, for the real table and for a bad batch in which 45 of 100 incomes were typed with extra zeros:

```python run
def implied_upper_bound(s, t=3.5):
    lg = np.log10(s.dropna())
    med = lg.median()
    mad = (lg - med).abs().median()
    return 10 ** (med + t * mad / 0.6745)


good = t2["income"]
bad_batch = good.dropna().sample(100, random_state=3).copy()
bad_batch.iloc[:45] *= 100
print("implied limit, normal table:", f"{implied_upper_bound(good):>12,.0f}")
print("implied limit, bad batch   :", f"{implied_upper_bound(bad_batch):>12,.0f}")
print("a fixed limit stays at     :", f"{INCOME_MAX:>12,.0f}")
```
```text
implied limit, normal table:      220,103
implied limit, bad batch   :  360,754,961
a fixed limit stays at     :    1,000,000
```

On the bad batch the statistical limit jumps to hundreds of millions, so the batch's errors become "normal" and nothing is flagged: masking again, and nobody is warned. The fixed bound, written down after studying good data, catches them. So: *use statistics to find the bound, then freeze it as a domain rule.*

The second check is idempotence:

```python run
again, _ = step_validate(step_outliers(step_duplicates(t4.copy())), survey_schema)
print("clean twice == clean once:", again.equals(t4))
a = step_formats(raw)
b = step_formats(raw)
print("same input, same output  :", a.equals(b))
```
```text
clean twice == clean once: True
same input, same output  : True
```

This check found a real bug while this chapter was written: the first version of `step_outliers` recomputed `income_flag` from the income column on every run, so the second run found no income above the bound (it was already missing) and erased the flag. The fix is the line `out["income_flag"] | new_flag`: never erase information that an earlier run recorded.

### 12.5 Write the outputs

A run produces four things: the **clean** table, the **rejects**, the **log**, and the **schema**. Save all four, and never overwrite the raw file.

```python run
import tempfile, pathlib
_tmp = tempfile.TemporaryDirectory()
out = pathlib.Path(_tmp.name)
t4.to_csv(out / "survey_clean.csv", index=False)
rejects.to_csv(out / "survey_rejects.csv", index=False)
show_log().to_csv(out / "cleaning_log.csv", index=False)
(out / "survey_schema.yaml").write_text(survey_schema.to_yaml())
print(sorted(p.name for p in out.iterdir()))
back = pd.read_csv(out / "survey_clean.csv", parse_dates=["signup"])
print(back.dtypes.astype(str).to_dict())
```
```text
['cleaning_log.csv', 'survey_clean.csv', 'survey_rejects.csv', 'survey_schema.yaml']
{'resp_id': 'int64', 'age': 'float64', 'city': 'str', 'income': 'float64', 'satisfaction': 'int64', 'signup': 'datetime64[us]', 'phone': 'float64', 'email': 'str', 'email_key': 'str', 'income_flag': 'bool'}
```

(The temporary folder name is machine-specific, so we print only the file names.) Look at the dtypes after reading the CSV back: `age` is `float64` (a missing value was written as an empty cell), `phone` is `float64` too (a number-looking text lost its type, and a phone number with a leading zero would lose the zero), the dates survive only because we asked for `parse_dates`. **CSV forgets types.** For files that other programs will read, a typed format such as Parquet (da.03) keeps dtypes; or keep the schema next to the CSV and validate after loading. This is the second job of a schema: it lets the next person load the file safely.


## 13. Project: a documented cleaning pipeline

**The brief.** A city publishes hourly air-quality readings from four monitoring stations as an open-data CSV. You are asked one simple question: **what is the average PM2.5 (a fine-dust measure, in µg/m³) at each station, and how often is the air above the limit of 60 µg/m³?** Before anyone can trust that answer, the file must be cleaned, the cleaning must be documented, and the effect of the missing readings must be shown.

The assignment, as a checklist:

1. A cleaning pipeline made of small functions, with a **log**.
2. A **pandera schema** for the clean table, with a quarantine of rows that fail.
3. A **data dictionary** (what each column means, its unit, its allowed values).
4. A **missing-data report**: how many, where, why (MCAR / MAR / MNAR), and the final answer computed **two ways**.
5. A short **cleaning report** that a colleague could read without opening your code.

> **Using a real public dataset.** Open-data portals publish files like this (air quality, bike hire, road accidents, school results). This chapter works offline, so the file below is synthetic, built to have the usual problems. Everything you write for it works on a downloaded file if you change only the loading line and the names in the rules. When you do use a real file, start at section 2 (the audit) and write your own rules from what you see; do not copy these.

### 13.1 The raw file and its known problems

The generator keeps the truth (the clean, complete readings), so we can score our work at the end. The dirt, listed:

- station names in three spellings each (`Central`, `central `, `CENTRAL`, `hill-road`);
- two timestamp formats: one station writes `01/03/2025 14:00` (day first), the others `2025-03-01 14:00`;
- a code `-999` for "sensor error", in 3 percent of the readings;
- 40 repeated rows (the logger sent them twice);
- 10 spikes (a reading 8 times too high);
- one **stuck sensor**: `Hill Road` repeats the same value for 36 hours;
- one **outage**: `Riverside` is silent for 3 days;
- a **fog effect**: when humidity is above 85 percent, the optical sensor fails half of the time. High humidity also goes with higher dust here. This is MAR.

```python run
STATIONS = ["Central", "Riverside", "Hill Road", "Airport"]


def make_air(seed=21, days=45):
    rng = np.random.default_rng(seed)
    hours = pd.date_range("2025-03-01", periods=days * 24, freq="h")
    frames = []
    for st, base in zip(STATIONS, [55, 40, 70, 35]):
        h = hours.hour.values
        hum = np.clip(60 + 25 * np.sin((h - 4) / 24 * 2 * np.pi) + rng.normal(0, 8, len(hours)), 20, 100).round(0)
        pm = base + 0.6 * (hum - 60) + 12 * np.sin((h - 8) / 24 * 2 * np.pi) + rng.normal(0, 6, len(hours))
        frames.append(pd.DataFrame({"station": st, "ts": hours, "pm25": np.clip(pm, 2, None).round(1), "humidity": hum}))
    air_truth = pd.concat(frames, ignore_index=True)

    raw = air_truth.copy()
    pm = raw["pm25"].copy()
    pm[(raw["humidity"] > 85) & (rng.random(len(raw)) < .5)] = np.nan                 # fog: MAR
    pm[(raw["station"] == "Riverside") & (raw["ts"] >= "2025-03-21") & (raw["ts"] < "2025-03-24")] = np.nan  # outage
    pm[(raw["station"] == "Hill Road") & (raw["ts"] >= "2025-03-10 06:00") & (raw["ts"] < "2025-03-11 18:00")] = 41.0  # stuck
    spikes = rng.choice(len(raw), 10, replace=False)
    pm.iloc[spikes] = pm.iloc[spikes] * 8
    pm[rng.random(len(raw)) < .03] = -999
    raw["pm25"] = pm

    ts = raw["ts"].dt.strftime("%Y-%m-%d %H:%M")
    raw["ts"] = np.where(raw["station"] == "Airport", raw["ts"].dt.strftime("%d/%m/%Y %H:%M"), ts)
    spell = {"Central": ["Central", "central ", "CENTRAL"], "Riverside": ["Riverside", "RIVERSIDE", "riverside "],
             "Hill Road": ["Hill Road", "hill-road", "HILL ROAD "], "Airport": ["Airport", "airport", "AIRPORT "]}
    pick = rng.choice(3, len(raw), p=[.7, .15, .15])
    raw["station"] = [spell[s][i] for s, i in zip(raw["station"], pick)]
    raw = pd.concat([raw, raw.sample(40, random_state=4)], ignore_index=True)
    return air_truth, raw


air_truth, air_raw = make_air()
print("raw:", air_raw.shape, "| truth:", air_truth.shape)
print(audit(air_raw).drop(columns="example").to_string())
```
```text
raw: (4360, 4) | truth: (4320, 4)
            dtype  missing  pct_missing  distinct
station       str        0         0.00        12
ts            str        0         0.00      2160
pm25      float64      272         6.20       928
humidity  float64        0         0.00        81
```

Run the audit and read it, as in section 2. `station` has 12 spellings instead of 4. `ts` is text. `pm25` hides the `-999` code, so its missing count of about 6 percent understates the problem. Now write rules from what you see.

### 13.2 The data dictionary comes first

Write what the clean table must look like **before** you write the cleaning code. Then the code has a target, and the schema is only the dictionary turned into checks.

```python run
dictionary = pd.DataFrame([
    ("station", "text", "-", "one of Central, Riverside, Hill Road, Airport", "no"),
    ("ts", "datetime", "local time", "hour start; one row per station and hour", "no"),
    ("pm25", "float", "µg/m³", "0 to 500; fine dust, sensor reading", "yes (reason in pm25_flag)"),
    ("humidity", "float", "percent", "0 to 100; relative humidity", "yes (outage)"),
    ("pm25_flag", "category", "-", "ok / code / spike / stuck / missing: why pm25 is missing or was removed", "no"),
], columns=["column", "type", "unit", "meaning and allowed values", "missing allowed"])
print(dictionary.to_string(index=False))
```
```text
   column     type       unit                                              meaning and allowed values           missing allowed
  station     text          -                           one of Central, Riverside, Hill Road, Airport                        no
       ts datetime local time                                hour start; one row per station and hour                        no
     pm25    float      µg/m³                                     0 to 500; fine dust, sensor reading yes (reason in pm25_flag)
 humidity    float    percent                                             0 to 100; relative humidity              yes (outage)
pm25_flag category          - ok / code / spike / stuck / missing: why pm25 is missing or was removed                        no
```

### 13.3 The pipeline

Each step is a function that takes a DataFrame and returns one. The new idea in this project is `pm25_flag`: **one column that records the reason** why a reading was removed. Later, the report counts the reasons.

```python run
LIMIT = 60.0          # the air-quality limit asked about in the brief


def air_formats(df):
    out = df.copy()
    out["station"] = (out["station"].str.strip().str.replace("-", " ", regex=False).str.title())
    is_dmy = out["ts"].str.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}")
    is_iso = out["ts"].str.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
    assert (is_dmy ^ is_iso).all(), "a timestamp matches neither known format (or both)"
    out["ts"] = pd.to_datetime(out["ts"].where(is_iso).fillna(""), format="%Y-%m-%d %H:%M", errors="coerce") \
                  .fillna(pd.to_datetime(out["ts"].where(is_dmy).fillna(""), format="%d/%m/%Y %H:%M", errors="coerce"))
    assert out["ts"].notna().all()
    out["pm25_flag"] = np.where(out["pm25"] == -999, "code", np.where(out["pm25"].isna(), "missing", "ok"))
    out["pm25"] = out["pm25"].mask(out["pm25"] == -999)
    return out


def air_duplicates(df):
    return df.drop_duplicates(subset=["station", "ts"], keep="first").sort_values(["station", "ts"]).reset_index(drop=True)


def air_suspects(df, spike_ratio=3.0, stuck_hours=6, hi=500):
    out = df.copy()
    g = out.groupby("station")["pm25"]
    neighbours = g.transform(lambda s: s.rolling(7, center=True, min_periods=3).median())      # typical value around the hour
    spike = (out["pm25"] > spike_ratio * neighbours) | (out["pm25"] > hi)
    same = out["pm25"].eq(g.shift())                                                          # equal to the previous hour?
    run_id = (~same).groupby(out["station"]).cumsum()
    run_len = out.groupby(["station", run_id])["pm25"].transform("size")
    stuck = out["pm25"].notna() & (run_len >= stuck_hours)
    out.loc[spike.fillna(False), "pm25_flag"] = "spike"
    out.loc[stuck, "pm25_flag"] = "stuck"
    out["pm25"] = out["pm25"].mask(out["pm25_flag"].isin(["spike", "stuck"]))
    return out


LOG.clear()
a0 = air_raw.copy()
a1 = log_step("1 formats", a0, air_formats(a0), "names, timestamps, -999 -> missing")
a2 = log_step("2 duplicates", a1, air_duplicates(a1), "same station + hour: first copy kept")
a3 = log_step("3 suspects", a2, air_suspects(a2), "spikes and stuck runs -> missing, reason kept")
print(show_log().to_string(index=False))
print()
print(a3["pm25_flag"].value_counts().to_string())
```
```text
        step  rows_before  rows_after  na_before  na_after                                          note
   1 formats         4360        4360        272       411            names, timestamps, -999 -> missing
2 duplicates         4360        4320        411       405          same station + hour: first copy kept
  3 suspects         4320        4320        405       445 spikes and stuck runs -> missing, reason kept

pm25_flag
ok         3875
missing     267
code        138
stuck        33
spike         7
```

Three decisions in this code are worth a comment, because each one is a place where a different, equally reasonable choice exists.

- **The spike rule is relative to the neighbours** (3 times the median of the 7 readings around it), not to the whole table. A reading of 150 µg/m³ is an outlier on a quiet night, and plausible on a polluted evening: the context decides. A rolling median is robust to the spike itself.
- **The stuck rule counts runs.** A real sensor may give the same value twice in a row (`41.0, 41.0`), but not six times. `run_len >= 6` is a judgement; we write it as a parameter, so it is visible.
- **The reason is kept.** `pm25` becomes missing, but `pm25_flag` says `code`, `spike` or `stuck`. A plain `NaN` would have lost the story.

> **Try it.** The spike rule found a number of spikes. We planted 10, but some got `-999` or became missing earlier. How many rows have flag `spike` and are *not* among our planted spikes? Use the truth to answer: compare `pm25` before suspect-removal (`a2`) to the truth value for the flagged rows.

<details><summary>Answer</summary>

```python run
key = ["station", "ts"]
chk = a2.merge(air_truth[key + ["pm25"]], on=key, suffixes=("", "_true"))
chk["flag3"] = a3.merge(chk[key], on=key)["pm25_flag"].values
sp = chk[chk["flag3"] == "spike"]
print("flagged as spike:", len(sp))
print("really spikes (more than 3x the truth):", int((sp["pm25"] > 3 * sp["pm25_true"]).sum()))
st = chk[chk["flag3"] == "stuck"]
print("flagged as stuck:", len(st), "| the stuck period was 36 hours at Hill Road")
```
```text
flagged as spike: 7
really spikes (more than 3x the truth): 7
flagged as stuck: 33 | the stuck period was 36 hours at Hill Road
```

Every spike flag is a real one: no honest reading was removed. We planted 10 spikes, and 7 were found; the other 3 were already hidden by a `-999` code or a missing value before the rule ran. The stuck rule flagged 33 of the 36 stuck hours at Hill Road, and the other 3 hours were already missing. If a rule removed honest readings, you would see them here: the "truth" check is the test of the rule. In a real project, you test with a handful of rows you inspected by hand.

</details>

### 13.4 Validate: the schema and the quarantine

The schema is the dictionary written as code. Note the **uniqueness over two columns** (`unique=["station", "ts"]`): one row per station and hour.

```python run
air_schema = pa.DataFrameSchema(
    {
        "station": pa.Column(str, pa.Check.isin(STATIONS)),
        "ts": pa.Column("datetime64[ns]", pa.Check.in_range(pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-30"))),
        "pm25": pa.Column(float, pa.Check.in_range(0, 500), nullable=True),
        "humidity": pa.Column(float, pa.Check.in_range(0, 100), nullable=True),
        "pm25_flag": pa.Column(str, pa.Check.isin(["ok", "code", "spike", "stuck", "missing"])),
    },
    unique=["station", "ts"],
    strict=True,
    name="air_v1",
)
a3["ts"] = a3["ts"].astype("datetime64[ns]")
checked = air_schema.validate(a3, lazy=True)
print("schema passes:", checked.shape)
print("rows per station:", a3.groupby("station").size().to_dict())
print("expected per station:", 45 * 24)
```
```text
schema passes: (4320, 5)
rows per station: {'Airport': 1080, 'Central': 1080, 'Hill Road': 1080, 'Riverside': 1080}
expected per station: 1080
```

One more rule is worth adding as a cross-check: **a value is present exactly when the flag says `ok`**. This protects the next person who edits the pipeline and forgets to set the flag.

```python run
consistent = pa.Check(lambda d: d["pm25"].notna() == (d["pm25_flag"] == "ok"), error="pm25 present <=> flag is ok")
air_schema2 = pa.DataFrameSchema(air_schema.columns, unique=["station", "ts"], strict=True, checks=[consistent], name="air_v2")
air_schema2.validate(a3, lazy=True)
print("cross-column rule passes:", True)
broken = a3.copy()
broken.loc[5, "pm25_flag"] = "ok"           # pretend somebody forgot a flag
broken.loc[5, "pm25"] = np.nan
rep = lazy_report(air_schema2, broken)
print("rule that fired:", rep["check"].unique().tolist(), "| row:", sorted(rep["index"].unique().tolist()))
```
```text
cross-column rule passes: True
rule that fired: ['pm25 present <=> flag is ok'] | row: [5]
```

A deliberately broken table fails the new rule. This is the "test your schema" habit of section 11.8.

### 13.5 The missing-data report

Now the part of the project that matters most. After cleaning, how much is missing, where, and why?

```python run
a4 = a3.copy()
share = (a4["pm25"].isna().groupby(a4["station"]).mean() * 100).round(1)
print("percent of pm25 missing, by station")
print(share.to_string())
print()
print(pd.crosstab(a4["station"], a4["pm25_flag"]).to_string())
```
```text
percent of pm25 missing, by station
station
Airport      8.20
Central      7.90
Hill Road   10.80
Riverside   14.30

pm25_flag  code  missing   ok  spike  stuck
station                                    
Airport      38       49  991      2      0
Central      35       49  995      1      0
Hill Road    28       54  963      2     33
Riverside    37      115  926      2      0
```

`Riverside` stands out with its 3-day outage; `Hill Road` has the 36 stuck hours. The other columns of the crosstab are the reasons. Now the MAR check: does missingness depend on **humidity**?

```python run
bins = pd.cut(a4["humidity"], [0, 40, 60, 80, 85, 100])
prof = (a4["pm25"].isna().groupby(bins, observed=True).mean() * 100).round(1)
print("percent of pm25 missing, by humidity band")
print(prof.to_string())
```
```text
percent of pm25 missing, by humidity band
humidity
(0, 40]      5.10
(40, 60]     5.70
(60, 80]     6.10
(80, 85]     6.20
(85, 100]   51.40
```

Below 85 percent humidity the missing rate is a flat few percent; above 85 percent it jumps to about 50. That is a clear MAR signature: missingness depends on a **visible** column (humidity), and, since humid air carries more dust in this data, the missing readings are not typical readings. Dropping them will bias the average low. This is what we expect; now we measure it.

### 13.6 Two answers to the brief

**Way A: drop the missing hours.** Average what exists.
**Way B: repair the gaps, in a way that suits the cause.** For short gaps (up to 3 hours), interpolate along time within each station. For long gaps, leave them missing. Then, because the fog pattern is MAR, add humidity: predict the remaining missing readings from the same station's hour-of-day and humidity.

We compare both against the truth (only possible because the data are synthetic).

```python run
def mean_and_exceedance(d):
    return pd.DataFrame({"mean_pm25": d.groupby("station")["pm25"].mean(),
                         "pct_hours_over_60": d.groupby("station")["pm25"].apply(lambda s: (s.dropna() > LIMIT).mean() * 100)})


way_a = mean_and_exceedance(a4)

b = a4.copy().set_index("ts")
b["pm25"] = b.groupby("station")["pm25"].transform(lambda s: s.interpolate(method="time", limit=3, limit_area="inside"))
b = b.reset_index()
rest = b["pm25"].isna() & b["humidity"].notna()                      # remaining gaps where humidity is known
fitted = {}
for st, g in b[b["pm25"].notna()].groupby("station"):                # a line per station: pm25 ~ humidity
    slope, intercept = np.polyfit(g["humidity"], g["pm25"], 1)
    fitted[st] = (slope, intercept)
b.loc[rest, "pm25"] = [fitted[s][0] * h + fitted[s][1] for s, h in zip(b.loc[rest, "station"], b.loc[rest, "humidity"])]
b["pm25_filled"] = rest | (a4["pm25"].isna() & b["pm25"].notna())
way_b = mean_and_exceedance(b)

true_ans = mean_and_exceedance(air_truth)
final = pd.concat({"A drop": way_a, "B repair": way_b, "TRUTH": true_ans}, axis=1)
print(final.round(1).to_string())
print()
print("gap A - truth, mean :", (way_a["mean_pm25"] - true_ans["mean_pm25"]).round(1).to_dict())
print("gap B - truth, mean :", (way_b["mean_pm25"] - true_ans["mean_pm25"]).round(1).to_dict())
print("hours filled in B   :", int(b["pm25_filled"].sum()))
```
```text
             A drop                    B repair                       TRUTH                  
          mean_pm25 pct_hours_over_60 mean_pm25 pct_hours_over_60 mean_pm25 pct_hours_over_60
station                                                                                      
Airport       34.00              7.20     34.70              7.50     35.00              8.90
Central       54.20             40.50     55.10             43.30     55.50             43.70
Hill Road     68.30             62.70     69.30             65.20     69.90             65.10
Riverside     38.70             14.00     39.50             14.40     39.80             16.20

gap A - truth, mean : {'Airport': -1.0, 'Central': -1.3, 'Hill Road': -1.6, 'Riverside': -1.1}
gap B - truth, mean : {'Airport': -0.3, 'Central': -0.4, 'Hill Road': -0.6, 'Riverside': -0.3}
hours filled in B   : 445
```

Read the table.

- **The mean**: in all four stations, A is **1.0 to 1.6 µg/m³ too low**, because the foggy hours, the dusty ones, went missing. B cuts the gap to 0.3 to 0.6. A small number, but it always points the same way.
- **The question of the brief**, the share of hours over the limit, shows it more: at Central, A says 40.5 percent, B says 43.3, truth 43.7. At Hill Road A says 62.7 and the truth is 65.1. An average that is 2 percent off became a share that is nearly 3 points off, since the missing hours were exactly the high ones.
- **B is closer but not right**: the repair model uses only a line in humidity, and the Airport share (7.5 against 8.9) is still low. The 72-hour `Riverside` outage was repaired from humidity alone, a weak basis, because a line in humidity knows nothing about the hour of the day. The report must say so.

So the honest answer to the brief is not one number: "Central exceeds the limit about 40 to 44 percent of the hours, depending on how the foggy hours with failed sensors are treated; the true value is more likely near the upper end."

### 13.7 The cleaning report

The last deliverable is text. A colleague should be able to read it and know what was done, why, and what changed. Generate it from the log and the numbers, so it cannot disagree with the code.

```python run
def build_report(log, flags, answers_a, answers_b):
    lines = ["# Air quality: cleaning report", "", "### Steps"]
    for _, r in log.iterrows():
        lines.append(f"- **{r['step']}**: {r['rows_before']} -> {r['rows_after']} rows; "
                     f"missing cells {r['na_before']} -> {r['na_after']}. {r['note']}.")
    lines += ["", "### Why pm25 is missing (after cleaning)"]
    for k, v in flags.items():
        lines.append(f"- {k}: {v}")
    lines += ["", "### Missing-data decision",
              "Missingness depends on humidity (above 85 percent about half of the readings fail): MAR.",
              "Way A drops them. Way B interpolates gaps up to 3 hours, then predicts from humidity.",
              "", "### Result: mean PM2.5 (ug/m3) by station", "",
              "| station | A: drop | B: repair | difference |", "|---|---|---|---|"]
    for st in answers_a.index:
        a_, b_ = answers_a.loc[st, "mean_pm25"], answers_b.loc[st, "mean_pm25"]
        lines.append(f"| {st} | {a_:.1f} | {b_:.1f} | {b_ - a_:+.1f} |")
    return "\n".join(lines)


report = build_report(show_log(), a4["pm25_flag"].value_counts().to_dict(), way_a, way_b)
print(report)
```
```text
# Air quality: cleaning report

### Steps
- **1 formats**: 4360 -> 4360 rows; missing cells 272 -> 411. names, timestamps, -999 -> missing.
- **2 duplicates**: 4360 -> 4320 rows; missing cells 411 -> 405. same station + hour: first copy kept.
- **3 suspects**: 4320 -> 4320 rows; missing cells 405 -> 445. spikes and stuck runs -> missing, reason kept.

### Why pm25 is missing (after cleaning)
- ok: 3875
- missing: 267
- code: 138
- stuck: 33
- spike: 7

### Missing-data decision
Missingness depends on humidity (above 85 percent about half of the readings fail): MAR.
Way A drops them. Way B interpolates gaps up to 3 hours, then predicts from humidity.

### Result: mean PM2.5 (ug/m3) by station

| station | A: drop | B: repair | difference |
|---|---|---|---|
| Airport | 34.0 | 34.7 | +0.7 |
| Central | 54.2 | 55.1 | +0.9 |
| Hill Road | 68.3 | 69.3 | +1.0 |
| Riverside | 38.7 | 39.5 | +0.9 |
```

Writing is part of the cleaning. A report like this, plus the dictionary, the schema file and the code, is what makes your work something another person can trust and rerun: the pipeline is a **document in code**.

### 13.8 What to hand in

For your own public dataset, deliver this list:

1. `raw/` untouched, and `clean/` produced by one command.
2. `cleaning.py` with one function per step and a log.
3. `schema` (pandera) and a data dictionary in plain language.
4. `rejects` with a reason column (or a flag column, as above).
5. A missing-data section: how much, where, MCAR/MAR/MNAR, **two ways to answer**, and the gap.
6. A one-page report in plain words.
7. A test with a handful of rows you checked by hand (the substitute for our "truth").

## 14. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Missing values hidden behind codes (`-999`, `999`, `N/A`, `""`) | `isna()` says "no missing"; means are nonsense | list the codes, convert to real missing first (3.3) |
| `to_numeric(errors="coerce")` | unparseable values silently become `NaN` | use `raise` while building; count what coerce removed (3.2) |
| `to_datetime` on mixed formats | day and month swapped without any error | explicit formats, assert each row matched exactly one (3.4) |
| `dayfirst=True` on ISO dates | `2024-03-05` read as 3 May | parse each format separately (3.4) |
| `str.replace` and `regex=` | older code treated patterns as text | always write `regex=True` or `regex=False` (4.1) |
| `contains` against `fullmatch` | partial matches pass validation | use `fullmatch` to validate (4.1) |
| `str` methods and missing values | `object` returns `NaN`, pandas 3 `str` returns `False` | pass `na=` on purpose (4.1) |
| Unanchored phone regex | strips real digits | lookahead, and a test set of tricky inputs (4.2) |
| `duplicated` with `NaN` keys | missing keys count as duplicates of each other | filter or choose another key (5.3) |
| Unique ID but duplicate people | re-submissions with new IDs survive | choose the key from meaning, such as the email (5.3) |
| `drop_duplicates()` without `sort_values` | the survivor is arbitrary | sort first, state the rule (5.4) |
| z-score with many outliers | masking: outliers hide each other | robust z (median and MAD), look at the log scale (6.3) |
| IQR on skewed data | many false alarms | transform with `log10`, or use groups (6.3) |
| Winsorising to make the mean look right | honest values rewritten | fix proven errors only, compare what changed (6.5) |
| Outlier rule relative to the data | the limit moves with each batch | find the bound with statistics, then freeze it (12.4) |
| `x == np.nan` | always `False` | `isna()` (7.2) |
| Mean of the answered, called "the mean" | reports a value with no mention of 20 percent missing | report `count` next to every average (7.3) |
| `dropna()` on a wide table | nearly every row has some missing cell | measure first (7.4) |
| Filling with the mean | right mean, wrong spread, correlation and tail | group fill, random draw, or a model; check more than the mean (9.1) |
| `ffill` over a long gap | a broken sensor looks like a steady one | `limit=`, keep long gaps visible (7.5) |
| Treating all missing alike | structural missing filled, zero-sales days invented | find the reason first (8.5) |
| Assuming MCAR | dropping rows biases the result | profile the missing rate by other columns (8.4) |
| Believing the diagnostic proves MCAR | MNAR is invisible in the observed data | reason about how the data was collected (8.4) |
| Reporting one number after a fill | falsely precise | report a second method, or a sensitivity range (9.3, 9.6) |
| Weakening a schema rule until it passes | the problem is hidden | decide whether the data or the rule is wrong (11.8) |
| `drop_invalid_rows=True` | rows vanish with no reason | quarantine with a reason column (11.6) |
| CSV round trip | dtypes, leading zeros and dates are lost | keep the schema, validate after loading, or use Parquet (12.5) |
| A step that is not idempotent | cleaning twice changes the result | test it; never erase an earlier flag (12.4) |

A debugging habit for every cleaning surprise: print `df.shape` before and after the step, `df.isna().sum()` before and after, and a `value_counts()` of the column you touched. Most of the bugs in this chapter are visible in those three outputs.

## 15. Summary

- **Cleaning is analysis.** Keep the raw data untouched, log every step with row and missing counts, flag before you delete, and treat a missing value as information.
- **Audit first**: shape, dtypes, missing counts, distinct counts, `value_counts`, `describe`. The fake values (`999`, `-999`, `N/A`, empty text) hide in plain sight until you look.
- **Formats**: `strip`, `lower`/`title`, a written mapping table for typos; `to_numeric` with `raise` while you learn the dirt; parse dates with explicit formats and assert that every row matched exactly one; convert codes to real missing values; describe what *valid* looks like, not what invalid looks like.
- **Regex in pandas**: `contains`, `match`, `fullmatch`, `extract`, `extractall`, `replace(regex=True)`. Normalise first, then validate with `fullmatch`; use lookaheads carefully and test with tricky inputs.
- **Duplicates**: `duplicated` / `drop_duplicates` with `subset` and `keep`; look at the groups; remember that `NaN` equals `NaN` here; choose the key from the meaning; decide which copy survives by sorting first; fuzzy matching only suggests.
- **Outliers**: a rule only points at suspects. The z-score is fooled by masking; the robust z-score (median, MAD) and the log scale are safer for skewed data; domain rules are the clearest. Flag, fix proven errors, set the rest to missing, and be careful with winsorising.
- **Missing mechanics**: `NaN`, `None`, `NaT`, `pd.NA`; `isna` never `== nan`; nullable dtypes; aggregations skip missing values; measure missingness by column and by row before you choose `dropna`.
- **Why values are missing**: MCAR (a coin flip: dropping is safe but wasteful), MAR (depends on visible columns: bias that you can repair using them), MNAR (depends on the hidden value: bias the data alone cannot show or fix). MAR and MNAR can look alike in the diagnostics, so the reasoning about how the data was collected cannot be skipped.
- **Dropping or filling changes the answer.** Dropping and mean fill gave the same biased mean under MAR; mean fill also shrank the spread, the correlation and the tail even under MCAR; group fill, random draws and regression repaired MAR; nothing repaired MNAR. So report a **second method**, and under MNAR report a **range** (sensitivity analysis).
- **Validation**: write rules as code. By hand with a report table, or with **pandera**: `DataFrameSchema`, `Column`, `Check` (built-in, custom and cross-column), `nullable`, `coerce`, `strict`, `unique`, `lazy=True` and `failure_cases`, and the class style `DataFrameModel`. A schema documents the table and fails loudly; it cannot prove the data are true.
- **A pipeline you can trust**: small step functions in a sensible order (formats, duplicates, outliers, validate), a log, a quarantine with reasons, tests for idempotence and determinism, a frozen outlier bound, and four saved outputs (clean, rejects, log, schema).

You reached the outcome of this chapter: you can **show how two reasonable missing-data choices give two different answers**: you built the same dataset three times (MCAR, MAR, MNAR), cleaned it six reasonable ways, and watched the mean income move by almost 2,000 rupees, the share over 50,000 by 3.5 points, and the share of hours over the dust limit by nearly 3 points, depending only on what you did with the blanks. More importantly, you now know how to say which answer to trust and why, and how to write it down so that the reader can disagree. Next, da.06 asks what one row *means* (the grain of a table), how joins fan out, and how to define a metric so that two people get the same answer from the same data.
