from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

check_out_markup = InlineKeyboardMarkup()
check_out_markup.add(InlineKeyboardButton("Ввести дату выселения", callback_data="checkout"))
