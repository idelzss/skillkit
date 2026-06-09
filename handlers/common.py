from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from buttons import get_main_menu_keyboard


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "👋 Вітаю! Це масштабний довідник софту для digital-сфери.\n\n"
        "Оберіть напрямок, щоб дізнатися про найкращі інструменти для роботи:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery):
    text = "Оберіть напрямок:"
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
