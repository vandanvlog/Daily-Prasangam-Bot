# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Daily-Prasangam-Bot** — a Telegram bot that delivers a rotating queue of stories/prasangams to subscribers on a daily schedule.

## Running the Bot

```bash
# Set required environment variables, then run:
python bot.py
```

Required environment variables:
- `BOT_TOKEN` — Telegram Bot API token (required)
- `ADMIN_ID` — Telegram user ID for admin-only commands (default: `"0"`)
- `SEND_HOUR` — Hour (24h UTC) for daily sends (default: `"8"`)
- `SEND_MIN` — Minute for daily sends (default: `"0"`)

## Dependencies

No `requirements.txt` exists yet. The project requires:
```
python-telegram-bot>=20.0
```

Install with: `pip install python-telegram-bot`

## Architecture

**Single-file** — all logic lives in [bot.py](bot.py) (~243 lines).

### Data layer

Persisted to `data.json` (created at runtime). Schema:
```json
{
  "stories": [],        // list of story strings
  "current_index": 0,   // rotation pointer
  "users": [],          // subscribed user IDs
  "paused_users": []    // paused (but still subscribed) user IDs
}
```

Every handler follows this pattern: `load_data()` → modify in-memory → `save_data(data)`. There is no transaction safety or locking.

### Command handlers

| Command | Access | Description |
|---|---|---|
| `/start` | User | Subscribe and show welcome |
| `/stop` | User | Unsubscribe completely |
| `/pause` | User | Pause delivery without unsubscribing |
| `/resume` | User | Resume delivery |
| `/today` | User | Get current story immediately |
| `/queue` | User | List all stories with previews |
| `/addstory <text>` | Admin | Append story to queue |
| `/removestory <n>` | Admin (1-indexed) | Remove story by position |
| `/stats` | Admin | Subscriber/story statistics |

Admin gate: handlers check `str(update.effective_user.id) == ADMIN_ID`.

### Scheduled job

`send_daily_story()` runs daily at `SEND_HOUR:SEND_MIN` UTC via PTB's job queue. It iterates all users, skips paused ones, sends the story at `current_index`, then advances the index (wraps with modulo). Per-user exceptions are caught and logged so one failure doesn't abort the whole job.
