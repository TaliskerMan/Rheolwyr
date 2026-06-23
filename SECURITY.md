# Security Policy

## The capability Rheolwyr requires (read this first)

Rheolwyr is a text expander: to detect triggers it must **read your keystrokes
globally**. On Wayland this is done by reading `/dev/input/event*` via `evdev`,
which requires your user account to be a member of the **`input` group**.

**What `input`-group membership grants:** read access to *all* input event
devices. That means the account can read **every keystroke from every
application** — passwords, messages, anything you type — and on a shared machine
potentially other users' input as well. This access is **system-wide and
permanent**: it applies to the whole account at all times, not only while
Rheolwyr is running, and it persists until you remove yourself from the group.

This is inherent to any evdev-based expander; it is not specific to a bug in
Rheolwyr. We disclose it plainly because the trust model of this tool *is* "it
can see everything you type."

**What Rheolwyr does to limit exposure:** it does **not** record or log
keystrokes. The match buffer is held in memory, capped at 50 characters, and
discarded; expanded snippet content is never written to logs.

**Joining the group is an informed opt-in.** The package does not add you to the
`input` group automatically. You enable expansion yourself:

```bash
sudo usermod -aG input,uinput "$USER"   # then log out and back in
```

### Least-privilege alternatives

If you are not comfortable making your login account permanently
keylog-capable, consider:

- **A dedicated service user.** Run the listener as a separate, minimal user
  that is in the `input`/`uinput` groups, instead of your interactive login
  account, so your normal account never gains the capability.
- **Device scoping with udev.** Grant read access only to your specific
  keyboard's `event*` node (matched by vendor/product in a udev rule) rather
  than the whole `input` group, narrowing the exposure to one device.
- **X11 only.** On X11 the injection path uses `pynput`/XTest and does not
  require `input`-group membership (the security trade-offs of X11 input access
  are different, but the `input`-group grant is avoided).

These are documented as options; the default `.deb` flow uses the `input` group
for simplicity, and asks you to opt in explicitly.

## Supported Versions

Only the latest release of Rheolwyr is supported with security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in Rheolwyr, please report it by email
to Chuck Talk <chuck@nordheim.online>. Please do not report security
vulnerabilities through public GitHub issues. All reports will be addressed
promptly.
