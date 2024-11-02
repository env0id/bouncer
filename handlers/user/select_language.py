from typing import Union
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user import UserService
from utils.custom_filters import IsUserExistFilter, TranslatedFilter
from utils.tags_remover import HTMLTagsRemover
from services.language import LanguageService
from handlers.common import get_back_to_menu_button
select_language_router = Router()

class SelectLanguageCallback(CallbackData, prefix="select_language"):
    level: int
    language_code: str

def create_callback_language(level: int, language_code: str = ""):
    return SelectLanguageCallback(level=level, language_code=language_code).pack()

@select_language_router.message(TranslatedFilter("language"), IsUserExistFilter())
async def select_language_text_message(message: types.message):
    await select_language(message)

async def select_language(message: Union[Message, CallbackQuery]):
    telegram_id = message.chat.id if isinstance(message, Message) else message.from_user.id
    translations = await UserService.get_translations(telegram_id)

    select_language_markup_builder = create_language_keyboard_builder(translations)
    
    msg = translations["select_language"]
    if isinstance(message, Message):
        await message.answer(msg, parse_mode=ParseMode.HTML, reply_markup=select_language_markup_builder.as_markup())
    elif isinstance(message, CallbackQuery):
        callback = message
        raw_message_text = HTMLTagsRemover.remove_html_tags(msg)
        if raw_message_text != callback.message.text:
            await callback.message.edit_text(msg, parse_mode=ParseMode.HTML, reply_markup=select_language_markup_builder.as_markup())
        else:
            await callback.answer()

async def change_language(callback: CallbackQuery):
    from handlers.user.start import start
    unpacked_callback = SelectLanguageCallback.unpack(callback.data)
    telegram_id = callback.from_user.id
    await UserService.update_language(telegram_id, unpacked_callback.language_code)
    await start(callback)

def create_language_keyboard_builder(translations):
    language_markup_builder = InlineKeyboardBuilder()
    languages = LanguageService.get_all()
    for language in languages:
        language_inline = types.InlineKeyboardButton(
            text=language["name"].capitalize(),
            callback_data=create_callback_language(1, language["code"])
        )
        language_markup_builder.add(language_inline)
    language_markup_builder.add(get_back_to_menu_button(translations))
    language_markup_builder.adjust(1)
    return language_markup_builder

@select_language_router.callback_query(SelectLanguageCallback.filter(), IsUserExistFilter())
async def navigate(callback: CallbackQuery, callback_data: SelectLanguageCallback):
    current_level = callback_data.level

    levels = {
        0: select_language,
        1: change_language,
    }

    current_level_function = levels[current_level]

    await current_level_function(callback)