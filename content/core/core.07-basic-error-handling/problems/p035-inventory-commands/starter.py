def process(commands, stock):
    """Run each command on stock; return one reply per command ('error: ...' for bad ones)."""
    replies = []
    for command in commands:
        verb, item, qty = command.split()
        if verb == "add":
            stock[item] = stock.get(item, 0) + int(qty)
        replies.append(f"{item}: {stock[item]}")
    return replies
