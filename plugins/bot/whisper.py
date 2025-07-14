from ChampuMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ParseMode

from utils.permissions import unauthorised

BOT_USERNAME = app.username
whisper_db = {}

async def create_whisper_notification(from_user, to_user):
    """Create the whisper notification message"""
    return (
        f"📩 Whisper for {to_user.mention}\n\n"
        f"{from_user.mention} sent you a private whisper!\n"
        "Only you can view it by clicking below.\n\n"
        f"💬 @{BOT_USERNAME}"
    )

async def show_usage(inline_query):
    """Show whisper usage instructions"""
    help_msg = (
        f"💌 Whisper Usage\n\n"
        f"Format: @{BOT_USERNAME} [username/id/mention] [message]\n\n"
        f"Examples:\n"
        f"@{BOT_USERNAME} @username I love you\n"
        f"@{BOT_USERNAME} 123456789 Check this out!"
    )
    
    switch_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "💌 Switch to Whisper", 
            switch_inline_query_current_chat=""
        )
    ]])
    
    await inline_query.answer([InlineQueryResultArticle(
        title="💌 How to use",
        description="Send private whispers",
        input_message_content=InputTextMessageContent(
            help_msg,
            parse_mode=ParseMode.MARKDOWN
        ),
        thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
        reply_markup=switch_btn
    )])

async def _whisper(_, inline_query):
    """Handle whisper inline queries"""
    data = inline_query.query.strip()
    
    if not data or data.lower() == "help":
        return await show_usage(inline_query)
    
    try:
        # Parse command: @bot username message
        parts = data.split(None, 2)
        if len(parts) < 3:
            return await show_usage(inline_query)
            
        user_identifier = parts[1]
        msg = parts[2]
        
        # Remove @ if present
        if user_identifier.startswith('@'):
            user_identifier = user_identifier[1:]
        
        # Get user object
        user = await _.get_users(user_identifier)
        
        # Store whisper in database
        whisper_key = f"{inline_query.from_user.id}_{user.id}"
        whisper_db[whisper_key] = {
            "msg": msg,
            "from_user": inline_query.from_user.id,
            "to_user": user.id,
            "from_name": inline_query.from_user.first_name,
            "from_username": inline_query.from_user.username
        }
        
        # Create notification message
        notification_msg = await create_whisper_notification(inline_query.from_user, user)
        
        # Create buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔓 View Whisper from {inline_query.from_user.first_name}",
                    callback_data=f"whisper_{inline_query.from_user.id}_{user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 View Sender Profile",
                    url=f"tg://user?id={inline_query.from_user.id}"
                ),
                InlineKeyboardButton(
                    "💌 Send Whisper",
                    switch_inline_query_current_chat=f"@{BOT_USERNAME} @{user.username or user.id} "
                )
            ]
        ])
        
        one_time_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"⚠️ One-Time Whisper from {inline_query.from_user.first_name}",
                    callback_data=f"whisper_{inline_query.from_user.id}_{user.id}_one"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 View Sender Profile",
                    url=f"tg://user?id={inline_query.from_user.id}"
                )
            ]
        ])
        
        # Create inline results
        results = [
            InlineQueryResultArticle(
                title="💌 Normal Whisper",
                description=f"Send to {user.first_name} (multiple views)",
                input_message_content=InputTextMessageContent(
                    notification_msg,
                    parse_mode=ParseMode.MARKDOWN
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=buttons
            ),
            InlineQueryResultArticle(
                title="⚠️ One-Time Whisper",
                description=f"Send to {user.first_name} (disappears after viewing)",
                input_message_content=InputTextMessageContent(
                    notification_msg,
                    parse_mode=ParseMode.MARKDOWN
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=one_time_buttons
            )
        ]
        
        await inline_query.answer(results, cache_time=0)
        
    except Exception as e:
        error_msg = (
            "❌ Error\n\n"
            "Failed to send whisper. Please check:\n"
            "1. The user exists\n"
            "2. You used the correct format\n\n"
            f"Try: @{BOT_USERNAME} @username your message"
        )
        
        await inline_query.answer([InlineQueryResultArticle(
            title="❌ Error",
            description="Failed to send whisper",
            input_message_content=InputTextMessageContent(
                error_msg,
                parse_mode=ParseMode.MARKDOWN
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "💌 How to use",
                    switch_inline_query_current_chat="help"
                )
            ]])
        )])

@app.on_callback_query(filters.regex(pattern=r"whisper_(.*)"))
async def whisper_callback(_, query):
    """Handle whisper callback queries"""
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    # Check authorization
    if user_id not in [from_user, to_user, 6399386263]:
        try:
            await _.send_message(
                from_user,
                f"{query.from_user.mention} tried to view your whisper to {to_user}."
            )
        except unauthorised:
            pass
        
        return await query.answer(
            "🔒 This whisper is not for you!", 
            show_alert=True
        )
    
    # Retrieve whisper message
    whisper_key = f"{from_user}_{to_user}"
    try:
        whisper_data = whisper_db[whisper_key]
        sender_link = f"[{whisper_data['from_name']}](tg://user?id={whisper_data['from_user']})"
        if whisper_data.get('from_username'):
            sender_link += f" (@{whisper_data['from_username']})"
        
        msg = (
            f"💌 Whisper from {sender_link}:\n\n"
            f"{whisper_data['msg']}\n\n"
            f"🔗 Reply to sender"
        )
    except:
        msg = "⚠️ Whisper not found or expired!"
    
    # Create reply markup
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💌 Send Whisper", 
                switch_inline_query_current_chat=""
            ),
            InlineKeyboardButton(
                "👤 View Sender", 
                url=f"tg://user?id={from_user}"
            )
        ]
    ])
    
    await query.answer(msg, show_alert=True)
    
    # Handle one-time whisper
    if len(data) > 3 and data[3] == "one" and user_id == to_user:
        try:
            del whisper_db[whisper_key]
        except:
            pass
        
        await query.edit_message_text(
            "📝 This one-time whisper has been deleted!",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

@app.on_inline_query()
async def bot_inline(_, inline_query):
    """Handle all inline queries"""
    string = inline_query.query.lower()
    
    if string.strip() == "" or string.startswith("help"):
        await show_usage(inline_query)
    else:
        await _whisper(_, inline_query)