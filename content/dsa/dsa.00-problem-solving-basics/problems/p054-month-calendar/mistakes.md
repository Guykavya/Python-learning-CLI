- Converting Zeller's result directly as if 0 were Monday. Zeller's 0 is Saturday, so every month
  is shifted by two columns. Check the conversion on a month whose first day you know.
- Printing each cell with `print(..., end=" ")`. That leaves a space at the end of every line and
  breaks the "no trailing spaces" rule.
- Printing an extra empty line when the month ends on a Sunday. After a full week the line is
  already printed and reset; printing it again at the end gives a blank line.
- Forgetting to move January and February into the previous year in Zeller's formula. Only those
  two months come out wrong, which is easy to miss if you test only May.
