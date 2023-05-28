## HTML form attacks (and defences)

Introducing a set of scenarios of how a simple HTML form with a PIN can be attacked and defended.

The form template is the same for all scenarios/levels, and visible under [`index.html`](templates/index.html). Each level is inputting a specific security settings into this template.

The server implementation for all levels can be seed under [`app.py`](app.py).

[`solver.py`](solver.py) includes examples of how to attack the form in each level.

### Level 0 (plaintext GET)

The form uses plaintext `GET` HTTP request to send the `PIN` to the server. Because of this, the `PIN` is visible in the URL bar and transmitted unsecurely over the network. This gives an attacker an easy way to start brute-forcing the PIN easily or intercepting the PIN in the network.

### Level 1 (POST)

Form already uses `POST` HTTP request to send the `PIN`. This is already better because attacker needs to construct the `POST` request in some "more advanced" way. However, still trivial to brute-force.

### Level 2 (CSRF token)

Introducing `CSRF` token to the form. This makes it harder for the attacker to construct the `POST` request, as they need a valid token for each request. When they do not supply it, even a valid `PIN` will not be accepted by the server.

### Level 3 (session_id cookie)

Using the same `HTML` code as `level 2`, but with the difference of sending the `session_id` with each request as a `cookie`, and pairing the tokens with the session. This way, the attacker must also send cookies with each request, which makes the attack little bit harder to carry out.

---

### Other possible defences

- Rate limiting
  - do not allow for more than X PIN attempts per Y time period
- Captcha
  - require the user to solve a browser captcha before submitting the form repeatedly
- IP address whitelisting
  - allowing to access the form only from specific IP addresses
- Progressive delays
  - when inputting a bad PIN, the server will wait for some time period before responding
  - this delay can be increased with each bad PIN input 
  