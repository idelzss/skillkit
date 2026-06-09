from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID
from database import (
    get_all_categories, add_category, delete_category,
    get_professions_by_category, add_profession, delete_profession,
    get_software_by_profession, add_software, delete_software,
    update_software_field, get_pending_requests, update_request_status, get_request_by_id
)


router = Router()

FIELD_NAMES = {
    "name": "назву",
    "type": "тип",
    "desc": "опис",
    "feature": "фішку",
    "url": "посилання",
    "youtube_tutorial": "туторіал з ютуба"
}


class AdminStates(StatesGroup):
    add_cat_id = State()
    add_cat_name = State()

    add_prof_cat = State()
    add_prof_id = State()
    add_prof_name = State()

    add_soft_cat = State()
    add_soft_prof = State()
    add_soft_name = State()
    add_soft_type = State()
    add_soft_desc = State()
    add_soft_feature = State()
    add_soft_url = State()
    add_soft_youtube_tutorial = State()

    del_prof_cat = State()
    del_soft_cat = State()
    del_soft_prof = State()

    edit_soft_cat = State()
    edit_soft_prof = State()
    edit_soft_select = State()
    edit_soft_field = State()
    edit_soft_value = State()


def get_admin_menu():
    pending_count = len(get_pending_requests())
    builder = InlineKeyboardBuilder()
    builder.button(text=f"📨 Заявки ({pending_count})", callback_data="admin_requests")
    builder.button(text="➕ Додати напрямок", callback_data="admin_add_cat")
    builder.button(text="➕ Додати професію", callback_data="admin_add_prof")
    builder.button(text="➕ Додати софт", callback_data="admin_add_soft")
    builder.button(text="🗑 Видалити напрямок", callback_data="admin_del_cat")
    builder.button(text="🗑 Видалити професію", callback_data="admin_del_prof")
    builder.button(text="🗑 Видалити софт", callback_data="admin_del_soft")
    builder.button(text="✏️ Редагувати софт", callback_data="admin_edit_soft")
    builder.adjust(1)
    return builder.as_markup()


