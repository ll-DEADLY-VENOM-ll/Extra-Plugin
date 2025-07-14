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

# Small caps conversion dictionary
SMALL_CAPS = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ', ' ': ' '
}

def to_small_caps(text):
    """Convert text to small caps style"""
    return ''.join(SMALL_CAPS.get(c.lower(), c) for c in text)

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton(
    to_small_caps("switch to whisper"), 
    switch_inline_query_current_chat=""
)]])

async def _whisper(_, inline_query):
    data = inline_query.query.strip()
    
    if not data or data.lower() == "help":
        return await in_help(inline_query)
    
    # Check both formats
    parts = data.split(f"@{BOT_USERNAME}", 1)
    if len(parts) == 2 and parts[1].strip():
        user_identifier = parts[0].strip()
        msg = parts[1].strip()
    else:
        try:
            parts = data.split(None, 2)
            if len(parts) < 2:
                return await show_usage(inline_query)
            user_identifier = parts[1] if parts[0] == f"@{BOT_USERNAME}" else parts[0]
            msg = parts[2] if parts[0] == f"@{BOT_USERNAME}" else ' '.join(parts[1:])
        except:
            return await show_usage(inline_query)

    try:
        if user_identifier.startswith('@'):
            user_identifier = user_identifier[1:]
        
        user = await _.get_users(user_identifier)
        
        # Store whisper
        whisper_db[f"{inline_query.from_user.id}_{user.id}"] = {
            "msg": msg,
            "from_user": inline_query.from_user.id,
            "to_user": user.id,
            "from_name": inline_query.from_user.first_name,
            "from_username": inline_query.from_user.username
        }
        
        # Create notification message
        notification_msg = to_small_caps(
            f"📩 ᴡʜɪsᴘᴇʀ ғᴏʀ {user.mention}\n\n"
            f"{inline_query.from_user.mention} sᴇɴᴛ ʏᴏᴜ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴡʜɪsᴘᴇʀ!\n"
            "ᴏɴʟʏ ʏᴏᴜ ᴄᴀɴ ᴠɪᴇᴡ ɪᴛ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʙᴇʟᴏᴡ."
        )
        
        buttons = [
            [
                InlineKeyboardButton(
                    to_small_caps(f"🔓 view whisper from {inline_query.from_user.first_name}"),
                    callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    to_small_caps("👤 view sender profile"),
                    url=f"tg://user?id={inline_query.from_user.id}"
                )
            ]
        ]
        
        one_time_buttons = [
            [
                InlineKeyboardButton(
                    to_small_caps(f"⚠️ one-time whisper from {inline_query.from_user.first_name}"),
                    callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one"
                )
            ],
            [
                InlineKeyboardButton(
                    to_small_caps("👤 view sender profile"),
                    url=f"tg://user?id={inline_query.from_user.id}"
                )
            ]
        ]
        
        results = [
            InlineQueryResultArticle(
                title=to_small_caps("💌 normal whisper"),
                description=to_small_caps(f"send to {user.first_name} (multiple views)"),
                input_message_content=InputTextMessageContent(
                    notification_msg,
                    parse_mode=ParseMode.MARKDOWN
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=InlineKeyboardMarkup(buttons)
            ),
            InlineQueryResultArticle(
                title=to_small_caps("⚠️ one-time whisper"),
                description=to_small_caps(f"send to {user.first_name} (disappears after viewing)"),
                input_message_content=InputTextMessageContent(
                    notification_msg,
                    parse_mode=ParseMode.MARKDOWN
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=InlineKeyboardMarkup(one_time_buttons)
            )
        ]
        
        await inline_query.answer(results, cache_time=0)
        
    except Exception as e:
        await show_error(inline_query, str(e))

async def show_usage(inline_query):
    help_msg = to_small_caps(
        f"💌 ᴡʜɪsᴘᴇʀ ᴜsᴀɢᴇ\n\n"
        f"ғᴏʀᴍᴀᴛ 1: @{BOT_USERNAME} [ᴜsᴇʀ] [ᴍsɢ]\n"
        f"ғᴏʀᴍᴀᴛ 2: [ᴜsᴇʀ] @{BOT_USERNAME} [ᴍsɢ]\n\n"
        f"ᴇxᴀᴍᴘʟᴇs:\n"
        f"@{BOT_USERNAME} @username ɪ ʟᴏᴠᴇ ʏᴏᴜ\n"
        f"@username @{BOT_USERNAME} ᴄʜᴇᴄᴋ ᴛʜɪs ᴏᴜᴛ!"
    )
    
    await inline_query.answer([InlineQueryResultArticle(
        title=to_small_caps("💌 whisper help"),
        description=to_small_caps("how to send whispers"),
        input_message_content=InputTextMessageContent(
            help_msg,
            parse_mode=ParseMode.MARKDOWN
        ),
        thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
        reply_markup=switch_btn
    )])

async def show_error(inline_query, error=""):
    error_msg = to_small_caps(
        "❌ ᴇʀʀᴏʀ\n\n"
        "ᴄᴏᴜʟᴅɴ'ᴛ sᴇɴᴅ ᴡʜɪsᴘᴇʀ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ:\n"
        "1. ᴛʜᴇ ᴜsᴇʀ ᴇxɪsᴛs\n"
        "2. ʏᴏᴜ ᴜsᴇᴅ ᴀ ᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ"
    )
    
    await inline_query.answer([InlineQueryResultArticle(
        title=to_small_caps("❌ error"),
        description=to_small_caps("failed to send whisper"),
        input_message_content=InputTextMessageContent(
            error_msg,
            parse_mode=ParseMode.MARKDOWN
        ),
        thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
        reply_markup=switch_btn
    )])

@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whisper_callback(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 6399386263]:
        try:
            await _.send_message(
                from_user,
                to_small_caps(
                    f"{query.from_user.mention} ᴛʀɪᴇᴅ ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴡʜɪsᴘᴇʀ ᴛᴏ {to_user}."
                )
            )
        except unauthorised:
            pass
        
        return await query.answer(
            to_small_caps("🔒 ᴛʜɪs ᴡʜɪsᴘᴇʀ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!"), 
            show_alert=True
        )
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        whisper_data = whisper_db[search_msg]
        sender_link = f"[{whisper_data['from_name']}](tg://user?id={whisper_data['from_user']})"
        msg = to_small_caps(
            f"💌 ᴡʜɪsᴘᴇʀ ғʀᴏᴍ {sender_link}:\n\n"
            f"{whisper_data['msg']}\n\n"
            f"🔗 ʀᴇᴘʟʏ ᴛᴏ sᴇɴᴅᴇʀ"
        )
    except:
        msg = to_small_caps("⚠️ ᴡʜɪsᴘᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ!")
    
    SWITCH = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            to_small_caps("💌 send a whisper"), 
            switch_inline_query_current_chat=""
        ),
        InlineKeyboardButton(
            to_small_caps("👤 view sender"), 
            url=f"tg://user?id={from_user}"
        )
    ]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one" and user_id == to_user:
        try:
            del whisper_db[search_msg]
        except:
            pass
        
        await query.edit_message_text(
            to_small_caps("📝 ᴛʜɪs ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!"),
            reply_markup=SWITCH,
            parse_mode=ParseMode.MARKDOWN
        )

