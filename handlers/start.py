# ============================================================
# Smm Panel Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message
from pyrogram.errors import FloodWait, RPCError, PeerIdInvalid
from datetime import datetime, timedelta
import asyncio
import logging
from config import REFERRER_BONUS, OWNER_USERNAME, FORCE_CHANNEL, QR_IMAGE, DAILY_BONUS
import db

OWNER_ID = 7907656673

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)   

CHANNEL = FORCE_CHANNEL.replace("@", "")
broadcast_state = {}

async def notify_user(client, user_id, msg):
    try:
        await client.send_message(user_id, msg)
    except:
        pass


async def check_force_sub(client, user_id):
    try:

        user = await client.get_chat_member(FORCE_CHANNEL, user_id)

        if user.status in ["left", "kicked"]:
            return False

        return True

    except FloodWait as e:

        await asyncio.sleep(e.value)
        return await check_force_sub(client, user_id)

    except PeerIdInvalid:
        return "INVALID_CHANNEL"

    except RPCError as e:
        if "chat_admin_required" in str(e).lower() or "not enough rights" in str(e).lower():
            return False
        return False




def register_start_handler(app: Client):

    async def start_menu(message, user):
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Balance", callback_data="cb_balance"),
             InlineKeyboardButton("💳 Pricing", callback_data="cb_pricing")],
            [InlineKeyboardButton("🗣 Invite Friends", callback_data="cb_invite"),
             InlineKeyboardButton("🌐 Statistics", callback_data="cb_stats")],
            [InlineKeyboardButton("🎉 Bonus", callback_data="cb_bonus"),
             InlineKeyboardButton("🆘 Help", callback_data="cb_help")],
            [InlineKeyboardButton("🛒 Buy Services", callback_data="cb_services")]
        ])
        await message.reply(f"Hey {user.first_name} 👋\nWelcome to Panel Bot 🚀", reply_markup=btns)

    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client, message):
        user = message.from_user
        args = message.text.split()
        ref_id = None

        status = await check_force_sub(client, user.id)
        
        if status != True:
            await message.reply(
                "🚫 You must join our channel to use this bot!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL}")],
                    [InlineKeyboardButton("✅ Try Again", callback_data="cb_start")]
                ])
            )
            return


        if len(args) == 2:
            try:
                ref_id = int(args[1])
            except:
                ref_id = None

        is_new = not await db.user_exists(user.id)
        await db.add_user(user.id, user.first_name, referred_by=ref_id if is_new else None)

        if ref_id and ref_id != user.id and is_new:
            await db.add_balance(ref_id, REFERRER_BONUS)
            await notify_user(client, ref_id, f"🎉 New referral joined!\n💰 {REFERRER_BONUS} coins added.")

        await start_menu(message, user)

    @app.on_callback_query(filters.regex("^cb_start$"))
    async def cb_start_menu(client, callback):

        if not await check_force_sub(client, callback.from_user.id):
            await callback.answer("⚠️ Please join the channel first!", show_alert=True)
            return

        try:
            await callback.message.delete()
        except:
            pass

        await start_menu(callback.message, callback.from_user)


 
    # ------------------------------------------------------------
    # Subtract Balance
    # ------------------------------------------------------------
    
    @app.on_message(filters.command("subbal") & filters.user(OWNER_ID))
    async def subtract_balance_cmd(client, message):
        try:
            _, user_id, amount = message.text.split()
            user_id = int(user_id)
            amount = float(amount)
    
            await db.users.update_one(
                {"_id": user_id},
                {"$inc": {"balance": -amount}}
            )
    
            await message.reply(f"✅ Subtracted **{amount} coins** from user {user_id}")
    
        except:
            await message.reply("❌ Usage: /subbal user_id amount")
    
    
    # ------------------------------------------------------------
    # Set Balance
    # ------------------------------------------------------------
    
    @app.on_message(filters.command("setbal") & filters.user(OWNER_ID))
    async def set_balance_cmd(client, message):
        try:
            _, user_id, amount = message.text.split()
            user_id = int(user_id)
            amount = float(amount)
    
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"balance": amount}}
            )
    
            await message.reply(
                f"🟢 Balance updated: {user_id} now has **{amount} coins**"
            )
    
        except:
            await message.reply("❌ Usage: /setbal user_id amount")
    
    
    @app.on_callback_query(filters.regex("^cb_balance$"))
    async def cb_balance(client, callback):
        user_id = callback.from_user.id
        balance = await db.check_balance(user_id)
        await callback.answer(f"💰 Your balance: {balance} coins", show_alert=True)
    
    
    # ------------------------------------------------------------
    # Add Balance
    # ------------------------------------------------------------
    
    @app.on_message(filters.command("addbal") & filters.user(OWNER_ID))
    async def add_balance_cmd(client, message):
        try:
            _, user_id, amount = message.text.split()
            user_id = int(user_id)
            amount = float(amount)
    
            await db.users.update_one(
                {"_id": user_id},
                {"$inc": {"balance": amount}}
            )
    
            await message.reply(f"✅ Added **{amount} coins** to user {user_id}")
    
        except:
            await message.reply("❌ Usage: /addbal user_id amount")

            
