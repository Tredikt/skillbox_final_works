from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

hotel_markup = InlineKeyboardMarkup()
hotel_markup.add(InlineKeyboardButton("Найти отель", callback_data="hotel"))
