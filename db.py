# ============================================================
# Smm Panel Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

 
import logging
import math
import motor.motor_asyncio
from config import MONGO_URI, DB_NAME
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users = db["users"]
orders = db["orders"]
activity = db["activity"]
tg_account_stock = db["tg_account_stock"]

#heloers config
COUNTRIES_PER_PAGE = 12


# ---------------------------------------------------
# by account functions
# ---------------------------------------------------

async def upsert_country_stock(country: str, code: str, stock: int, price: int):
    await tg_account_stock.update_one(
        {"code": code},
        {"$set": {
            "country": country,
            "code": code,
            "stock": stock,
            "price": price,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


async def get_countries_sorted():
    cursor = tg_account_stock.find().sort(
        [("stock", -1), ("country", 1)]
    )
    return await cursor.to_list(length=1000)



async def get_countries_page(page: int):
    skip = (page - 1) * COUNTRIES_PER_PAGE

    cursor = tg_account_stock.find().sort(
        [("stock", -1), ("country", 1)]
    ).skip(skip).limit(COUNTRIES_PER_PAGE)

    return await cursor.to_list(length=COUNTRIES_PER_PAGE)

async def get_total_country_pages():
    total = await tg_account_stock.count_documents({})
    return math.ceil(total / COUNTRIES_PER_PAGE)


async def reduce_country_stock(code: str, qty: int = 1):
    await tg_account_stock.update_one(
        {"code": code, "stock": {"$gte": qty}},
        {"$inc": {"stock": -qty}}
    )


# ---------------------------------------------------
# User functions
# --------------------------------------------------
 
async def log_activity(user_id: int, action: str):
    await activity.insert_one({
        "user_id": user_id,
        "action": action,
        "time": datetime.utcnow()
    })


async def user_exists(user_id: int) -> bool:
    return await users.find_one({"_id": user_id}) is not None


async def add_user(user_id: int, name: str, referred_by: int | None = None):
    await users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {
            "_id": user_id,
            "name": name,
            "balance": 0,
            "orders": 0,
            "referred_by": referred_by,
            "refs": 0,
            "last_bonus": None
        }},
        upsert=True
    )


async def add_balance(user_id: int, amount: float):
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )


async def check_balance(user_id: int) -> float:
    user = await users.find_one({"_id": user_id})
    return user.get("balance", 0) if user else 0


async def add_ref(user_id: int):
    await users.update_one({"_id": user_id}, {"$inc": {"refs": 1}})


async def get_referrals(user_id: int) -> int:
    user = await users.find_one({"_id": user_id}, {"refs": 1})
    return user.get("refs", 0) if user else 0


async def total_users() -> int:
    return await users.count_documents({})


async def total_orders() -> int:
    return await orders.count_documents({})


async def get_last_bonus(user_id: int):
    user = await users.find_one({"_id": user_id}, {"last_bonus": 1})
    return user.get("last_bonus") if user else None


async def set_last_bonus(user_id: int):
    await users.update_one(
        {"_id": user_id},
        {"$set": {"last_bonus": datetime.utcnow()}},
        upsert=True
    )


# ---------------------------------------------------
# Order functions
# ---------------------------------------------------

async def create_order(user_id: int, service_id: int, link: str, quantity: int, amount: float, api_order_id: int):
    await orders.insert_one({
        "user_id": user_id,
        "service_id": service_id,
        "link": link,
        "quantity": quantity,
        "amount": amount,
        "api_order_id": api_order_id,
        "status": "pending",
        "time": datetime.utcnow()
    })
    await users.update_one({"_id": user_id}, {"$inc": {"orders": 1}})


async def update_order_status(api_order_id: int, new_status: str):
    await orders.update_one({"api_order_id": api_order_id}, {"$set": {"status": new_status}})


async def get_user_orders(user_id: int):
    cursor = orders.find({"user_id": user_id}).sort("time", -1)
    return await cursor.to_list(None)


async def get_order_by_api(api_order_id: int):
    return await orders.find_one({"api_order_id": api_order_id})