# ------------------------------------------------------------
# Broadcast
# ------------------------------------------------------------
    
    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
    async def broadcast_start(client: Client, message: Message):
        broadcast_state[OWNER_ID] = True
        await message.reply("📢 Send the message you want to broadcast (text or media).")
    
    
    @app.on_message(filters.user(OWNER_ID)  & filters.reply)
    async def broadcast_handler(client: Client, message: Message):
        if not broadcast_state.get(OWNER_ID):
            return
    
        broadcast_state.pop(OWNER_ID)
        sent = 0
        failed = 0
    
        async for user in db.users.find({}):
            user_id = user["_id"]
    
            try:
                if message.text:
                    await client.send_message(user_id, message.text)
    
                elif message.photo:
                    await client.send_photo(
                        user_id,
                        photo=message.photo.file_id,
                        caption=message.caption or ""
                    )
    
                elif message.video:
                    await client.send_video(
                        user_id,
                        video=message.video.file_id,
                        caption=message.caption or ""
                    )
    
                elif message.document:
                    await client.send_document(
                        user_id,
                        document=message.document.file_id,
                        caption=message.caption or ""
                    )
    
                elif message.audio:
                    await client.send_audio(
                        user_id,
                        audio=message.audio.file_id,
                        caption=message.caption or ""
                    )
    
                else:
                    continue
    
                sent += 1
    
            except:
                failed += 1
                continue
    
        await message.reply(
            f"📢 Broadcast Completed!\n"
            f"✅ Sent: {sent}\n"
            f"❌ Failed: {failed}"
        )



    @app.on_callback_query(filters.regex("^cb_pricing$"))
    async def cb_pricing(client, callback):
        text = """
📦 Our Services:
        
👥 Telegram Members  
⌛ Start: Instant  
⚡ Speed: 700K/day  
♛ Min: 1000 | Max: 500K  
♻ Refill: 60 Days  
💎 Quality: Real Mix  
❤️ Non-Drop: 60 Days  
🚀 Delivery: Ultra Fast  
🔗 Link: Public Channel/Group  
        
- - - - - - - - - - - - - - - 
        
👍 Reactions Service  
♻ Refill: No  
♛ Min: 10 | Max: 1,000,000+  
🎁 Free Views Included  
⚡ Delivery: Super Fast  
🔗 Link: Post Link  
        
- - - - - - - - - - - - - - - 
        
👀 Views Service  
⚡ Ultra Fast Delivery  
♛ Min: 10  
🔗 Works on Public Posts  
💰 Cheapest & Safe  
        
💡 Contact the owner below for more info.
        """

    
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("Send Screenshot 🛍️", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("Back 🔙", callback_data="cb_back")]
        ])
    
        try:
 
            await callback.message.delete()
            
            await client.send_photo(
                chat_id=callback.message.chat.id,
                photo=QR_IMAGE,
                caption=text,
                reply_markup=btns
            )
            await callback.answer()
        
        except Exception as e:
            print(f"⚠️ Error sending new message in cb_pricing: {e}")
            await callback.answer("❌ Failed to send message", show_alert=True)


    @app.on_callback_query(filters.regex("^cb_back$"))
    async def cb_back(client, callback):
        try:
            await callback.message.delete()
        except:
            pass
    
        await callback.message.reply(
            f"Hey {callback.from_user.first_name} 👋\nWelcome to Panel Bot 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Balance", callback_data="cb_balance"),
                 InlineKeyboardButton("💳 Pricing", callback_data="cb_pricing")],
                [InlineKeyboardButton("🗣 Invite Friends", callback_data="cb_invite"),
                 InlineKeyboardButton("🌐 Statistics", callback_data="cb_stats")],
                [InlineKeyboardButton("🎉 Bonus", callback_data="cb_bonus"),
                 InlineKeyboardButton("🆘 Help", callback_data="cb_help")],
                [InlineKeyboardButton("🛒 Buy Services", callback_data="cb_services")]
            ])
        )


    @app.on_callback_query(filters.regex("^cb_invite$"))
    async def cb_invite_callback(client, callback):
        user_id = callback.from_user.id
        referred = await db.get_referrals(user_id)
        
        text = f"""
Invite your friends and earn rewards 🎉

Per Referral: {REFERRER_BONUS} coins
Total Referred: {referred}
        """
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Back 🔙", callback_data="cb_back")
            ]
        ])

        await callback.message.edit_text(
            text=text,
            reply_markup=btns
        )
        await callback.answer()


    @app.on_callback_query(filters.regex("^cb_stats$"))
    async def cb_stats_callback(client, callback):
        user_id = callback.from_user.id
        stats = await db.total_users()
        orders = await db.total_orders()

        text = f"""
📊 Bot Statistics:

👥 Total Users: {stats}
🛒 Total Orders: {orders}
"""
        
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Back 🔙", callback_data="cb_back")
            ]
        ])

        await callback.answer(text, show_alert=True)



    @app.on_callback_query(filters.regex("^cb_bonus$"))
    async def cb_bonus(client, callback):
        user_id = callback.from_user.id
        last = await db.get_last_bonus(user_id)  
    
        if last:
            next_time = last + timedelta(hours=24)
            if datetime.utcnow() < next_time:
                remaining = next_time - datetime.utcnow()
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
    
                await callback.answer(
                    f"⏳ You already claimed bonus!\nCome back in {hours}h {minutes}m.",
                    show_alert=True
                )
                return
    
        await db.add_balance(user_id, DAILY_BONUS)
        await db.set_last_bonus(user_id)
    
        await callback.answer(
            f"🎉 Bonus claimed!\nYou received {DAILY_BONUS} coins.",
            show_alert=True
        )


    @app.on_callback_query(filters.regex("^cb_help$"))
    async def cb_help(client, callback):
        text = (
            "🆘 **Help & Support**\n\n"
            "If you face any issue or have questions, please contact us.\n"
            "We are here to help you anytime!"
        )
    
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Owner 🛠", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("Back 🔙", callback_data="cb_back")]
        ])
    
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=btns
            )
            await callback.answer()
        except Exception:
            await callback.answer()

        