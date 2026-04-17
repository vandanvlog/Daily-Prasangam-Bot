# 📖 Daily Prasangam Bot

A Telegram bot that delivers a daily rotating story (prasangam) to subscribers — one story per day, in order, automatically.

---

## Features

- **Daily delivery** — sends one story to all subscribers at a configured time each day
- **Rotating queue** — cycles through stories in order, looping back when the queue ends
- **Pause & resume** — users can pause delivery without losing their subscription
- **On-demand reading** — subscribers can read the current story anytime with `/today`
- **Admin panel** — add/remove stories and view live stats from Telegram itself

---

## Bot Commands

### User Commands

| Command | Description |
|---|---|
| `/start` | Subscribe to daily stories |
| `/stop` | Unsubscribe |
| `/pause` | Pause daily delivery |
| `/resume` | Resume daily delivery |
| `/today` | Read today's story right now |
| `/queue` | Browse all stories in the queue |

### Admin Commands

| Command | Description |
|---|---|
| `/addstory <text>` | Add a new story to the queue |
| `/removestory <n>` | Remove story by number (use `/queue` to see numbers) |
| `/stats` | View subscriber count, active/paused, and story count |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/vandanvlog/Daily-Prasangam-Bot.git
cd Daily-Prasangam-Bot
```

### 2. Install dependencies

```bash
pip install python-telegram-bot
```

### 3. Configure environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | — | Your Telegram Bot API token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | No | `0` | Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot)) |
| `SEND_HOUR` | No | `8` | Hour to send daily stories (UTC, 24h format) |
| `SEND_MIN` | No | `0` | Minute to send daily stories |

Set them in your terminal before running:

```bash
export BOT_TOKEN="your_token_here"
export ADMIN_ID="your_telegram_id"
export SEND_HOUR="8"
export SEND_MIN="0"
```

### 4. Run the bot

```bash
python bot.py
```

---

## Deployment

### Railway / Render / Koyeb

1. Push this repo to GitHub
2. Create a new project and connect the repo
3. Set environment variables (`BOT_TOKEN`, `ADMIN_ID`, etc.) in the dashboard
4. Set the start command to `python bot.py`

### Keep it running with a process manager (VPS)

```bash
nohup python bot.py &
```

Or use **screen**:

```bash
screen -S prasangam-bot
python bot.py
# Press Ctrl+A, then D to detach
```

---

## How It Works

Stories are stored in a local `data.json` file. The bot maintains a `current_index` pointer that advances by one after each daily send, cycling back to the start when all stories have been delivered. Each subscriber's state (subscribed, paused) is tracked in the same file.

```
data.json
├── stories[]        — list of all story texts
├── current_index    — pointer to today's story
├── users[]          — subscribed user IDs
└── paused_users[]   — users who paused delivery
```

---

## License

MIT
