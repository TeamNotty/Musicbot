# ============================================================
# Smm Panel Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
import aiohttp
from config import SMM_SITE, ORDER_CHANNEL
from db import create_order, users
from datetime import datetime

PROFIT_MULTIPLIER = 2  # User price will be API price * PROFIT_MULTIPLIER

# ============================================================
# Temporary order storage
# ============================================================
def init_temp(app: Client):
    if not hasattr(app, "order_temp"):
        app.order_temp = {}

# ============================================================
# Helper - safely extract readable text (link/caption/entities)
# ============================================================
def _extract_message_text(message: Message) -> str:
    if getattr(message, "text", None):
        return message.text.strip()
    if getattr(message, "caption", None):
        return message.caption.strip()
    if message.entities:
        for ent in message.entities:
            if getattr(ent, "type", "") == "text_link" and getattr(ent, "url", None):
                return ent.url.strip()
    return ""

# ============================================================
# Show main service menu
# ============================================================
async def cb_services(client: Client, callback: CallbackQuery):
    text = "🛒 **Buy Services**\nChoose a category:"
    btns = [
        [InlineKeyboardButton("Reaction 😉", callback_data="service_reaction"),
         InlineKeyboardButton("Members 👥", callback_data="service_members")],
        [InlineKeyboardButton("Views 👁️", callback_data="service_views")],
        [InlineKeyboardButton("Back 🔙", callback_data="cb_back")]
    ]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
    await callback.answer()

# ============================================================
# Fetch packages from API
# ============================================================
async def fetch_packages():
    payload = {"key": SMM_SITE["api_key"], "action": "services"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SMM_SITE["api_url"], data=payload) as resp:
                return await resp.json()
    except Exception as e:
        print("Fetch Error:", e)
        return []

# ============================================================
# Select service
# ============================================================
async def cb_service_select(client: Client, callback: CallbackQuery):
    init_temp(client)
    data = callback.data
    if not data.startswith("service_"):
        return

    service_name = data.split("_", 1)[1]
    service_id = SMM_SITE["services"].get(service_name)
    if not service_id:
        await callback.answer("❌ Invalid service!", show_alert=True)
        return

    await callback.message.edit_text(f"📦 Fetching {service_name} packages...")
    packages = await fetch_packages()
    if not packages or not isinstance(packages, list):
        await callback.message.edit_text(
            f"❌ Failed to fetch {service_name} packages.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back 🔙", callback_data="cb_services")]])
        )
        return

    available = [p for p in packages if p.get("service") == service_id]
    if not available:
        await callback.message.edit_text(
            f"❌ No packages available for {service_name}.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back 🔙", callback_data="cb_services")]])
        )
        return

    user_id = callback.from_user.id
    client.order_temp.setdefault(user_id, {})
    client.order_temp[user_id]["available_packages"] = available
    client.order_temp[user_id]["available_for"] = service_name

    btns = []
    for idx, pkg in enumerate(available):
        pkg_name = pkg.get("name", "Package")
        api_rate = float(pkg.get("rate", 0) or 0)
        user_rate = api_rate * PROFIT_MULTIPLIER
        # Save user_rate in package for later
        pkg["rate_user"] = user_rate
        pkg["rate_api"] = api_rate
        btns.append([InlineKeyboardButton(
            f"{pkg_name} - {user_rate:.4f} coins",
            callback_data=f"order_{service_name}_{idx}"
        )])
    btns.append([InlineKeyboardButton("Back 🔙", callback_data="cb_services")])

    await callback.message.edit_text(
        f"📦 Packages for **{service_name.capitalize()}**:",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    await callback.answer()

# ============================================================
# Start order package
# ============================================================
async def cb_order_package(client: Client, callback: CallbackQuery):
    init_temp(client)
    parts = callback.data.split("_")
    if len(parts) < 3:
        return await callback.answer("❌ Invalid selection.", show_alert=True)

    _, service_name, idx_str = parts
    try:
        pkg_idx = int(idx_str)
    except ValueError:
        return await callback.answer("❌ Invalid package index.", show_alert=True)

    user_id = callback.from_user.id
    user_temp = client.order_temp.setdefault(user_id, {})
    available = user_temp.get("available_packages")
    available_for = user_temp.get("available_for")

    if not available or available_for != service_name:
        packages = await fetch_packages()
        service_id = SMM_SITE["services"].get(service_name)
        available = [p for p in packages if p.get("service") == service_id]
        user_temp["available_packages"] = available
        user_temp["available_for"] = service_name

    if pkg_idx < 0 or pkg_idx >= len(available):
        return await callback.answer("❌ Invalid package selected.", show_alert=True)

    pkg = available[pkg_idx]

    # Save selected package with user price
    service_id = pkg.get("service") or pkg.get("id") or pkg.get("service_id") or 0
    client.order_temp[user_id] = {
        "service_id": int(service_id),
        "service_name": service_name,
        "package": pkg,
        "rate_api": float(pkg.get("rate_api", 0)),
        "rate_user": float(pkg.get("rate_user", 0)),
        "step": "link"
    }

    await callback.message.edit_text("📎 Send the **link** where you want the service delivered:")
    await callback.answer()

# ============================================================
# Handle order steps (link -> quantity -> confirm)
# ============================================================
async def handle_order_steps(client: Client, message: Message):
    init_temp(client)
    user_id = message.from_user.id
    user_order = client.order_temp.get(user_id)
    if not user_order:
        return

    step = user_order.get("step")
    text = _extract_message_text(message)

    if step == "link":
        if not text:
            return await message.reply("📎 Please send the **link** where you want the service applied.")
        user_order["link"] = text
        user_order["step"] = "qty"
        await message.reply("🔢 Now send **quantity** you want:")
        return

    if step == "qty":
        qty_text = text.replace(",", "").strip()
        if not qty_text.isdigit():
            return await message.reply("❌ Quantity must be a number. Send again:")
        user_order["qty"] = int(qty_text)
        user_order["step"] = "confirm"
        user_order["created_at"] = datetime.utcnow().isoformat()

        # Calculate total price
        qty = user_order.get("qty", 0)
        unit_price_user = float(user_order.get("rate_user", 0))  # your selling price
        total_price = (qty / 1000) * unit_price_user  # total price user will pay

        await message.reply(
            "🧾 Confirm your order:\n\n"
            f"🔹 Service: {user_order.get('service_name')}\n"
            f"🔹 Link: {user_order.get('link')}\n"
            f"🔹 Quantity: {qty}\n"
            f"🔹 Total price: {total_price:.4f} coins\n\nProceed?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✔ Confirm", callback_data="confirm_order")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")]
            ])
        )
        return


