from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

town_markup = InlineKeyboardMarkup()
town_markup.add(InlineKeyboardButton("Ввести город", callback_data="town"))
