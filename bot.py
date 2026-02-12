# Don't Remove Credit @teacher_slex
# Subscribe YouTube ƈɦǟռռɛʟ For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram.types import Message
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users
from configs import cfg
import asyncio

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

#━━━━━━━━━━━━━━━━━━━━ HELPER ━━━━━━━━━━━━━━━━━━━━
def parse_post_link(link: str):
    parts = link.split("/")
    chat = parts[-2]
    msg_id = int(parts[-1])
    return chat, msg_id

#━━━━━━━━━━━━━━━━━━━━ JOIN REQUEST (AUTO-APPROVE + DM) ━━━━━━━━━━━━━━━━━━━━
# Note: Pyrogram's on_chat_join_request passes a ChatJoinRequest-like object.
@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, join_request):
    # join_request has attributes: chat, from_user (or .user), etc.
    try:
        op = getattr(join_request, "chat", None) or join_request.chat
        user = getattr(join_request, "from_user", None) or getattr(join_request, "user", None)

        if not op or not user:
            return

        add_group(op.id)
        add_user(user.id)

        # ----- AUTO-APPROVE -----
        try:
            await app.approve_chat_join_request(op.id, user.id)
            # optional: notify the user they are approved
            await app.send_message(
                user.id,
                f"✅ Hi {user.first_name}, aapka join request approve kar diya gaya hai. Welcome!\n\n🔰 Join karne ke liye shukriya."
            )
        except FloodWait as e:
            # server asks to wait: sleep and retry
            await asyncio.sleep(e.x if hasattr(e, "x") else e.value)
            try:
                await app.approve_chat_join_request(op.id, user.id)
            except Exception:
                pass
        except errors.RPCError as e:
            # common failures (bot not admin / missing rights / PeerIdInvalid etc.)
            # fallback: try DM informing user
            try:
                await app.send_message(
                    user.id,
                    "⚠️ Sorry, mera bot group mein required admin permission nahi mila isliye aapko auto-approve nahi kar paya. Group admin se contact karein."
                )
            except:
                pass
        except Exception:
            # generic ignore to keep bot alive
            try:
                await app.send_message(
                    user.id,
                    "⚠️ Koi error aaya. Admin permissions check karo."
                )
            except:
                pass

        # ----- SEND PROMO / POSTS AFTER APPROVE -----
        for link in cfg.POSTS:
            try:
                chat_id, msg_id = parse_post_link(link)
                await app.copy_message(
                    chat_id=user.id,
                    from_chat_id=chat_id,
                    message_id=msg_id
                )
                await asyncio.sleep(1)
            except:
                pass

    except errors.PeerIdInvalid:
        # user has privacy settings or cannot be PMed
        pass
    except FloodWait as e:
        await asyncio.sleep(e.x if hasattr(e, "x") else e.value)
    except Exception:
        pass

#━━━━━━━━━━━━━━━━━━━━ START COMMAND ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    add_user(m.from_user.id)

    # NORMAL USER
    if m.from_user.id not in cfg.SUDO:
        await m.reply_text(
            "𝐁𝐇𝐀𝐈 𝐇𝐀𝐂𝐊 𝐒𝐄 𝐏𝐋𝐀𝐘 𝐊𝐑𝐎\n\n💸𝐏𝐑𝐎𝐅𝐈𝐓 𝐊𝐑𝐎🍻"
        )

        for link in cfg.POSTS:
            try:
                chat_id, msg_id = parse_post_link(link)
                await app.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=chat_id,
                    message_id=msg_id
                )
                await asyncio.sleep(1)
            except:
                pass
        return

    # ADMIN HOME (NO JOIN CHECK)
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🗯 ƈɦǟռռɛʟ", url="https://t.me/lnx_store"),
            InlineKeyboardButton("💬 Support", url="https://t.me/teacher_slex")
        ]]
    )

    await m.reply_photo(
        photo="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhsaR6kRdTPF2ZMEgmgSYjjXU6OcsJhkBe1EWtI1nfbOziINTYzxjlGCMSVh-KoH05Z8MpRWhVV9TIX_ykpjdeGqJ1atXy1TUqrVkohUxlykoZyl67EfMQppHoWYrdHmdi6FMcL9v-Vew2VtaWHWY_eGZt-GN057jLGvYj7UV49g0rXVxoDFXQAYxvaX1xP/s1280/75447.jpg",
        caption=(
            f"**🦊 Hello {m.from_user.mention}!**\n\n"
            "I'm an auto approve bot.\n"
            "I handle join requests & DM users.\n\n"
            "📢 Broadcast : /bcast\n"
            "📊 Users : /users\n\n"
            "__Powered By : @teacher_slex__"
        ),
        reply_markup=keyboard
    )

#━━━━━━━━━━━━━━━━━━━━ USERS COUNT ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def users_count(_, m: Message):
    u = all_users()
    g = all_groups()
    await m.reply_text(f"🙋 Users : `{u}`\n👥 Groups : `{g}`\n📊 Total : `{u+g}`")

#━━━━━━━━━━━━━━━━━━━━ BROADCAST COPY ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m: Message):
    status = await m.reply("⚡ Broadcasting...")
    ok = fail = 0
    for u in users.find():
        try:
            await m.reply_to_message.copy(u["user_id"])
            ok += 1
        except:
            fail += 1
    await status.edit(f"✅ {ok} | ❌ {fail}")

#━━━━━━━━━━━━━━━━━━━━ 🚫 AUTO DELETE ILLEGAL BOT MSG ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.me)
async def auto_delete_illegal(_, m: Message):
    try:
        content = ""
        if m.text:
            content = m.text.lower()
        elif m.caption:
            content = m.caption.lower()

        for word in cfg.ILLEGAL_WORDS:
            if word.lower() in content:
                await asyncio.sleep(0.1)
                await m.delete()
                return
    except:
        pass

print("🤖 Bot is Alive!")
app.run()
