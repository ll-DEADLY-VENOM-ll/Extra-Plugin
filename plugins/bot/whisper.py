from ChampuMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.errors import UsernameInvalid, PeerIdInvalid

BOT_USERNAME = app.username
whisper_db = {}

# Improved switch button with better text
switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔮 Start Whisper", switch_inline_query_current_chat="")]])

async def _whisper(_, inline_query):
    data = inline_query.query.strip()
    
    if not data or len(data.split()) < 2:
        return [InlineQueryResultArticle(
            title="💌 Send Secret Whisper",
            description=f"Format: @{BOT_USERNAME} username message",
            input_message_content=InputTextMessageContent(
                f"✨ **Whisper Bot Instructions** ✨\n\n"
                f"Send private messages that only the recipient can view!\n\n"
                f"**Usage:**\n`@{BOT_USERNAME} @username your message`\n"
                f"`@{BOT_USERNAME} userid your message`\n\n"
                f"Example: `@{BOT_USERNAME} @john Hello there!`"
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=switch_btn
        )]

    try:
        # Extract target user reference and message
        parts = data.split(None, 1)
        user_ref = parts[0].strip('@[]')  # Handle @username and [@username]
        msg = parts[1]
        
        # Get user object
        user = await _.get_users(user_ref)
        
        # Create mention text (clickable in groups)
        mention_text = user.mention(user.first_name)
        if user.username:
            mention_text += f" (@{user.username})"
        
        # Store whisper data with all needed info
        whisper_id = f"{inline_query.from_user.id}_{user.id}"
        whisper_db[whisper_id] = {
            "msg": msg,
            "from_user": inline_query.from_user.id,
            "to_user": user.id,
            "mention": mention_text,
            "username": user.username
        }

        # Create buttons with better styling
        buttons = [
            [
                InlineKeyboardButton("💌 Normal Whisper", callback_data=f"whisper_{whisper_id}"),
                InlineKeyboardButton("⏳ One-Time Whisper", callback_data=f"whisper_{whisper_id}_one")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="whisper_cancel")]
        ]

        return [InlineQueryResultArticle(
            title=f"💌 Whisper to {user.first_name}",
            description=f"Send secret message to {mention_text}",
            input_message_content=InputTextMessageContent(
                f"🔮 You're sending a whisper to {mention_text}\n\n"
                f"Type your private message below:\n\n"
                f"💬 Message: {msg[:50]}..." if len(msg) > 50 else f"💬 Message: {msg}"
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=InlineKeyboardMarkup(buttons)
        )]

    except Exception as e:
        return [InlineQueryResultArticle(
            title="⚠️ Error Finding User",
            description="Check the username/ID and try again",
            input_message_content=InputTextMessageContent(
                f"❌ Couldn't find that user!\n\n"
                f"Please make sure you're using:\n"
                f"- Correct @username\n"
                f"- Valid user ID\n"
                f"- Proper mention format\n\n"
                f"Example: @{BOT_USERNAME} @username Hello there!"
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=switch_btn
        )]

@app.on_callback_query(filters.regex("^whisper_"))
async def whisper_callback(_, query):
    data = query.data.split("_")
    user_id = query.from_user.id
    
    if data[1] == "cancel":
        await query.message.delete()
        return

    whisper_id = data[1]
    is_one_time = len(data) > 2 and data[2] == "one"
    
    if whisper_id not in whisper_db:
        return await query.answer("❌ Whisper expired or invalid!", show_alert=True)
    
    whisper = whisper_db[whisper_id]
    from_user = whisper["from_user"]
    to_user = whisper["to_user"]
    
    # Check permissions
    if user_id not in [from_user, to_user, 7006524418]: 
        try:
            sender = await _.get_users(from_user)
            target = await _.get_users(to_user)
            mention = target.mention(target.first_name)
            if target.username:
                mention += f" (@{target.username})"
                
            await _.send_message(
                from_user,
                f"⚠️ {query.from_user.mention} tried to view your whisper to {mention}!",
                disable_notification=True
            )
        except:
            pass
        
        return await query.answer("🔒 This whisper isn't for you!", show_alert=True)
    
    # Prepare the whisper message with proper tagging
    sender_mention = (await _.get_users(from_user)).mention()
    whisper_text = (
        f"🔮 **Secret Whisper** 🔮\n\n"
        f"From: {sender_mention}\n"
        f"To: {whisper['mention']}\n\n"
        f"💬 Message:\n{whisper['msg']}"
    )
    
    # Show the whisper
    await query.answer(whisper_text, show_alert=True)
    
    # Handle one-time whisper
    if is_one_time and user_id == to_user:
        del whisper_db[whisper_id]
        await query.edit_message_text(
            "📭 One-time whisper has been read and deleted!\n"
            "Press the button below to send your own whisper:",
            reply_markup=switch_btn
        )

@app.on_inline_query()
async def inline_handler(_, inline_query):
    query = inline_query.query
    if not query.strip():
        # Show help when empty query
        await inline_query.answer([InlineQueryResultArticle(
            title="💌 Send Secret Whisper",
            description=f"Start with @{BOT_USERNAME} username message",
            input_message_content=InputTextMessageContent(
                f"✨ Send private whispers with @{BOT_USERNAME}!\n\n"
                f"Usage: @{BOT_USERNAME} @username your_message"
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=switch_btn
        )])
    else:
        # Process whisper request
        results = await _whisper(_, inline_query)
        await inline_query.answer(results, cache_time=0)