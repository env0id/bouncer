from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Union
from config import SUPPORT_LINK, COMMUNITY_LINK
from services.user import UserService
from utils.stripe_api import create_customer, create_checkout_session, get_prices
from handlers.common import get_back_to_menu_markup, get_back_to_menu_button
from handlers.user.select_language import  create_callback_language

start_router = Router()

class StartCallback(CallbackData, prefix="main"):
  level: int

def create_callback_start(level: int) -> str:
  return StartCallback(level=level).pack()

@start_router.chat_join_request()
async def bounce_user(join_request: types.ChatJoinRequest):
  user_id = join_request.from_user.id
  user = join_request.from_user
  user_exist = await UserService.is_exist(user_id)
  if user_exist is False:
    stripe_customer = await create_customer(user_id, user.first_name, user.last_name, user.username)
    await UserService.user_logged(user_id, stripe_customer.id, user.username)

  user = await UserService.get_by_tgid(user_id)
  translations = await UserService.get_translations(user_id)
  if user.subscription:
    await join_request.approve()  
  else:
    await join_request.decline()
    await join_request.bot.send_message(user_id, translations["subscription_needed"])


@start_router.message(Command(commands=["start", "help"]))
async def start(message: Union[types.Message, types.CallbackQuery]):
  user_id = message.chat.id if isinstance(message, types.Message) else message.from_user.id
  user = message.from_user
  stripe_customer = await create_customer(user_id, user.first_name, user.last_name, user.username)
  await UserService.user_logged(user_id, stripe_customer.id, user.username)

  translations = await UserService.get_translations(user_id)
  main_keyboard_builder = InlineKeyboardBuilder()
  main_keyboard_builder.button(text=translations["billing"], callback_data=create_callback_start(3))
  main_keyboard_builder.button(text=translations["faq"], callback_data=create_callback_start(1))
  main_keyboard_builder.button(text=translations["support"], callback_data=create_callback_start(2))
  main_keyboard_builder.button(text=translations["community"], url=COMMUNITY_LINK)
  main_keyboard_builder.button(text=translations["language"], callback_data=create_callback_language(0))
  main_keyboard_builder.adjust(1)
  if isinstance(message, types.Message):
    await message.answer(translations["hello"], reply_markup=main_keyboard_builder.as_markup())
    await message.bot.set_my_commands([BotCommand(command="start", description="Start the bot")])
  if isinstance(message, types.CallbackQuery):
    await message.message.edit_text(translations["hello"], reply_markup=main_keyboard_builder.as_markup())


async def faq(callback: types.CallbackQuery):
  user_telegram_id = callback.from_user.id
  translations = await UserService.get_translations(user_telegram_id)
  await callback.message.edit_text(translations["faq"].format(callback.from_user.first_name), parse_mode='html', reply_markup=get_back_to_menu_markup(translations))


async def support(callback: types.CallbackQuery):
  user_telegram_id = callback.from_user.id
  translations = await UserService.get_translations(user_telegram_id)
  admin_keyboard_builder = InlineKeyboardBuilder()
  admin_keyboard_builder.button(text=translations["support"], url=SUPPORT_LINK)
  admin_keyboard_builder.add(get_back_to_menu_button(translations))
  admin_keyboard_builder.adjust(1)
  await callback.message.edit_text(translations["help_message"], reply_markup=admin_keyboard_builder.as_markup())


async def billing(callback: types.CallbackQuery):
  user_id = callback.message.chat.id
  translations = await UserService.get_translations(user_id)
  user = await UserService.get_by_tgid(user_id)

  prices = await get_prices()
  price_keyboard_builder = InlineKeyboardBuilder()

  for price in prices:
    price_id = price["price_id"]
    interval = price["interval"]
    amount = price["amount"]
    currency = price["currency"]
    url = await create_checkout_session(user.stripe_id, price_id)
    price_keyboard_builder.button(text=f"{interval} | {amount} {currency})", url=url)
  
  price_keyboard_builder.add(get_back_to_menu_button(translations))
  price_keyboard_builder.adjust(1)
  await callback.message.edit_text(translations["billing_options"], reply_markup=price_keyboard_builder.as_markup())


@start_router.callback_query(StartCallback.filter())
async def start_menu_navigation(callback: types.CallbackQuery, callback_data: StartCallback):
  current_level = callback_data.level
  levels = {
  0: start,
  1: faq,
  2: support,
  3: billing
  }
  current_level_function = levels[current_level]
  await current_level_function(callback)