# Same summary, different data

Chapter section 15. Four datasets of 20 values each have the **same mean (50.0) and the same standard deviation (10.0)** to one decimal. Each `#` is one value; the bins are 5 wide.

Dataset A (20 values): mean 50.0, standard deviation 10.0

```text
 25 to <30  | #
 30 to <35  | 
 35 to <40  | ##
 40 to <45  | ###
 45 to <50  | ####
 50 to <55  | ####
 55 to <60  | ###
 60 to <65  | ##
 65 to <70  | 
 70 to <75  | #
 75 to <80  | 
 80 to <85  | 
 85 to <90  | 
 90 to <95  | 
 95 to <100 | 
```

Dataset B (20 values): mean 50.0, standard deviation 10.0

```text
 25 to <30  | 
 30 to <35  | 
 35 to <40  | ####
 40 to <45  | ######
 45 to <50  | 
 50 to <55  | 
 55 to <60  | ####
 60 to <65  | ######
 65 to <70  | 
 70 to <75  | 
 75 to <80  | 
 80 to <85  | 
 85 to <90  | 
 90 to <95  | 
 95 to <100 | 
```

Dataset C (20 values): mean 50.0, standard deviation 10.0

```text
 25 to <30  | 
 30 to <35  | 
 35 to <40  | 
 40 to <45  | 
 45 to <50  | ###################
 50 to <55  | 
 55 to <60  | 
 60 to <65  | 
 65 to <70  | 
 70 to <75  | 
 75 to <80  | 
 80 to <85  | 
 85 to <90  | 
 90 to <95  | #
 95 to <100 | 
```

Dataset D (20 values): mean 50.0, standard deviation 10.0

```text
 25 to <30  | 
 30 to <35  | 
 35 to <40  | #
 40 to <45  | #######
 45 to <50  | ####
 50 to <55  | ###
 55 to <60  | ##
 60 to <65  | #
 65 to <70  | #
 70 to <75  | 
 75 to <80  | #
 80 to <85  | 
 85 to <90  | 
 90 to <95  | 
 95 to <100 | 
```

In `answer.md` write about 250 to 400 words:

1. For each dataset, say in one sentence what the picture shows that "mean 50, sd 10" does not.
2. Explain why mean and standard deviation alone cannot tell these apart.
3. Name **extra numbers** that would separate them (for example the median, quartiles, minimum and maximum, skewness) and say which dataset each would expose.
4. Say what you should do **before** trusting a summary.
5. Add one sentence about the *averaging averages* trap: why the mean of group means is not always the overall mean.

Use the words *shape*, *bimodal*, *outlier*, *plot first*, *five-number summary*.

## Example

"Dataset B has two clusters, one near 40 and one near 60, and almost nobody near 50: the mean of 50 describes a place where no value lives."
