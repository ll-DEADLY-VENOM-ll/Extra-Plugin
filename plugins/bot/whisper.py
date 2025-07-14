from ChampuMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from utils.permissions import unauthorised

BOT_USERNAME = app.username

whisper_db = {}

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query_current_chat="")]])

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="💒 ᴡʜɪsᴘᴇʀ",
                description=f"@{BOT_USERNAME} [USERNAME | ID | MENTION] [TEXT]",
                input_message_content=InputTextMessageContent(
                    f"💒 Whisper Usage:\n\n"
                    f"@{BOT_USERNAME} [username|id|mention] [your message]\n\n"
                    f"Examples:\n"
                    f"@{BOT_USERNAME} @username Hello\n"
                    f"@{BOT_USERNAME} 123456789 I miss you\n"
                    f"@{BOT_USERNAME} @[USERNAME] Let's chat!"
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=switch_btn
            )
        ]
        return mm
    
    try:
        # Extract user reference (could be username, ID, or mention)
        user_ref = data.split()[0]
        msg = data.split(None, 1)[1]
        
        # Try to get user by username/ID/mention
        try:
            user = await _.get_users(user_ref)
        except:
            # Check if it's a mention format (@username)
            if user_ref.startswith("@"):
                user_ref = user_ref[1:]  # Remove @
                user = await _.get_users(user_ref)
            else:
                raise Exception("Invalid user reference")
        
        # Prepare user description with username if available
        user_desc = user.first_name
        if user.username:
            user_desc += f" (@{user.username})"
        
        whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 ᴡʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}")]])
        one_time_whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one")]])
        
        mm = [
            InlineQueryResultArticle(
                title="💒 ᴡʜɪsᴘᴇʀ",
                description=f"Send whisper to {user_desc}",
                input_message_content=InputTextMessageContent(
                    f"💒 You're sending a whisper to {user_desc}\n\n"
                    f"Type your message below:"
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=whisper_btn
            ),
            InlineQueryResultArticle(
                title="🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ",
                description=f"Send one-time whisper to {user_desc}",
                input_message_content=InputTextMessageContent(
                    f"🔩 You're sending a one-time whisper to {user_desc}\n\n"
                    f"Type your message below:"
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=one_time_whisper_btn
            )
        ]
        
        # Store the whisper message
        whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
        
        return mm
        
    except Exception as e:
        mm = [
            InlineQueryResultArticle(
                title="⚠️ Error",
                description="Invalid user reference! Use username, ID or mention",
                input_message_content=InputTextMessageContent(
                    "Invalid user reference!\n\n"
                    "Please use:\n"
                    "- Username (with or without @)\n"
                    "- User ID\n"
                    "- User mention (@username)\n\n"
                    f"Example: @{BOT_USERNAME} @username Hello there"
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=switch_btn
            )
        ]
        return mm


@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 7006524418]:
        try:
            sender = await _.get_users(from_user)
            target = await _.get_users(to_user)
            
            # Prepare target description
            target_desc = target.first_name
            if target.username:
                target_desc += f" (@{target.username})"
                
            await _.send_message(
                from_user, 
                f"⚠️ {query.from_user.mention} is trying to open your whisper to {target_desc}!"
            )
        except unauthorised:
            pass
        
        return await query.answer("This whisper is not for you 🚧", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        msg = whisper_db[search_msg]
    except:
        msg = "🚫 Error!\n\nWhisper has been deleted from the database!"
    
    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("ɢᴏ ɪɴʟɪɴᴇ 🪝", switch_inline_query_current_chat="")]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text(
                "📬 Whisper has been read!\n\nPress the button below to send a whisper!", 
                reply_markup=SWITCH
            )


async def in_help():
    answers = [
        InlineQueryResultArticle(
            title="💒 ᴡʜɪsᴘᴇʀ",
            description=f"@{BOT_USERNAME} [USERNAME | ID | MENTION] [TEXT]",
            input_message_content=InputTextMessageContent(
                f"**💒 Whisper Usage:**\n\n"
                f"`@{BOT_USERNAME} [username|id|mention] [your message]`\n\n"
                f"**Examples:**\n"
                f"`@{BOT_USERNAME} @username Hello`\n"
                f"`@{BOT_USERNAME} 123456789 I miss you`\n"
                f"`@{BOT_USERNAME} @[USERNAME] Let's chat!`\n\n"
                f"The target user will be notified with your message."
            ),
            thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
            reply_markup=switch_btn
        )
    ]
    return answers


@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers, cache_time=0)