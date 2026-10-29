# OsonDeutsch Telegram boti

## Bot nima qiladi
- Menyu tugmasi orqali OsonDeutsch saytini Telegram ichida (Mini App) ochadi
- Foydalanuvchidan aniq rozilik so'raydi, faqat rozilik berganlarni saqlaydi
- Telefon va email — ixtiyoriy
- Foydalanuvchi: `/mydata`, `/stop`, `/delete`, `/privacy`
- Admin (siz): `/stats`, `/broadcast`

## 1. Bot yaratish
1. Telegramda @BotFather → `/newbot` → nom bering → **token**ni oling.
2. O'z Telegram ID'ingizni @userinfobot orqali bilib oling.

## 2. Kompyuterda ishga tushirish
```bash
pip install -r requirements.txt
cp .env.example .env      # Windows'da: copy .env.example .env
```
`.env` faylini oching va token, sayt manzili, ID'ingizni yozing. Keyin:
```bash
python bot.py
```
Botga `/start` yozib tekshiring.

## 3. Maxfiylik siyosati
`privacy.html` faylini sayt repository'ingizga qo'shing. U GitHub Pages'da
`https://username.github.io/osondeutsch/privacy.html` manzilida ochiladi.
Ichidagi `[Ism Familiya]`, `[email@manzil]` kabi joylarni to'ldiring.

## 4. Reklama yuborish
Botga yubormoqchi bo'lgan xabaringizni (matn, rasm yoki video) yuboring,
so'ng **shu xabarga javob (reply) qilib** `/broadcast` yozing.
Xabar faqat rozilik berganlarga boradi.

## ⚠️ Muhim
- `.env` va `osondeutsch.db` fayllari **hech qachon** GitHub'ga yuklanmasin
  (`.gitignore` buni oldini oladi).
- Bot doim ishlab turishi uchun uni serverga qo'yish kerak (kompyuter o'chsa bot ham to'xtaydi).
- `osondeutsch.db` faylining zaxira nusxasini muntazam oling.
