import re
import requests
import os
import tempfile
from pyrogram import filters

from ChampuMusic import app
from config import LOGGER_ID


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return
    url = message.text.split()[1]
    if not re.match(
        re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"), url
    ):
        return await message.reply_text(
            "Tʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ URL ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL😅😅"
        )
    a = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        response = requests.get(api_url)
        result = response.json()
        data = result["result"]
    except Exception as e:
        f = f"Eʀʀᴏʀ :\n{e}"
        try:
            await a.edit(f)
        except Exception:
            await message.reply_text(f)
            return await app.send_message(LOGGER_ID, f)
        return await app.send_message(LOGGER_ID, f)

    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        type = data["extension"]
        size = data["formattedSize"]
        caption = f"**Dᴜʀᴀᴛɪᴏɴ :** {duration}\n**Qᴜᴀʟɪᴛʏ :** {quality}\n**Tʏᴘᴇ :** {type}\n**Sɪᴢᴇ :** {size}"
        
        try:
            await a.edit("Dᴏᴡɴʟᴏᴀᴅɪɴɢ...")
            
            # Download the video
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{type}") as temp_file:
                for chunk in video_response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            await a.edit("Uᴘʟᴏᴀᴅɪɴɢ...")
            
            # Send the video file
            await message.reply_video(
                video=temp_file_path,
                caption=caption,
                supports_streaming=True
            )
            
            await a.delete()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass
            
            error_msg = f"Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ/sᴇɴᴅ ʀᴇᴇʟ: {str(e)}"
            try:
                await a.edit(error_msg)
            except Exception:
                await message.reply_text(error_msg)
            await app.send_message(LOGGER_ID, error_msg)
    else:
        try:
            return await a.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
        except Exception:
            return await message.reply_text("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")


__MODULE__ = "Rᴇᴇʟ"
__HELP__ = """
**ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ:**

• `/ig [URL]`: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
• `/instagram [URL]`: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
• `/reel [URL]`: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
"""