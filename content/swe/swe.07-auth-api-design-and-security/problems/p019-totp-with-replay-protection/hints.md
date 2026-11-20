## Hint 1

For `hotp`: which standard-library function builds an HMAC? What type must the counter be before it is hashed (8 bytes)? Which `struct` format code means "unsigned 64-bit, big-endian"?

## Hint 2

"Dynamic truncation" means: the last byte of the MAC chooses where to read. Read 4 bytes there, turn them into an integer, and clear the top bit so the number is never negative. Then keep the last `digits` decimal digits, and think about what to do when the number is small (leading zeros). For `verify_totp`, which slots do you try, and what is the one extra condition besides "the code matches"?

## Hint 3

```text
hotp:  mac = hmac_sha1(key, pack(">Q", counter))
       o = mac[-1] & 0x0F
       n = unpack(">I", mac[o:o+4]) & 0x7FFFFFFF
       return str(n % 10**digits).zfill(digits)
totp:  hotp(key, int(at) // step, digits)
verify: if code is not 6 ASCII digits: None
        cur = int(now) // 30
        for s in cur-1, cur, cur+1:
            if s > last_step and compare_digest(hotp(key, s), code): return s
        None
```
