## Model answer

**1. What TLS hides.** The request line and **path**, the **query string**, all **headers** (including `Cookie` and `Authorization`), the **request and response bodies**, and the status code. An observer sees only encrypted bytes.

**2. What stays visible.** The **IP address** of the server, the **host name** (it is in the DNS lookup unless that is encrypted, and in the **SNI** field of the TLS handshake), the **port**, the **amount of data** and the **timing** of the packets (which can reveal which page was loaded), and the fact that you talked to this server at that time.

**3. What a certificate proves.** (a) The server has the **private key** matching the public key in the certificate; (b) a **certificate authority** that the client trusts has signed that this key belongs to this **host name** (and the dates are valid). It does **not** prove that the site is honest, safe, or what it claims to be: a phishing site can have a perfectly valid certificate for its own name.

**4. Why skipping verification is dangerous.** TLS without certificate checking still encrypts, but it encrypts to **whoever answers**. A **man in the middle** (an attacker on the same Wi-Fi, a malicious router) can present their own certificate, read and change everything, and forward it to the real server. `verify=False` removes exactly the check that stops this; the warning page is the browser telling you it cannot tell. It is acceptable only for a test server you control, never for real data.

**5. Logging the URL.** TLS protects the data **in transit**. Once the client writes `?token=...` into a log file, the secret sits in plain text on disk (and in log shipping tools), where anyone with access to the logs can read it. Secrets belong in headers or bodies, never in URLs, and should be redacted in logs. Browser history and `Referer` headers also copy URLs.

**Checklist: your answer should mention**
- [ ] path, query, headers, cookies, body are **hidden**
- [ ] IP address, **host name (SNI/DNS)**, size and timing are **visible**
- [ ] a certificate proves **key ownership for a name, signed by a trusted CA**, not honesty
- [ ] `verify=False` allows a **man-in-the-middle** (encrypts to anyone)
- [ ] secrets in URLs leak through **logs, history, Referer**
