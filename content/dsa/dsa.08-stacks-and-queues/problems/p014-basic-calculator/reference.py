def trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def calculate(s):
    s = s.replace(" ", "")

    def parse(i):
        stack = []
        number = 0
        op = "+"
        while True:
            ch = s[i] if i < len(s) else ")"
            if ch.isdigit():
                number = number * 10 + int(ch)
            elif ch == "(":
                number, i = parse(i + 1)
            else:
                if op == "+":
                    stack.append(number)
                elif op == "-":
                    stack.append(-number)
                elif op == "*":
                    stack.append(stack.pop() * number)
                else:
                    stack.append(trunc_div(stack.pop(), number))
                if ch == ")":
                    return sum(stack), i
                op = ch
                number = 0
            i += 1

    value, _ = parse(0)
    return value
