import os
import json
import logging
from datetime import time
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS  = {int(os.environ.get("ADMIN_ID", "0")), 83740493}  # Admin user IDs
DATA_FILE  = "data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"stories": [], "current_index": 0, "users": [], "paused_users": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
        await update.message.reply_text(
            "👋 *Welcome to the Daily Story Bot!*\n\n"
            "You're now subscribed. Every day you'll receive one story in order.\n\n"
            "📖 Commands:\n"
            "/queue — see upcoming stories\n"
            "/today — get today's story right now\n"
            "/pause — pause daily stories\n"
            "/resume — resume daily stories\n"
            "/stop — unsubscribe\n\n"
            "Enjoy the stories! ✨",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("You're already subscribed! Use /today to get the current story. 😊")

async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id in data["users"]:
        data["users"].remove(user_id)
        if user_id in data["paused_users"]:
            data["paused_users"].remove(user_id)
        save_data(data)
        await update.message.reply_text("You've unsubscribed. Come back anytime with /start 👋")
    else:
        await update.message.reply_text("You're not subscribed. Use /start to join!")

async def pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id not in data["users"]:
        await update.message.reply_text("You're not subscribed yet. Use /start first.")
        return
    if user_id not in data["paused_users"]:
        data["paused_users"].append(user_id)
        save_data(data)
        await update.message.reply_text("⏸ Daily stories paused. Use /resume to start again.")
    else:
        await update.message.reply_text("Already paused. Use /resume to start receiving stories.")

async def resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id in data["paused_users"]:
        data["paused_users"].remove(user_id)
        save_data(data)
        await update.message.reply_text("▶️ Resumed! You'll get your next story tomorrow.")
    else:
        await update.message.reply_text("You're not paused. Stories are already being sent daily!")

async def today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id not in data["users"]:
        await update.message.reply_text("Please /start first to subscribe.")
        return
    if not data["stories"]:
        await update.message.reply_text("No stories available yet. Check back soon!")
        return
    idx = data["current_index"] % len(data["stories"])
    story = data["stories"][idx]
    total = len(data["stories"])
    await update.message.reply_text(
        f"📖 *Story {idx + 1} of {total}*\n\n{story}",
        parse_mode="Markdown"
    )

async def queue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["stories"]:
        await update.message.reply_text("No stories in the queue yet.")
        return
    idx = data["current_index"] % len(data["stories"])
    total = len(data["stories"])
    lines = [f"📚 *Story Queue* ({total} total)\n"]
    for i, story in enumerate(data["stories"]):
        prefix = "➡️ " if i == idx else f"{i+1}. "
        preview = story[:60] + "..." if len(story) > 60 else story
        lines.append(f"{prefix}{preview}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ─── ADMIN COMMANDS ───────────────────────────────────────────────────────────
async def addprasang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only the admin can add stories.")
        return
    story_text = " ".join(ctx.args)
    if not story_text:
        await update.message.reply_text(
            "Please provide a story.\nUsage: /addstory Your story text here..."
        )
        return
    data = load_data()
    data["stories"].append(story_text)
    save_data(data)
    position = len(data["stories"])
    await update.message.reply_text(
        f"✅ Story added! It's #{position} in the queue.\n\n"
        f"Preview: {story_text[:100]}{'...' if len(story_text) > 100 else ''}"
    )

async def removestory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only the admin can remove stories.")
        return
    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("Usage: /removestory <number>\nUse /queue to see story numbers.")
        return
    num = int(ctx.args[0]) - 1
    data = load_data()
    if num < 0 or num >= len(data["stories"]):
        await update.message.reply_text("Invalid story number.")
        return
    removed = data["stories"].pop(num)
    if data["current_index"] >= len(data["stories"]) and data["stories"]:
        data["current_index"] = 0
    save_data(data)
    await update.message.reply_text(f"🗑 Removed story #{num+1}:\n{removed[:80]}...")

async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only.")
        return
    data = load_data()
    total_users = len(data["users"])
    paused = len(data["paused_users"])
    active = total_users - paused
    stories = len(data["stories"])
    current = (data["current_index"] % stories) + 1 if stories else 0
    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"👥 Total subscribers: {total_users}\n"
        f"▶️ Active: {active}\n"
        f"⏸ Paused: {paused}\n"
        f"📖 Total stories: {stories}\n"
        f"📍 Current story: #{current}",
        parse_mode="Markdown"
    )

# ─── DAILY JOB ────────────────────────────────────────────────────────────────
async def send_daily_story(ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data["stories"] or not data["users"]:
        return

    idx = data["current_index"] % len(data["stories"])
    story = data["stories"][idx]
    total = len(data["stories"])

    success = 0
    for user_id in data["users"]:
        if user_id in data["paused_users"]:
            continue
        try:
            await ctx.bot.send_message(
                chat_id=user_id,
                text=f"📖 *Daily Story — {idx + 1} of {total}*\n\n{story}",
                parse_mode="Markdown"
            )
            success += 1
        except Exception as e:
            logger.warning(f"Could not send to {user_id}: {e}")

    # Advance to next story
    data["current_index"] = (idx + 1) % len(data["stories"])
    save_data(data)
    logger.info(f"Daily story sent to {success} users. Next index: {data['current_index']}")

# ─── UNKNOWN COMMAND ──────────────────────────────────────────────────────────
async def unknown(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I don't understand that command.\n\n"
        "Try /start to begin or /today to read a story!"
    )

async def clear_stories(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only.")
        return
    data = load_data()
    data["stories"] = []
    data["current_index"] = 0
    save_data(data)
    await update.message.reply_text("🗑 All stories cleared!")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("stop",   stop))
    app.add_handler(CommandHandler("pause",  pause))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("today",  today))
    app.add_handler(CommandHandler("queue",  queue))

    # Admin commands
    app.add_handler(CommandHandler("addprasang",    addprasang))
    app.add_handler(CommandHandler("removestory", removestory))
    app.add_handler(CommandHandler("stats",       stats))
    app.add_handler(CommandHandler("clear",       clear_stories))

    # Unknown
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Two daily jobs
    app.job_queue.run_daily(
        send_daily_story,
        time=time(hour=6, minute=30)
    )
    app.job_queue.run_daily(
        send_daily_story,
        time=time(hour=16, minute=30)
    )

    logger.info("Bot started. Daily stories at 6:30 AM and 4:30 PM UTC")
    app.run_polling()

if __name__ == "__main__":
    main()