pattern = input().strip()
words = input().split()

answer = "YES"
if len(pattern) != len(words):
    answer = "NO"
else:
    to_word = {}
    to_letter = {}
    for ch, w in zip(pattern, words):
        if to_word.get(ch, w) != w or to_letter.get(w, ch) != ch:
            answer = "NO"
            break
        to_word[ch] = w
        to_letter[w] = ch
print(answer)
