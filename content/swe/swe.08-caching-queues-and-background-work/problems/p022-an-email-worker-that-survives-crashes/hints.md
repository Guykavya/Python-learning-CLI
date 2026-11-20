## Hint 1

Go through the crash points one at a time and ask: "after this crash, the job runs again **from the start**; what will the second run see, and what will it do?" Which crash can produce a second e-mail even when you keep a log? (Look at the window between `send` and recording `sent`.)

## Hint 2

The log alone cannot close the window between "sent" and "recorded sent": only the provider knows. So give the provider something stable to recognise. Which value is the same for the retry of a job **and** for a duplicate job of the same e-mail?

```text
key = "welcome:" + user_id
crash.hit("start")
if log[key] == "sent": return
INSERT OR IGNORE log(key, to, 'sending')
crash.hit("after-claim")
message_id = provider.send(to, "Welcome!", "Hello and welcome.", idempotency_key=key)
crash.hit("after-send")
UPDATE log SET state='sent', provider_id=message_id WHERE key=key
crash.hit("after-record")
```
