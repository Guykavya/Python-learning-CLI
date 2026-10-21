players = []
for _ in range(int(input())):
    name, score = input().split()
    players.append((-int(score), name))
players.sort()
rank_of = {}
for i, (neg, name) in enumerate(players, start=1):
    if neg not in rank_of:
        rank_of[neg] = i
    print(f"{rank_of[neg]}. {name} {-neg}")
print("Distinct scores:", len(rank_of))
