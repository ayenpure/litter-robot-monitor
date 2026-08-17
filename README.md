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

## Running it in Docker (e.g. on a Raspberry Pi)

A `Dockerfile` and `docker-compose.yml` are included. This runs well on a Pi
4/5 on 64-bit Raspberry Pi OS — the base image and all dependencies have
prebuilt `linux/arm64` wheels, so no compiler/build step is needed.

1. Copy the repo to the Pi (`git clone`/`scp`/etc.), with your filled-in
   `.env` alongside it (it's gitignored, so copy it separately).

2. Build and run:

   ```bash
   docker compose up -d --build
   ```

   This builds the image, starts the container in the background with
   `restart: unless-stopped` (so it survives reboots and crashes), and
   mounts `./data` into the container so `data/state.json` (alert state)
   persists across restarts.

3. Check logs / stop it:

   ```bash
   docker compose logs -f
   docker compose down
   ```

If you're building on a different machine (e.g. this Mac) and pushing to
the Pi instead of building on-device, cross-build for arm64 with:

```bash
docker buildx build --platform linux/arm64 -t litter-robot-monitor .
```

(32-bit Raspberry Pi OS uses `armv7` — swap the platform flag to
`linux/arm/v7` if that's what you're running; wheel availability for that
architecture is spottier, so a build failure there may need
`build-essential` added to the `Dockerfile`.)

## Running it with Podman (lighter-weight alternative to Docker)

Podman has no persistent background daemon and runs rootless by default,
which makes it a lighter footprint on a storage/RAM-constrained Pi than
Docker Engine. The same `Dockerfile` works unchanged.

1. Copy the repo + your filled-in `.env` to the Pi, same as the Docker flow.

2. Build the image:

   ```bash
   podman build -t litter-robot-monitor .
   mkdir -p data
   ```

3. Run the smoke test first (see below) to confirm the image, credentials,
   and gateway all actually work before leaving it running unattended.

4. Set it up as a persistent, boot-surviving service via systemd (plain
   `podman run --restart` doesn't survive a reboot on its own — it needs a
   systemd unit to relaunch it):

   ```bash
   podman create --name litter-robot-monitor \
     --env-file .env \
     -v ./data:/app/data \
     litter-robot-monitor

   mkdir -p ~/.config/systemd/user
   podman generate systemd --name litter-robot-monitor --files --restart-policy=always
   mv container-litter-robot-monitor.service ~/.config/systemd/user/

   systemctl --user daemon-reload
   systemctl --user enable --now container-litter-robot-monitor.service

   # lets the user service start on boot even before you log in
   loginctl enable-linger "$(whoami)"
   ```

5. Check logs / stop it:

   ```bash
   journalctl --user -u container-litter-robot-monitor.service -f
   systemctl --user stop container-litter-robot-monitor.service
   ```

   To pick up code changes later: rebuild the image, then
   `podman rm -f litter-robot-monitor` and repeat step 4's `podman create` +
   `generate systemd` + `enable --now`.

## Verifying a deployment actually works

`scripts/smoke_test.py` logs into your Whisker account, prints your robot's
real waste drawer / litter level readings, and (with `--notify`) sends one
real test text through the SMS gateway. Run it once after any deployment to
confirm credentials and the gateway are both working, before trusting the
long-running poll loop:

```bash
# venv
python scripts/smoke_test.py --notify

# Docker
docker compose run --rm litter-robot-monitor python scripts/smoke_test.py --notify

# Podman
podman run --rm --env-file .env litter-robot-monitor python scripts/smoke_test.py --notify
```

It exits `0` and prints "Smoke test passed." on success, or a `FAILED:`
line explaining what broke (bad Whisker login, no robots on the account, or
an SMTP/gateway failure) with a nonzero exit code otherwise. There's no
other automated test suite in this repo — the monitor logic is simple
enough that this end-to-end check is the practical way to verify it.

## Notes

- Litter-Robot 3 only exposes waste drawer level (no litter/globe level), so
  only the "drawer full" alert applies to it.
- Litter-Robot 4 exposes both waste drawer level and litter (hopper) level.
