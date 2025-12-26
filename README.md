<div align="center">

<a href="https://files.catbox.moe/081e7a.jpg">
  <img src="https://files.catbox.moe/081e7a.jpg" width="300" height="300" />
</a>

![Stars](https://img.shields.io/github/stars/LearningBotsOfficial/smm_panel_bot)
![Forks](https://img.shields.io/github/forks/LearningBotsOfficial/smm_panel_bot)

----------------------------------------------------
A **Telegram SMM Panel Bot** built with **Pyrogram** + **MongoDB** for managing SMM services, users, referrals, and payments

</div>

---

## ⭐ Features
- **Owner Commands**: `/addbal`, `/subbal`, `/setbal`, `/broadcast`  
- **User Management**: Balance checking, referral system, daily bonus, total stats  
- **Force Channel Subscription**: Users must join a channel before using the bot  
- **Interactive Inline Menu**: Balance, Pricing, Invite Friends, Statistics, Bonus, Help, Buy Services  
- **Service Menu**: Telegram Members, Reactions, Views (with min/max, refill, delivery info)  
- **Broadcast**: Supports text, photo, video, document, and audio messages to all users  
- **MongoDB Storage** for persistent user and order data  
- **Beautiful Inline UI** with buttons and modular code

---

<details>
<summary><b>🔸 Deploy on VPS / Localhost</b></summary>

### 1. Fork & Star ⭐
- Click **Fork** (top-right of GitHub repo)  
- Then click **Star** ⭐ to support this project!  

---

### 2. Get Your Fork URL
```
https://github.com/<your-username>/smm_panel_bot.git
```

---

### 3. Setup Your VPS
Install system packages:
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv tmux nano
```

---

### 4. Clone Your Fork
```
git clone https://github.com/your_account_username/smm_panel_bot
cd smm_panel_bot
python3 -m venv venv
source venv/bin/activate
```

---

### 5. Install Dependencies
```
pip install --upgrade pip && pip install -r requirements.txt
```

---

### 6. Configure the Bot
```
nano .evn
```

⚙️ required fields

```
# Telegram API
API_ID=
API_HASH=
BOT_TOKEN=

# MongoDB
MONGO_URI=
DB_NAME=

# Owner and Bot Info
OWNER_ID=
OWNER_USERNAME=

# Links & Visuals
SUPPORT_GROUP=
UPDATE_CHANNEL=
START_IMAGE=

# Force Join Channel
FORCE_CHANNEL=

# Bonuses & Referrals
REFERRER_BONUS=
DAILY_BONUS=

# QR Image
QR_IMAGE=

# SMM Panel Settings
SMM_API_KEY=

# Channel to receive order notifications
ORDER_CHANNEL=


```

✅ Save with: `Ctrl + O`, then Enter  
❌ Exit with: `Ctrl + X`

### 7. Run the Bot
```
tmux new -s groupbot
source venv/bin/activate
python3 bot.py
```

➡️ Detach (keep it running): `Ctrl + B`, then `D`

</details>

<div align="center">

### ☕ Support Me!

<a href="https://files.catbox.moe/4elv8g.jpg" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="45" width="190" alt="Buy Me a Coffee" />
</a>

</div>

---

## 📱 Connect with Me

<p align="center">
<a href="https://www.instagram.com/learning_bots"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white"></a>
<a href="https://t.me/LearningBotsCommunity"><img src="https://img.shields.io/badge/Telegram%20Group-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"></a>
<a href="https://t.me/learning_bots"><img src="https://img.shields.io/badge/Telegram%20Channel-0088cc?style=for-the-badge&logo=telegram&logoColor=white"></a>
<a href="https://youtube.com/@learning_bots?si=aNUuRSfZD7na78GM"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white"></a>
</p>

---

## ⚠️ License / Usage Terms

This project is open-source under a **custom license** by [Yash](https://github.com/LearningBotsOfficial).

✅ You Can:
- Use this code for personal or educational purposes  
- Host your own version **with proper credits**  
- Modify or improve the code (while keeping credit intact)

🚫 You Cannot:
- Remove author credits or change project name  
- Sell, rent, or resell this code or any modified version  
- Claim ownership or re-upload it without permission  

If you want to use this project commercially,  
please contact the author at [LearningBotsOfficial](https://t.me/LearningBotsOfficial).

---

**Author:** [LearningBotsOfficial](https://github.com/LearningBotsOfficial)  
**Support Group:** [@LearningBotsCommunity](https://t.me/LearningBotsCommunity)  
**Update Channel:** [@learning_bots](https://t.me/learning_bots)  
**YouTube:** [Learning Bots](https://youtube.com/@learning_bots)