# ============================================================
# Confirm order
# ============================================================
async def cb_confirm_order(client: Client, callback: CallbackQuery):
    init_temp(client)
    user_id = callback.from_user.id
    order = client.order_temp.get(user_id)
    if not order or order.get("step") != "confirm":
        return await callback.answer("Session expired!", show_alert=True)

    qty = order.get("qty", 0)
    unit_price_api = float(order.get("rate_api", 0))
    unit_price_user = float(order.get("rate_user", 0))
    price = (qty / 1000) * unit_price_user

    # Check user balance
    user_data = await users.find_one({"_id": user_id})
    balance = float(user_data.get("balance", 0)) if user_data else 0
    if balance < price:
        return await callback.answer(
            f"❌ Not enough balance!\nRequired: {price:.4f}\nYour balance: {balance}",
            show_alert=True
        )

    await users.update_one({"_id": user_id}, {"$inc": {"balance": -price}})

    payload = {
        "key": SMM_SITE["api_key"],
        "action": "add",
        "service": order.get("service_id"),
        "link": order.get("link"),
        "quantity": qty
    }
    api_order_id = 0
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SMM_SITE["api_url"], data=payload) as resp:
                res = await resp.json()
                api_order_id = res.get("order", 0)
    except Exception as e:
        print("Order Error:", e)

    await create_order(
        user_id=user_id,
        service_id=order.get("service_id"),
        link=order.get("link"),
        quantity=qty,
        amount=price,
        api_order_id=api_order_id
    )

    try:
        await client.send_message(
            ORDER_CHANNEL,
            f"📦 **New Order**\n"
            f"👤 User: {callback.from_user.first_name} ({user_id})\n"
            f"🛒 Service: {order.get('service_name')}\n"
            f"🔗 Link: {order.get('link')}\n"
            f"📌 Quantity: {qty}\n"
            f"💰 Price: {price:.4f} coins\n"
            f"🧾 API Order ID: {api_order_id}"
        )
    except Exception as e:
        print("ORDER_CHANNEL Error:", e)

    await callback.message.edit_text(
        "🎉 Order placed successfully!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back to Services", callback_data="cb_services")]
        ])
    )

    if user_id in client.order_temp:
        del client.order_temp[user_id]

    await callback.answer("✅ Order placed!")

# ============================================================
# Cancel order
# ============================================================
async def cb_cancel_order(client: Client, callback: CallbackQuery):
    init_temp(client)
    user_id = callback.from_user.id
    if user_id in client.order_temp:
        del client.order_temp[user_id]
    await callback.message.edit_text("❌ Order canceled.")
    await callback.answer()

# ============================================================
# Register handlers
# ============================================================
def register_services_handlers(app: Client):
    init_temp(app)

    @app.on_callback_query(filters.regex("^cb_services$"))
    async def _cb_services(c, q):
        await cb_services(c, q)

    @app.on_callback_query(filters.regex("^service_(reaction|members|views)$"))
    async def _cb_service_select(c, q):
        await cb_service_select(c, q)

    @app.on_callback_query(filters.regex(r"^order_(reaction|members|views)_\d+$"))
    async def _cb_order_package(c, q):
        await cb_order_package(c, q)

    @app.on_callback_query(filters.regex("^confirm_order$"))
    async def _cb_confirm(c, q):
        await cb_confirm_order(c, q)

    @app.on_callback_query(filters.regex("^cancel_order$"))
    async def _cb_cancel(c, q):
        await cb_cancel_order(c, q)

    @app.on_message(filters.private & ~filters.command("start"))
    async def _handle_order_steps(c: Client, m: Message):
        await handle_order_steps(c, m)

    print("✅ Service handlers loaded")
