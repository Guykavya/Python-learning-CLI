# Palindrome phrases

A phrase is a palindrome if it reads the same backwards **after** removing spaces and punctuation and ignoring case. "Was it a car or a cat I saw?" is one.

Read a phrase and print:

```
Cleaned: <the phrase casefolded, with all ASCII punctuation and all whitespace removed>
Palindrome: <True or False>
```

**Example**

Input:
```
Was it a car or a cat I saw?
```
Output:
```
Cleaned: wasitacaroracatisaw
Palindrome: True
```

An empty phrase (or one that is only punctuation) cleans to an empty string, which counts as a palindrome.
