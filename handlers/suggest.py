from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import get_all_categories, get_professions_by_category, add_item_request

router = Router()


class SuggestStates(StatesGroup):
    s_cat_id = State()
    s_cat_name = State()

    s_prof_cat = State()
    s_prof_id = State()
    s_prof_name = State()

    s_soft_cat = State()
    s_soft_prof = State()
    s_soft_name = State()
    s_soft_type = State()
    s_soft_desc = State()
    s_soft_feature = State()
    s_soft_url = State()
    s_soft_yt = State()


def get_suggest_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="Напрямок", callback_data="suggest_cat")
    builder.button(text="Професію", callback_data="suggest_prof")
    builder.button(text="Програму (Софт)", callback_data="suggest_soft")
    builder.button(text="❌ Скасувати", callback_data="suggest_cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_cat_selection_kb(prefix: str):
    builder = InlineKeyboardBuilder()
    for cat in get_all_categories():
        builder.button(text=cat["name"], callback_data=f"{prefix}_{cat['id']}")
    builder.button(text="❌ Скасувати", callback_data="suggest_cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_prof_selection_kb(cat_id: str, prefix: str):
    builder = InlineKeyboardBuilder()
    for prof in get_professions_by_category(cat_id):
        builder.button(text=prof["name"], callback_data=f"{prefix}_{cat_id}_{prof['id']}")
    builder.button(text="❌ Скасувати", callback_data="suggest_cancel")
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("suggest"))
@router.callback_query(F.data == "suggest_start")
async def cmd_suggest(update, state: FSMContext):
    await state.clear()
    
    msg = update.message if isinstance(update, CallbackQuery) else update
    if isinstance(update, CallbackQuery):
        await msg.edit_text("💡 Що ви хочете запропонувати додати?", reply_markup=get_suggest_menu())
    else:
        await msg.answer("💡 Що ви хочете запропонувати додати?", reply_markup=get_suggest_menu())



@router.callback_query(F.data == "suggest_cancel")
async def suggest_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Дію скасовано. Можете скористатися /suggest знову.")



@router.callback_query(F.data == "suggest_cat")
async def suggest_cat_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введіть ID нового напрямку (латиницею, без пробілів, наприклад 'design'):")
    await state.set_state(SuggestStates.s_cat_id)

@router.message(SuggestStates.s_cat_id)
async def suggest_cat_id(message: Message, state: FSMContext):
    await state.update_data(cat_id=message.text.strip())
    await message.answer("Введіть назву напрямку (наприклад '🎨 Дизайн'):")
    await state.set_state(SuggestStates.s_cat_name)

@router.message(SuggestStates.s_cat_name)
async def suggest_cat_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data_dict = {
        "cat_id": data["cat_id"],
        "name": message.text.strip()
    }
    add_item_request(message.from_user.id, "category", data_dict)
    await state.clear()
    await message.answer("✅ Вашу заявку на додавання напрямку успішно відправлено! Після перевірки адміністратором вона може з'явитися в каталозі.")



@router.callback_query(F.data == "suggest_prof")
async def suggest_prof_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("Спочатку має бути доданий хоча б один напрямок.")
    await callback.message.edit_text("Оберіть напрямок, куди ви хочете додати професію:", reply_markup=get_cat_selection_kb("sp_cat"))
    await state.set_state(SuggestStates.s_prof_cat)

@router.callback_query(SuggestStates.s_prof_cat, F.data.startswith("sp_cat_"))
async def suggest_prof_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("sp_cat_", "")
    await state.update_data(cat_id=cat_id)
    await callback.message.edit_text("Введіть ID професії (латиницею, наприклад 'ui_ux'):")
    await state.set_state(SuggestStates.s_prof_id)

@router.message(SuggestStates.s_prof_id)
async def suggest_prof_id(message: Message, state: FSMContext):
    await state.update_data(prof_id=message.text.strip())
    await message.answer("Введіть назву професії (наприклад 'UI/UX Дизайнер'):")
    await state.set_state(SuggestStates.s_prof_name)

@router.message(SuggestStates.s_prof_name)
async def suggest_prof_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data_dict = {
        "cat_id": data["cat_id"],
        "prof_id": data["prof_id"],
        "name": message.text.strip()
    }
    add_item_request(message.from_user.id, "profession", data_dict)
    await state.clear()
    await message.answer("✅ Вашу заявку на додавання професії успішно відправлено!")



@router.callback_query(F.data == "suggest_soft")
async def suggest_soft_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок:", reply_markup=get_cat_selection_kb("ss_cat"))
    await state.set_state(SuggestStates.s_soft_cat)

@router.callback_query(SuggestStates.s_soft_cat, F.data.startswith("ss_cat_"))
async def suggest_soft_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("ss_cat_", "")
    if not get_professions_by_category(cat_id):
        await state.clear()
        return await callback.message.edit_text("У цьому напрямку немає професій!")
    await state.update_data(cat_id=cat_id)
    await callback.message.edit_text("Оберіть професію:", reply_markup=get_prof_selection_kb(cat_id, "ss_prof"))
    await state.set_state(SuggestStates.s_soft_prof)

@router.callback_query(SuggestStates.s_soft_prof, F.data.startswith("ss_prof_"))
async def suggest_soft_prof(callback: CallbackQuery, state: FSMContext):
    prof_id = callback.data.split("_")[-1]
    await state.update_data(prof_id=prof_id)
    await callback.message.edit_text("Введіть назву програми (софту):")
    await state.set_state(SuggestStates.s_soft_name)

@router.message(SuggestStates.s_soft_name)
async def suggest_soft_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введіть тип програми (Платна / Безкоштовна / Freemium тощо):")
    await state.set_state(SuggestStates.s_soft_type)

@router.message(SuggestStates.s_soft_type)
async def suggest_soft_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text.strip())
    await message.answer("Введіть короткий опис програми:")
    await state.set_state(SuggestStates.s_soft_desc)

@router.message(SuggestStates.s_soft_desc)
async def suggest_soft_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer("Введіть головну фішку (особливість):")
    await state.set_state(SuggestStates.s_soft_feature)

@router.message(SuggestStates.s_soft_feature)
async def suggest_soft_feature(message: Message, state: FSMContext):
    await state.update_data(feature=message.text.strip())
    await message.answer("Введіть посилання на програму:")
    await state.set_state(SuggestStates.s_soft_url)

@router.message(SuggestStates.s_soft_url)
async def suggest_soft_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text.strip())
    await message.answer("Введіть посилання на туторіал з YouTube (або надішліть '-' якщо немає):")
    await state.set_state(SuggestStates.s_soft_yt)

@router.message(SuggestStates.s_soft_yt)
async def suggest_soft_yt(message: Message, state: FSMContext):
    data = await state.get_data()
    yt = message.text.strip()
    if yt == "-":
        yt = ""

    data_dict = {
        "prof_id": data["prof_id"],
        "name": data["name"],
        "type": data["type"],
        "desc": data["desc"],
        "feature": data["feature"],
        "url": data["url"],
        "youtube_tutorial": yt
    }
    
    add_item_request(message.from_user.id, "software", data_dict)
    await message.answer("✅ Вашу заявку на додавання програми успішно відправлено!")
    await state.clear()
