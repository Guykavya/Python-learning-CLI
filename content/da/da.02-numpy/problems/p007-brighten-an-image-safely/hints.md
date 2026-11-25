## Hint 1

`uint8` arithmetic wraps before you ever get a chance to clip. Into which dtype can you convert the image first so that 250 + 255 and 0 − 255 both fit?

## Hint 2

```text
wide = img.astype(np.int16)        # -32768 .. 32767: room for the sum
wide = wide + delta                # no wrap
wide = np.clip(wide, 0, 255)       # back into the pixel range
return wide.astype(np.uint8)       # the image type again
```
