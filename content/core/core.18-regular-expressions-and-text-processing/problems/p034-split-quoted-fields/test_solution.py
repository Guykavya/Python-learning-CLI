from solution import split_fields


def test_plain_fields():
    assert split_fields("a,b,c") == ["a", "b", "c"], "Simple fields separated by commas."


def test_one_field():
    assert split_fields("hello") == ["hello"], "No comma: one field."


def test_quoted_field_with_comma():
    assert split_fields('"Delhi, India",42') == ["Delhi, India", "42"], "A comma inside quotes belongs to the field. Try the quoted alternative first: \"([^\"]*)\"."


def test_quotes_removed():
    assert split_fields('"a","b"') == ["a", "b"], "The surrounding quotes are not part of the value: return the group inside them."


def test_spaces_around_unquoted_stripped():
    assert split_fields(" x , y ") == ["x", "y"], "Spaces around an unquoted field are dropped. A lazy [^,]*? followed by \\s* lets the trailing spaces fall outside the group."


def test_spaces_inside_quotes_kept():
    assert split_fields('  "  padded  "  ,z') == ["  padded  ", "z"], "Spaces INSIDE the quotes are kept; only those outside are ignored."


def test_empty_fields_kept():
    assert split_fields("a,,b") == ["a", "", "b"], "Two commas in a row mean an empty field between them."
    assert split_fields("a,") == ["a", ""], "A trailing comma means one more, empty, field."
    assert split_fields(",a") == ["", "a"], "A leading comma means the first field is empty."


def test_empty_line():
    assert split_fields("") == [""], "An empty line still has one (empty) field, like ''.split(',') == ['']."


def test_empty_quoted_field():
    assert split_fields('"",x') == ["", "x"], "\"\" is an empty quoted field. Use * not + inside the quotes."


def test_doubled_quotes():
    assert split_fields('"say ""hi""",2') == ['say "hi"', "2"], "Inside quotes, \"\" means one \". Allow (?:[^\"]|\"\")* inside, then replace '\"\"' with '\"' in the value."


def test_mixed_line():
    line = 'id, "Kumar, Ravi" ,  ,"",  "x,y,z" ,last'
    assert split_fields(line) == ["id", "Kumar, Ravi", "", "", "x,y,z", "last"], "Mix of plain, quoted, blank and empty quoted fields. Count the commas: 6 fields."


def test_no_extra_empty_field_at_end():
    assert len(split_fields("a,b")) == 2, "Do not produce an extra empty field after the last one. A pattern that can match the empty string at the end of the line (with finditer) adds one: start each field with (?:^|,)."
