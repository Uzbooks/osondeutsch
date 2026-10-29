"""Botning barcha matnlari bir joyda — tahrirlash oson bo'lsin."""

WELCOME = (
    "Assalomu alaykum, {name}! 👋\n\n"
    "<b>OsonDeutsch</b> — nemis tilini o'zbek tilida o'rganing: A1 dan C2 gacha "
    "grammatika, lug'at va Goethe imtihoniga tayyorgarlik.\n\n"
    "Pastdagi <b>📚 OsonDeutsch</b> tugmasini bosib darslarni oching."
)

CONSENT = (
    "📬 OsonDeutsch yangiliklari, yangi darslar va maxsus takliflar "
    "(jumladan reklama xabarlari) olishni xohlaysizmi?\n\n"
    "Rozi bo'lsangiz, Telegram'dagi ismingiz, familiyangiz va username'ingiz saqlanadi. "
    "Istalgan vaqtda /stop bilan obunani bekor qilishingiz, "
    "/delete bilan ma'lumotlaringizni butunlay o'chirishingiz mumkin.\n\n"
    "Batafsil: <a href=\"{privacy_url}\">Maxfiylik siyosati</a>"
)

CONSENT_YES = "✅ Roziman"
CONSENT_NO = "❌ Yo'q, rahmat"

CONSENT_THANKS = "Rahmat! ✅ Endi yangiliklar va takliflarni birinchilardan bo'lib olasiz."
CONSENT_DECLINED = (
    "Tushunarli 👍 Hech narsa saqlanmadi. Darslardan bemalol foydalanishingiz mumkin.\n"
    "Fikringiz o'zgarsa, /start bosing."
)

ASK_PHONE = (
    "📱 Xohlasangiz, telefon raqamingizni ham ulashing — muhim yangiliklarni "
    "o'tkazib yubormaslik uchun. Bu ixtiyoriy."
)
SHARE_PHONE = "📱 Raqamni ulashish"
SKIP = "O'tkazib yuborish"
PHONE_SAVED = "Raqamingiz saqlandi ✅"
PHONE_NOT_OWN = "Iltimos, faqat o'zingizning raqamingizni tugma orqali ulashing."
PHONE_SKIPPED = "Yaxshi 👍"
EMAIL_HINT = "Email orqali ham xabar olishni xohlasangiz: /email"

NEED_CONSENT = "Avval /start bosib, xabarlar olishga rozilik bering."
ASK_EMAIL = "✉️ Email manzilingizni yozing (bekor qilish: /cancel):"
EMAIL_INVALID = "Bu email manzilga o'xshamayapti. Qaytadan yozing yoki /cancel bosing."
EMAIL_SAVED = "Email saqlandi ✅"
CANCELLED = "Bekor qilindi."

STOPPED = (
    "Obuna bekor qilindi. Endi sizga reklama va yangilik xabarlari yuborilmaydi.\n"
    "Ma'lumotlaringizni butunlay o'chirish uchun: /delete"
)
NOT_SUBSCRIBED = "Sizning ma'lumotlaringiz saqlanmagan."

DELETE_CONFIRM = "⚠️ Barcha ma'lumotlaringiz (ism, telefon, email) butunlay o'chiriladi. Ishonchingiz komilmi?"
DELETE_YES = "Ha, o'chirilsin"
DELETE_NO = "Yo'q"
DELETED = "Ma'lumotlaringiz butunlay o'chirildi 🗑"

MY_DATA = (
    "🗂 <b>Saqlangan ma'lumotlaringiz:</b>\n"
    "Ism: {first_name}\nFamiliya: {last_name}\nUsername: {username}\n"
    "Telefon: {phone}\nEmail: {email}\n"
    "Xabarlar olish: {consent}\nRozilik sanasi: {consent_at}"
)

PRIVACY = "🔒 Maxfiylik siyosati: {privacy_url}"

HELP = (
    "<b>Buyruqlar:</b>\n"
    "/start — boshlash\n"
    "/email — email qo'shish\n"
    "/mydata — saqlangan ma'lumotlarim\n"
    "/privacy — maxfiylik siyosati\n"
    "/stop — xabarlar olishni to'xtatish\n"
    "/delete — ma'lumotlarimni o'chirish"
)

MENU_BUTTON = "📚 OsonDeutsch"
