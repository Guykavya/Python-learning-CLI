text = input()
data = text.encode("utf-8")
text_rev = text[::-1]
bytes_rev = data[::-1].decode("utf-8", errors="replace")
print(f"Hex: {data.hex(' ')}")
print(f"Bytes: {len(data)}")
print(f"Text reversed: {text_rev}")
print(f"Bytes reversed: {bytes_rev}")
print(f"Same: {text_rev == bytes_rev}")
