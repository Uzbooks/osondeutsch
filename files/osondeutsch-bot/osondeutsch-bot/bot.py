"""OsonDeutsch Telegram boti.

- Saytni Mini App sifatida ochadi (menyu tugmasi)
- Faqat aniq rozilik bilan foydalanuvchi ma'lumotlarini saqlaydi
- /stop, /delete, /mydata — foydalanuvchi o'z ma'lumotlarini boshqaradi
- Adminlar uchun: /stats va /broadcast (faqat rozilik berganlarga)
"""
import asyncio
import html
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, MenuButtonWebApp, Message, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, WebAppInfo,
)
from dotenv import load_dotenv

import texts as T
from db import Database

load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]
PRIVACY_URL = os.environ["PRIVACY_URL"]
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
DB_PATH = os.getenv("DB_PATH", "osondeutsch.db")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

db = Database(DB_PATH)
router = Router()


class EmailForm(StatesGroup):
    waiting = State()


def open_app_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=T.MENU_BUTTON, web_app=WebAppInfo(url=WEBAPP_URL))
    ]])


def consent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=T.CONSENT_YES, callback_data="consent:yes"),
        InlineKeyboardButton(text=T.CONSENT_NO, callback_data="consent:no"),
    ]])


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=T.SHARE_PHONE, request_contact=True)],
                  [KeyboardButton(text=T.SKIP)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


# ---------- Boshlash va rozilik ----------

@router.message(CommandStart())
async def start(message: Message) -> None:
    name = html.escape(message.from_user.first_name or "")
    await message.answer(T.WELCOME.format(name=name), reply_markup=open_app_kb())
    user = await db.get_user(message.from_user.id)
    if not user or not user["marketing_consent"]:
        await message.answer(T.CONSENT.format(privacy_url=PRIVACY_URL),
                             reply_markup=consent_kb(), disable_web_page_preview=True)


@router.callback_query(F.data == "consent:yes")
async def consent_yes(cb: CallbackQuery) -> None:
    u = cb.from_user
    await db.save_consent(u.id, u.first_name, u.last_name, u.username)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(T.CONSENT_THANKS)
    user = await db.get_user(u.id)
    if not user["phone"]:
        await cb.message.answer(T.ASK_PHONE, reply_markup=phone_kb())
    await cb.answer()


@router.callback_query(F.data == "consent:no")
async def consent_no(cb: CallbackQuery) -> None:
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(T.CONSENT_DECLINED)
    await cb.answer()


# ---------- Telefon (ixtiyoriy) ----------

@router.message(F.contact)
async def got_contact(message: Message) -> None:
    if message.contact.user_id != message.from_user.id:
        await message.answer(T.PHONE_NOT_OWN, reply_markup=phone_kb())
        return
    if not await db.get_user(message.from_user.id):
        await message.answer(T.NEED_CONSENT, reply_markup=ReplyKeyboardRemove())
        return
    await db.set_phone(message.from_user.id, message.contact.phone_number)
    await message.answer(T.PHONE_SAVED, reply_markup=ReplyKeyboardRemove())
    await message.answer(T.EMAIL_HINT)


@router.message(F.text == T.SKIP)
async def skip_phone(message: Message) -> None:
    await message.answer(T.PHONE_SKIPPED, reply_markup=ReplyKeyboardRemove())
    await message.answer(T.EMAIL_HINT)


# ---------- Email (ixtiyoriy) ----------

@router.message(Command("email"))
async def ask_email(message: Message, state: FSMContext) -> None:
    if not await db.get_user(message.from_user.id):
        await message.answer(T.NEED_CONSENT)
        return
    await state.set_state(EmailForm.waiting)
    await message.answer(T.ASK_EMAIL)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(T.CANCELLED, reply_markup=ReplyKeyboardRemove())


@router.message(EmailForm.waiting, F.text)
async def got_email(message: Message, state: FSMContext) -> None:
    email = message.text.strip().lower()
    if not EMAIL_RE.match(email) or len(email) > 254:
        await message.answer(T.EMAIL_INVALID)
        return
    await db.set_email(message.from_user.id, email)
    await state.clear()
    await message.answer(T.EMAIL_SAVED)


# ---------- Foydalanuvchi huquqlari ----------

@router.message(Command("mydata"))
async def my_data(message: Message) -> None:
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer(T.NOT_SUBSCRIBED)
        return
    show = lambda v: html.escape(str(v)) if v else "—"
    await message.answer(T.MY_DATA.format(
        first_name=show(user["first_name"]), last_name=show(user["last_name"]),
        username=show(user["username"]), phone=show(user["phone"]),
        email=show(user["email"]),
        consent="ha ✅" if user["marketing_consent"] else "yo'q ❌",
        consent_at=show(user["consent_at"]),
    ))


@router.message(Command("stop"))
async def stop(message: Message) -> None:
    if not await db.get_user(message.from_user.id):
        await message.answer(T.NOT_SUBSCRIBED)
        return
    await db.revoke_consent(message.from_user.id)
    await message.answer(T.STOPPED)


@router.message(Command("delete"))
async def delete_ask(message: Message) -> None:
    if not await db.get_user(message.from_user.id):
        await message.answer(T.NOT_SUBSCRIBED)
        return
    await message.answer(T.DELETE_CONFIRM, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=T.DELETE_YES, callback_data="delete:yes"),
        InlineKeyboardButton(text=T.DELETE_NO, callback_data="delete:no"),
    ]]))


