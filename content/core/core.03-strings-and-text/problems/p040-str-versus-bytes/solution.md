See the model answer shown when you check. The ideas that must appear:

1. `str` is a sequence of Unicode code points (text); `bytes` is a sequence of integers 0 to 255 (raw data). `encode` goes str to bytes using an encoding; `decode` goes bytes to str.
2. UTF-8 is variable length: `é` takes 2 bytes.
3. The message names the codec, the bad byte, its position and the reason.
4. Decode with the encoding that was actually used (`cp1252` or `latin-1`); `ignore` silently deletes letters from names.
5. Mojibake: decoding bytes with the wrong encoding without an error, giving text like `cafÃ©`.
