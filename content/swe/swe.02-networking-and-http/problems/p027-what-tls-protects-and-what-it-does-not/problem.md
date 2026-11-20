# What TLS protects, and what it does not

Chapter section 17. A friend says: "I use HTTPS, so nobody can see anything I do online, and if the browser shows a certificate warning I just click *continue*."

In `answer.md` (10 to 16 sentences), correct and complete this statement:

1. Which parts of a request and response does TLS **hide** from someone watching the network (for example on public Wi-Fi)? Give at least four.
2. Which parts can that observer **still see**? Give at least four.
3. What two things does a TLS **certificate** prove, and what does it **not** prove?
4. Why is clicking through a certificate warning, or using `verify=False` in `requests`/`httpx`, dangerous? What kind of attacker does it allow?
5. A server has a valid certificate, but the **client** logs the full URL with the query string (`?token=...`) in its log files. Which part of the protection is lost, and why?
