from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_category_by_id, get_profession_by_id, get_software_by_profession
from buttons import get_professions_keyboard, get_back_to_professions_keyboard


router = Router()


@router.callback_query(F.data.startswith("cat_"))
async def process_category_selection(callback: CallbackQuery):
    cat_id = callback.data.split("_")[1]

    cat = get_category_by_id(cat_id)
    if not cat:
        await callback.answer("Помилка: напрямок не знайдено.")
        return

    text = f"📂 Напрямок: <b>{cat['name']}</b>\n\nОберіть професію, щоб побачити софт:"
    await callback.message.edit_text(
        text,
        reply_markup=get_professions_keyboard(cat_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("prof_"))
async def process_profession_selection(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    cat_id = parts[1]
    prof_id = parts[2]

    prof = get_profession_by_id(prof_id)
    if not prof:
        await callback.answer("Помилка: професію не знайдено.")
        return

    software_list = get_software_by_profession(prof_id)

    text = f"🛠 Софт для професії: <b>{prof['name']}</b>\n\n"
    for sw in software_list:
        text += f"🔹 <b>{sw['name']}</b> ({sw['type']})\n"
        text += f"<i>{sw['desc']}</i>\n"
        text += f"💡 <b>Фішка:</b> {sw['feature']}\n"
        if sw['url'].startswith("http"):
            text += f"🔗 <a href='{sw['url']}'>Посилання на сайт</a>\n"
        else:
            text += f"🔗 {sw['url']}\n"
            
        if sw.get('youtube_tutorial'):
            text += f"▶️ <a href='{sw['youtube_tutorial']}'>Туторіал на YouTube</a>\n\n"
        else:
            text += "\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_professions_keyboard(cat_id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