def get_cat_selection_kb(prefix: str):
    builder = InlineKeyboardBuilder()
    for cat in get_all_categories():
        builder.button(text=cat["name"], callback_data=f"{prefix}_{cat['id']}")
    builder.button(text="❌ Скасувати", callback_data="admin_cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_prof_selection_kb(cat_id: str, prefix: str):
    builder = InlineKeyboardBuilder()
    for prof in get_professions_by_category(cat_id):
        builder.button(text=prof["name"], callback_data=f"{prefix}_{cat_id}_{prof['id']}")
    builder.button(text="❌ Скасувати", callback_data="admin_cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_soft_selection_kb(prof_id: str, prefix: str):
    builder = InlineKeyboardBuilder()
    for soft in get_software_by_profession(prof_id):
        builder.button(text=soft["name"], callback_data=f"{prefix}_{soft['id']}")
    builder.button(text="❌ Скасувати", callback_data="admin_cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_soft_fields_kb(soft_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="Назва", callback_data=f"esf_{soft_id}_name")
    builder.button(text="Тип (Платна/Безкоштовна)", callback_data=f"esf_{soft_id}_type")
    builder.button(text="Опис", callback_data=f"esf_{soft_id}_desc")
    builder.button(text="Фішка", callback_data=f"esf_{soft_id}_feature")
    builder.button(text="Посилання", callback_data=f"esf_{soft_id}_url")
    builder.button(text="Туторіал (YouTube)", callback_data=f"esf_{soft_id}_youtube_tutorial")
    builder.button(text="❌ Скасувати", callback_data="admin_cancel")
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if str(ADMIN_ID) == "0" or str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("Доступ заборонено.")
        return
    await state.clear()
    await message.answer("🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Дію скасовано. 🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_add_cat")
async def add_cat_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введіть ID нового напрямку (латиницею, без пробілів, наприклад 'dev'): ")
    await state.set_state(AdminStates.add_cat_id)


@router.message(AdminStates.add_cat_id)
async def add_cat_id(message: Message, state: FSMContext):
    await state.update_data(cat_id=message.text.strip())
    await message.answer("Введіть назву напрямку (наприклад '💻 Розробка'): ")
    await state.set_state(AdminStates.add_cat_name)


@router.message(AdminStates.add_cat_name)
async def add_cat_name(message: Message, state: FSMContext):
    data = await state.get_data()
    cat_id = data["cat_id"]
    cat_name = message.text.strip()

    if add_category(cat_id, cat_name):
        await message.answer(f"Напрямок '{cat_name}' додано!")
    else:
        await message.answer("Цей ID вже існує або сталася помилка. Скасовано.")

    await state.clear()
    await message.answer("🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_add_prof")
async def add_prof_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("Спочатку додайте напрямок!")
    await callback.message.edit_text("Оберіть напрямок, куди додати професію:",
                                      reply_markup=get_cat_selection_kb("ap_cat"))
    await state.set_state(AdminStates.add_prof_cat)


@router.callback_query(AdminStates.add_prof_cat, F.data.startswith("ap_cat_"))
async def add_prof_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("ap_cat_", "")
    await state.update_data(cat_id=cat_id)
    await callback.message.edit_text("Введіть ID професії (латиницею, наприклад 'dev_front'):")
    await state.set_state(AdminStates.add_prof_id)


@router.message(AdminStates.add_prof_id)
async def add_prof_id(message: Message, state: FSMContext):
    await state.update_data(prof_id=message.text.strip())
    await message.answer("Введіть назву професії (наприклад 'Frontend-розробник'):")
    await state.set_state(AdminStates.add_prof_name)


@router.message(AdminStates.add_prof_name)
async def add_prof_name(message: Message, state: FSMContext):
    data = await state.get_data()
    prof_id = data["prof_id"]
    prof_name = message.text.strip()

    if add_profession(prof_id, data["cat_id"], prof_name):
        await message.answer(f"Професію '{prof_name}' додано!")
    else:
        await message.answer("Ця професія вже існує або помилка. Скасовано.")

    await state.clear()
    await message.answer("🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_del_cat")
async def del_cat_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок для видалення:",
                                      reply_markup=get_cat_selection_kb("del_cat"))


@router.callback_query(F.data.startswith("del_cat_"))
async def del_cat_exec(callback: CallbackQuery):
    cat_id = callback.data.replace("del_cat_", "")
    delete_category(cat_id)
    await callback.message.edit_text("Напрямок видалено. 🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_del_prof")
async def del_prof_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок:", reply_markup=get_cat_selection_kb("dp_cat"))
    await state.set_state(AdminStates.del_prof_cat)


@router.callback_query(AdminStates.del_prof_cat, F.data.startswith("dp_cat_"))
async def del_prof_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("dp_cat_", "")
    if not get_professions_by_category(cat_id):
        await state.clear()
        return await callback.message.edit_text("У цьому напрямку немає професій. 🛠 Адмін-панель",
                                                 reply_markup=get_admin_menu())
    await callback.message.edit_text("Оберіть професію для видалення:",
                                      reply_markup=get_prof_selection_kb(cat_id, "dp_prof"))


@router.callback_query(AdminStates.del_prof_cat, F.data.startswith("dp_prof_"))
async def del_prof_exec(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    delete_profession(parts[-1])
    await state.clear()
    await callback.message.edit_text("Професію видалено. 🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_del_soft")
async def del_soft_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок:", reply_markup=get_cat_selection_kb("ds_cat"))
    await state.set_state(AdminStates.del_soft_cat)


@router.callback_query(AdminStates.del_soft_cat, F.data.startswith("ds_cat_"))
async def del_soft_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("ds_cat_", "")
    if not get_professions_by_category(cat_id):
        await state.clear()
        return await callback.message.edit_text("Немає професій. 🛠 Адмін-панель",
                                                 reply_markup=get_admin_menu())
    await callback.message.edit_text("Оберіть професію:",
                                      reply_markup=get_prof_selection_kb(cat_id, "ds_prof"))
    await state.set_state(AdminStates.del_soft_prof)


@router.callback_query(AdminStates.del_soft_prof, F.data.startswith("ds_prof_"))
async def del_soft_prof(callback: CallbackQuery, state: FSMContext):
    prof_id = callback.data.split("_")[-1]
    if not get_software_by_profession(prof_id):
        await state.clear()
        return await callback.message.edit_text("Немає софту. 🛠 Адмін-панель",
                                                 reply_markup=get_admin_menu())
    await callback.message.edit_text("Оберіть софт для видалення:",
                                      reply_markup=get_soft_selection_kb(prof_id, "ds_soft"))


@router.callback_query(AdminStates.del_soft_prof, F.data.startswith("ds_soft_"))
async def del_soft_exec(callback: CallbackQuery, state: FSMContext):
    soft_id = int(callback.data.split("_")[-1])
    delete_software(soft_id)
    await state.clear()
    await callback.message.edit_text("Софт видалено. 🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_edit_soft")
async def edit_soft_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок:", reply_markup=get_cat_selection_kb("es_cat"))
    await state.set_state(AdminStates.edit_soft_cat)


@router.callback_query(AdminStates.edit_soft_cat, F.data.startswith("es_cat_"))
async def edit_soft_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("es_cat_", "")
    if not get_professions_by_category(cat_id):
        await state.clear()
        return await callback.message.edit_text("Немає професій. 🛠 Адмін-панель",
                                                 reply_markup=get_admin_menu())
    await callback.message.edit_text("Оберіть професію:",
                                      reply_markup=get_prof_selection_kb(cat_id, "es_prof"))
    await state.set_state(AdminStates.edit_soft_prof)


@router.callback_query(AdminStates.edit_soft_prof, F.data.startswith("es_prof_"))
async def edit_soft_prof(callback: CallbackQuery, state: FSMContext):
    prof_id = callback.data.split("_")[-1]
    if not get_software_by_profession(prof_id):
        await state.clear()
        return await callback.message.edit_text("Немає софту. 🛠 Адмін-панель",
                                                 reply_markup=get_admin_menu())
    await callback.message.edit_text("Оберіть софт для редагування:",
                                      reply_markup=get_soft_selection_kb(prof_id, "es_soft"))
    await state.set_state(AdminStates.edit_soft_select)


@router.callback_query(AdminStates.edit_soft_select, F.data.startswith("es_soft_"))
async def edit_soft_select(callback: CallbackQuery, state: FSMContext):
    soft_id = int(callback.data.split("_")[-1])
    await state.update_data(soft_id=soft_id)
    await callback.message.edit_text("Що саме хочете змінити?", reply_markup=get_soft_fields_kb(soft_id))
    await state.set_state(AdminStates.edit_soft_field)


@router.callback_query(AdminStates.edit_soft_field, F.data.startswith("esf_"))
async def edit_soft_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[-1]
    await state.update_data(field=field)
    await callback.message.edit_text(f"Введіть нове значення для поля '{FIELD_NAMES[field]}':")
    await state.set_state(AdminStates.edit_soft_value)


@router.message(AdminStates.edit_soft_value)
async def edit_soft_value(message: Message, state: FSMContext):
    data = await state.get_data()
    update_software_field(data["soft_id"], data["field"], message.text.strip())
    await state.clear()
    await message.answer("Зміни успішно збережено! 🛠 Адмін-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_add_soft")
async def add_soft_start(callback: CallbackQuery, state: FSMContext):
    if not get_all_categories():
        return await callback.answer("БД порожня!")
    await callback.message.edit_text("Оберіть напрямок:", reply_markup=get_cat_selection_kb("as_cat"))
    await state.set_state(AdminStates.add_soft_cat)


@router.callback_query(AdminStates.add_soft_cat, F.data.startswith("as_cat_"))
async def add_soft_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("as_cat_", "")
    if not get_professions_by_category(cat_id):
        await state.clear()
        return await callback.message.edit_text("У цьому напрямку немає професій!",
                                                 reply_markup=get_admin_menu())
    await state.update_data(cat_id=cat_id)
    await callback.message.edit_text("Оберіть професію:",
                                      reply_markup=get_prof_selection_kb(cat_id, "as_prof"))
    await state.set_state(AdminStates.add_soft_prof)


@router.callback_query(AdminStates.add_soft_prof, F.data.startswith("as_prof_"))
async def add_soft_prof(callback: CallbackQuery, state: FSMContext):
    prof_id = callback.data.split("_")[-1]
    await state.update_data(prof_id=prof_id)
    await callback.message.edit_text("Введіть назву софту (напр. 'Figma'):")
    await state.set_state(AdminStates.add_soft_name)


@router.message(AdminStates.add_soft_name)
async def add_soft_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введіть тип (Платна/Безкоштовна):")
    await state.set_state(AdminStates.add_soft_type)


@router.message(AdminStates.add_soft_type)
async def add_soft_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text.strip())
    await message.answer("Введіть короткий опис:")
    await state.set_state(AdminStates.add_soft_desc)


@router.message(AdminStates.add_soft_desc)
async def add_soft_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer("Введіть фішку:")
    await state.set_state(AdminStates.add_soft_feature)


@router.message(AdminStates.add_soft_feature)
async def add_soft_feature(message: Message, state: FSMContext):
    await state.update_data(feature=message.text.strip())
    await message.answer("Введіть посилання:")
    await state.set_state(AdminStates.add_soft_url)


@router.message(AdminStates.add_soft_url)
async def add_soft_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text.strip())
    await message.answer("Введіть посилання на туторіал з YouTube (або надішліть '-' якщо немає):")
    await state.set_state(AdminStates.add_soft_youtube_tutorial)


@router.message(AdminStates.add_soft_youtube_tutorial)
async def add_soft_youtube_tutorial(message: Message, state: FSMContext):
    data = await state.get_data()
    yt = message.text.strip()
    if yt == "-":
        yt = ""

    add_software(
        prof_id=data["prof_id"],
        name=data["name"],
        type_=data["type"],
        desc=data["desc"],
        feature=data["feature"],
        url=data["url"],
        youtube_tutorial=yt
    )

    await message.answer(f"Софт '{data['name']}' додано!")
    await state.clear()
    await message.answer("🛠 Адмін-панель", reply_markup=get_admin_menu())




@router.callback_query(F.data == "admin_requests")
async def admin_requests_list(callback: CallbackQuery):
    requests = get_pending_requests()
    if not requests:
        return await callback.message.edit_text("Немає нових заявок. 🛠 Адмін-панель", reply_markup=get_admin_menu())
    
    req = requests[0]
    text = f"📨 <b>Заявка #{req['id']}</b> від користувача {req['user_id']}\n"
    text += f"Тип: <b>{req['request_type']}</b>\n\n"
    for k, v in req['data'].items():
        text += f"<b>{k}</b>: {v}\n"
        
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Схвалити", callback_data=f"admin_req_approve_{req['id']}")
    builder.button(text="❌ Відхилити", callback_data=f"admin_req_reject_{req['id']}")
    builder.button(text="🔙 Назад", callback_data="admin_cancel")
    builder.adjust(2, 1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin_req_approve_"))
async def admin_req_approve(callback: CallbackQuery):
    req_id = int(callback.data.replace("admin_req_approve_", ""))
    req = get_request_by_id(req_id)
    if not req or req['status'] != 'pending':
        return await callback.answer("Ця заявка вже оброблена або не існує.")
        
    data = req['data']
    try:
        if req['request_type'] == "category":
            add_category(data["cat_id"], data["name"])
        elif req['request_type'] == "profession":
            add_profession(data["prof_id"], data["cat_id"], data["name"])
        elif req['request_type'] == "software":
            add_software(data["prof_id"], data["name"], data["type"], data["desc"], data["feature"], data["url"], data.get("youtube_tutorial", ""))
        
        update_request_status(req_id, "approved")
        
        try:
            await callback.bot.send_message(req['user_id'], f"✅ Вашу заявку на додавання '{data['name']}' було схвалено адміністратором!")
        except Exception:
            pass
            
        await callback.answer("Схвалено!")
        await admin_requests_list(callback)
    except Exception as e:
        await callback.answer(f"Помилка: {e}")


@router.callback_query(F.data.startswith("admin_req_reject_"))
async def admin_req_reject(callback: CallbackQuery):
    req_id = int(callback.data.replace("admin_req_reject_", ""))
    req = get_request_by_id(req_id)
    if not req or req['status'] != 'pending':
        return await callback.answer("Ця заявка вже оброблена або не існує.")
        
    update_request_status(req_id, "rejected")
    data = req['data']
    
    try:
        await callback.bot.send_message(req['user_id'], f"❌ Вашу заявку на додавання '{data['name']}' було відхилено адміністратором.")
    except Exception:
        pass
        
    await callback.answer("Відхилено!")
    await admin_requests_list(callback)

