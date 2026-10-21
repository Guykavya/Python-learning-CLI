while True:
    line = input().strip()
    if line == "end":
        break
    valid = False
    match line.lower().split():
        case [time_text]:
            suffix = ""
        case [time_text, ("am" | "pm") as suffix]:
            pass
        case _:
            time_text = ""
            suffix = ""
    match time_text.split(":"):
        case [h, m]:
            s = "00"
        case [h, m, s]:
            pass
        case _:
            h = m = s = ""
    if (h.isdigit() and m.isdigit() and s.isdigit()
            and 1 <= len(h) <= 2 and len(m) == 2 and len(s) == 2):
        hour, minute, second = int(h), int(m), int(s)
        if suffix:
            hour_ok = 1 <= hour <= 12
            hour = hour % 12 + (12 if suffix == "pm" else 0)
        else:
            hour_ok = hour <= 23
        valid = hour_ok and minute < 60 and second < 60
    if valid:
        total = hour * 3600 + minute * 60 + second
        print(f"{hour:02d}:{minute:02d}:{second:02d} = {total} s")
    else:
        print(f"invalid: {line}")
