from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_all_categories, get_professions_by_category


def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    categories = get_all_categories()
    for cat in categories:
        builder.button(text=cat["name"], callback_data=f"cat_{cat['id']}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="💡 Запропонувати додавання", callback_data="suggest_start"))
    return builder.as_markup()


def get_professions_keyboard(cat_id: str):
    builder = InlineKeyboardBuilder()
    professions = get_professions_by_category(cat_id)
    for prof in professions:
        builder.button(text=prof["name"], callback_data=f"prof_{cat_id}_{prof['id']}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад до Головного меню", callback_data="back_to_main"))
    return builder.as_markup()


def get_back_to_professions_keyboard(cat_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад до професій", callback_data=f"cat_{cat_id}")
    return builder.as_markup()
