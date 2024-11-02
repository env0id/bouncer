from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_to_menu_button(translations):
  from handlers.user.start import create_callback_start
  return types.InlineKeyboardButton(text=translations["back"], callback_data=create_callback_start(0))

def get_back_to_menu_markup(translations):
  return types.InlineKeyboardMarkup(inline_keyboard=[[get_back_to_menu_button(translations)]])