import pytest

from solution import join_command, parse_settings, split_command


@pytest.mark.parametrize("line, expected, why", [
    ('cp "my notes.txt" backup/', ["cp", "my notes.txt", "backup/"], "Double quotes keep a file name with a space as ONE argument; the quotes are removed."),
    ("grep -n 'def main' app.py", ["grep", "-n", "def main", "app.py"], "Single quotes group words too."),
    ('say "it\'s fine"', ["say", "it's fine"], "A ' inside double quotes is an ordinary character."),
    ("  ls   -l  ", ["ls", "-l"], "Extra spaces between and around words are ignored."),
    ("", [], "An empty line gives no arguments."),
])
def test_split_command_quotes(line, expected, why):
    assert split_command(line) == expected, why + " str.split() knows nothing about quotes: use shlex.split."


def test_split_command_comments():
    assert split_command("echo hi # say hello") == ["echo", "hi"], "An unquoted # starts a comment: shlex.split(line, comments=True)."
    assert split_command('echo "a # b"') == ["echo", "a # b"], "A # inside quotes is just a character, not a comment."
    assert split_command("# only a comment") == [], "A line that is only a comment gives no arguments."


def test_split_command_unbalanced_quote():
    with pytest.raises(ValueError):
        split_command('echo "oops')
    # shlex raises ValueError("No closing quotation"); let it propagate


@pytest.mark.parametrize("args", [
    ["cp", "my notes.txt", "backup/"],
    ["echo", "it's"],
    ["rm", "-rf", "x; rm -rf ~"],
    ["printf", ""],
    ["ls", "$HOME", "*.py"],
])
def test_join_round_trip(args):
    line = join_command(args)
    assert isinstance(line, str), "join_command returns one string."
    assert split_command(line) == args, (
        f"join_command({args!r}) gave {line!r}, which splits back into something else. ' '.join() does not quote; "
        "shlex.join quotes every argument that needs it, so spaces, quotes, ; $ * and empty strings survive."
    )


def test_join_exact_forms():
    assert join_command(["cp", "my notes.txt", "backup/"]) == "cp 'my notes.txt' backup/", "shlex.join puts single quotes only where needed."
    assert join_command(["plain", "words"]) == "plain words", "Simple words are not quoted."
    assert join_command(["rm", "x; rm -rf ~"]) == "rm 'x; rm -rf ~'", "Quoting stops a shell from running the second command."


def test_parse_settings():
    got = parse_settings('name="Kavya B" city=Delhi  empty= url=a=b # a comment')
    assert got == {"name": "Kavya B", "city": "Delhi", "empty": "", "url": "a=b"}, (
        "Split with shlex (quotes, comments), then split each token at the FIRST '=' only (partition): "
        "'url=a=b' has the value 'a=b', and 'empty=' has the value ''."
    )


def test_parse_settings_order_and_duplicates():
    got = parse_settings("b=1 a=2 b=3")
    assert got == {"b": "3", "a": "2"} and list(got) == ["b", "a"], "A later value for the same key wins; keys keep first-seen order (normal dict)."


@pytest.mark.parametrize("bad", ["name", "=value", 'ok=1 broken'])
def test_parse_settings_rejects_bad_tokens(bad):
    with pytest.raises(ValueError):
        parse_settings(bad)
    # every token must look like key=value with a non-empty key
