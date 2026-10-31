from solution import tags


def test_example():
    result = tags("Loving #Python and #regex! cc @kavya_b, @Ravi #python")
    assert result == {"hashtags": ["python", "regex"], "mentions": ["kavya_b", "Ravi"]}, (
        "Hashtags lower-cased and de-duplicated, mentions as written, both in first-seen order. "
        f"Got {result!r}."
    )


def test_both_keys_always_present():
    assert tags("") == {"hashtags": [], "mentions": []}, "Always return both keys, each with a list, even for empty text."
    assert tags("plain words") == {"hashtags": [], "mentions": []}, "No tags: both lists empty."


def test_without_symbol():
    assert tags("#one @two") == {"hashtags": ["one"], "mentions": ["two"]}, "Return the name WITHOUT # or @: capture only the \\w+ part in a group."


def test_tag_ends_at_non_word_char():
    result = tags("#python! #re.sub @ana's (#x)")
    assert result["hashtags"] == ["python", "re", "x"], "A tag stops at the first non-word character: '#re.sub' is 're'. '(#x)' after a bracket is a tag."
    assert result["mentions"] == ["ana"], "'@ana's' is the mention 'ana': the apostrophe ends it."


def test_email_is_not_a_mention():
    result = tags("mail kavya@example.com or @admin")
    assert result["mentions"] == ["admin"], "In 'kavya@example.com' the @ comes straight after a word character: not a mention. Use \\B before @ (or a lookbehind (?<!\\w))."


def test_glued_hash_is_not_a_tag():
    result = tags("C#9 and a#b but #ok")
    assert result["hashtags"] == ["ok"], "'C#9' and 'a#b': # right after a word character is not a hashtag."


def test_lone_symbols():
    assert tags("# @ #! @.") == {"hashtags": [], "mentions": []}, "A # or @ with no word characters after it is not a tag: use \\w+ (one or more), not \\w*."


def test_hashtag_case_and_dedupe():
    result = tags("#AI #ai #Ai #ml #AI")
    assert result["hashtags"] == ["ai", "ml"], "Hashtags ignore case: lower-case them, then keep only the first of each, in order."


def test_mentions_keep_case():
    result = tags("@Ana @ana @Ana")
    assert result["mentions"] == ["Ana", "ana"], "Mentions keep their case: @Ana and @ana are different users. Remove only exact repeats."


def test_order_is_first_seen():
    result = tags("#zeta #alpha #zeta #mid")
    assert result["hashtags"] == ["zeta", "alpha", "mid"], "Keep first-seen order. Do not sort, and note that set() loses the order."


def test_digits_and_underscore():
    result = tags("#2024 #web_dev @user_42")
    assert result == {"hashtags": ["2024", "web_dev"], "mentions": ["user_42"]}, "Digits and _ are word characters, so they are part of the tag."


def test_start_of_text_and_newlines():
    result = tags("#first\n@second\n#third")
    assert result == {"hashtags": ["first", "third"], "mentions": ["second"]}, "A tag at the very start or right after a newline counts."
