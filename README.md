# litter-robot-monitor

Polls your Litter-Robot (via [pylitterbot](https://github.com/natekspencer/pylitterbot))
and texts you (via your carrier's email-to-SMS gateway) when:

- the waste drawer is almost full, or
- the litter level is running low (Litter-Robot 4 only — LR3 doesn't report this)

## Setup

1. Create a virtualenv and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in:
   - Your Whisker/Litter-Robot app username + password
   - An SMTP account to send from (`SMTP_USERNAME` / `SMTP_PASSWORD`). For
     Gmail, generate an [App Password](https://myaccount.google.com/apppasswords) —
     your regular Google password won't work over SMTP.
   - `SMS_GATEWAY_ADDRESS` — your phone number `@` your carrier's SMS
     gateway domain. Common ones:

     | Carrier | Gateway domain |
     |---|---|
     | Verizon | `vtext.com` |
     | AT&T | `txt.att.net` |
     | T-Mobile | `tmomail.net` |
     | Sprint | `messaging.sprintpcs.com` |
     | Google Fi | `msg.fi.google.com` |

     e.g. `5551234567@vtext.com`
   - Optionally tweak the polling interval and alert thresholds

   ```bash
   cp .env.example .env
   ```

   Note: this sends to your phone's own carrier gateway directly (not
   through Google Voice — Google Voice has no API for sending texts
   programmatically). Delivery is usually fast but not guaranteed instant,
   and some carriers occasionally rate-limit or filter gateway email.

3. Run it:

   ```bash
   python main.py
   ```

   It polls on a loop (`POLL_INTERVAL_MINUTES`, default 15) and sends one
   text when a threshold is crossed. It won't text again for the same
   condition until the reading recovers past the threshold by
   `ALERT_HYSTERESIS` percentage points (avoids repeat texts while a value
   hovers right at the line). Alert state is persisted to `data/state.json`
   so restarts don't re-fire alerts that already went out.

## Running it continuously (macOS)

An example `launchd` job is included as `com.litterrobot.monitor.plist.example`.
To use it:

```bash
cp com.litterrobot.monitor.plist.example ~/Library/LaunchAgents/com.litterrobot.monitor.plist
# edit the copied file if your repo path or Python version differs
launchctl load ~/Library/LaunchAgents/com.litterrobot.monitor.plist
```

Logs go to `data/monitor.log` / `data/monitor.err.log`. To stop it:

```bash
launchctl unload ~/Library/LaunchAgents/com.litterrobot.monitor.plist
```

## Notes

- Litter-Robot 3 only exposes waste drawer level (no litter/globe level), so
  only the "drawer full" alert applies to it.
- Litter-Robot 4 exposes both waste drawer level and litter (hopper) level.
