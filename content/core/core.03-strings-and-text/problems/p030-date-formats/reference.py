y, m, d = input().strip().split("-")
y, m, d = int(y), int(m), int(d)
months = "JanFebMarAprMayJunJulAugSepOctNovDec"
print(f"{d:02}/{m:02}/{y}")
print(f"{d} {months[3 * (m - 1):3 * m]} {y}")
print(f"{y}{m:02}{d:02}")