@router.callback_query(F.data.startswith("delete:"))
async def delete_answer(cb: CallbackQuery) -> None:
    await cb.message.edit_reply_markup(reply_markup=None)
    if cb.data == "delete:yes":
        await db.delete_user(cb.from_user.id)
        await cb.message.answer(T.DELETED)
    else:
        await cb.message.answer(T.CANCELLED)
    await cb.answer()


@router.message(Command("privacy"))
async def privacy(message: Message) -> None:
    await message.answer(T.PRIVACY.format(privacy_url=PRIVACY_URL))


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer(T.HELP)


# ---------- Admin ----------

@router.message(Command("stats"), F.from_user.id.in_(ADMIN_IDS))
async def stats(message: Message) -> None:
    s = await db.stats()
    await message.answer(
        f"👥 Jami: {s['total']}\n✅ Xabar olishga rozi: {s['consented']}\n"
        f"📱 Telefon bor: {s['phones']}\n✉️ Email bor: {s['emails']}"
    )


@router.message(Command("broadcast"), F.from_user.id.in_(ADMIN_IDS))
async def broadcast(message: Message, bot: Bot) -> None:
    """Ishlatish: yubormoqchi bo'lgan xabarga (matn, rasm, video...) javob qilib /broadcast yozing."""
    src = message.reply_to_message
    if not src:
        await message.answer("Yubormoqchi bo'lgan xabarga javob (reply) qilib /broadcast yozing.")
        return
    ids = await db.consented_ids()
    sent = failed = 0
    await message.answer(f"⏳ {len(ids)} kishiga yuborilmoqda...")
    for uid in ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=src.chat.id, message_id=src.message_id)
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=src.chat.id, message_id=src.message_id)
                sent += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            # Foydalanuvchi botni bloklagan — boshqa xabar yubormaymiz
            await db.revoke_consent(uid)
            failed += 1
        except TelegramBadRequest:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram limiti: soniyasiga ~30 xabar
    await message.answer(f"✅ Yuborildi: {sent}\n❌ Yuborilmadi: {failed}")


# ---------- Ishga tushirish ----------

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await db.init()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text=T.MENU_BUTTON, web_app=WebAppInfo(url=WEBAPP_URL))
    )
    await bot.set_my_commands([
        BotCommand(command="start", description="Boshlash"),
        BotCommand(command="email", description="Email qo'shish"),
        BotCommand(command="mydata", description="Saqlangan ma'lumotlarim"),
        BotCommand(command="privacy", description="Maxfiylik siyosati"),
        BotCommand(command="stop", description="Xabarlarni to'xtatish"),
        BotCommand(command="delete", description="Ma'lumotlarimni o'chirish"),
    ])
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