async def in_help(inline_query):
    help_msg = to_small_caps(
        f"💌 ᴡʜɪsᴘᴇʀ ʜᴇʟᴘ\n\n"
        f"sᴇɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴍᴇssᴀɢᴇs ᴛʜᴀᴛ ᴏɴʟʏ ᴛʜᴇ ʀᴇᴄɪᴘɪᴇɴᴛ ᴄᴀɴ ᴠɪᴇᴡ.\n\n"
        f"ғᴏʀᴍᴀᴛs:\n"
        f"1. @{BOT_USERNAME} [ᴜsᴇʀ] [ᴍsɢ]\n"
        f"2. [ᴜsᴇʀ] @{BOT_USERNAME} [ᴍsɢ]\n\n"
        f"ᴛʜᴇ ʀᴇᴄɪᴘɪᴇɴᴛ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴍɪɴᴇɴᴛʟʏ ᴍᴇɴᴛɪᴏɴᴇᴅ."
    )
    
    await inline_query.answer([InlineQueryResultArticle(
        title=to_small_caps("💌 whisper help"),
        description=to_small_caps("how to send private whispers"),
        input_message_content=InputTextMessageContent(
            help_msg,
            parse_mode=ParseMode.MARKDOWN
        ),
        thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
        reply_markup=switch_btn
    )])

@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "" or string.startswith("help"):
        await in_help(inline_query)
    else:
        await _whisper(_, inline_query)