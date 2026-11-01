# inventory.py -- the warehouse team's script. It works, nobody likes touching it.
import sys
from datetime import date

PATH = "/home/you/inventory.csv"
DATA = []
BAD = []
LOW = 5


def go():
    global DATA, BAD
    path = PATH
    if len(sys.argv) > 1:
        path = sys.argv[1]
    try:
        f = open(path)
    except OSError:
        print("error: cannot open " + path)
        return
    text = f.read()
    f.close()
    n = 0
    for line in text.splitlines():
        n = n + 1
        line = line.strip()
        if line == "":
            continue
        if n == 1 and line.lower().startswith("sku"):
            continue
        p = [x.strip() for x in line.split(",")]
        if len(p) != 5:
            BAD.append(n)
            continue
        try:
            q = int(p[2])
            pr = float(p[3])
            if p[4] != "":
                e = date.fromisoformat(p[4])
            else:
                e = None
        except ValueError:
            BAD.append(n)
            continue
        if q < 0 or pr < 0:
            BAD.append(n)
            continue
        DATA.append([p[0], p[1], q, pr, e])
    print("loaded " + str(len(DATA)) + " records")
    if len(BAD) > 0:
        print("skipped " + str(len(BAD)) + " bad line(s): " + ", ".join([str(b) for b in BAD]))
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        line = line.strip()
        if line == "":
            continue
        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd == "quit" or cmd == "exit":
            print("bye")
            break
        elif cmd == "list":
            if len(DATA) == 0:
                print("no records")
            for r in sorted(DATA, key=lambda r: r[0]):
                print("%-6s %-12s %4d %8.2f" % (r[0], r[1], r[2], r[3]))
        elif cmd == "low":
            limit = LOW
            if len(args) > 0:
                try:
                    limit = int(args[0])
                except ValueError:
                    print("error: low needs a whole number")
                    continue
            found = [r for r in DATA if r[2] < limit]
            if len(found) == 0:
                print("nothing low on stock")
            for r in sorted(found, key=lambda r: (r[2], r[0])):
                print("%-6s %-12s %4d %8.2f" % (r[0], r[1], r[2], r[3]))
        elif cmd == "expired":
            t = date.today()
            found = [r for r in DATA if r[4] is not None and r[4] < t]
            if len(found) == 0:
                print("nothing expired")
            for r in sorted(found, key=lambda r: (r[4], r[0])):
                print("%-6s %-12s expired %s" % (r[0], r[1], r[4].isoformat()))
        elif cmd == "value":
            total = 0
            for r in DATA:
                total = total + r[2] * r[3]
            print("total value: %.2f" % total)
        elif cmd == "find":
            text = " ".join(args).lower()
            if text == "":
                print("error: find needs some text")
                continue
            found = [r for r in DATA if text in r[1].lower()]
            if len(found) == 0:
                print("no match")
            for r in sorted(found, key=lambda r: r[0]):
                print("%-6s %-12s %4d %8.2f" % (r[0], r[1], r[2], r[3]))
        elif cmd == "report":
            t = date.today()
            units = 0
            value = 0
            for r in DATA:
                units = units + r[2]
                value = value + r[2] * r[3]
            print("INVENTORY REPORT " + t.isoformat())
            print("items: %d  units: %d  value: %.2f" % (len(DATA), units, value))
            low = sorted([r[0] for r in DATA if r[2] < LOW])
            if len(low) == 0:
                print("low stock (<%d): none" % LOW)
            else:
                print("low stock (<%d): %s" % (LOW, ", ".join(low)))
            exp = sorted([r[0] for r in DATA if r[4] is not None and r[4] < t])
            if len(exp) == 0:
                print("expired: none")
            else:
                print("expired: " + ", ".join(exp))
            if len(DATA) == 0:
                print("most valuable: none")
            else:
                best = sorted(DATA, key=lambda r: (-(r[2] * r[3]), r[0]))[0]
                print("most valuable: %s %s (%.2f)" % (best[0], best[1], best[2] * best[3]))
        elif cmd == "help":
            print("commands: expired, find, help, list, low, quit, report, value")
        else:
            print("unknown command: " + cmd + " (try help)")


if __name__ == "__main__":
    go()
