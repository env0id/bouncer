from aiogram import types
from aiogram.filters import BaseFilter

from services.user import UserService
from services.language import LanguageService

class IsUserExistFilter(BaseFilter):
  async def __call__(self, message: types.message):
    return await UserService.is_exist(message.from_user.id)

class TranslatedFilter(BaseFilter):
  def __init__(self, phrase: str):
    super().__init__()
    self.phrase = phrase

  async def __call__(self, message: types.message):
    return message.text in [t[self.phrase] for t in LanguageService.get_all()]
