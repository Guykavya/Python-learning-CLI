- **Dividing by 8 in line 3.** `mean` skips missing values: it divides by the number of values that are present (6).
- **Averaging the median by hand with the wrong pair.** For 8 sorted values the middle pair is the 4th and 5th; for 6
  values it is the 3rd and 4th. Sort first.
- **Writing `25` instead of `25.0` in the list.** A column with a missing value is `float64` and prints floats.
- **Writing `None` instead of `nan`.** A missing value in a float column prints as `nan`.
- **Forgetting that `age.max()` is read from the original Series on line 5.** It is still 999; `clean` is a new Series.
