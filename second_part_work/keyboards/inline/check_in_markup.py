from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

check_in_markup = InlineKeyboardMarkup()
check_in_markup.add(InlineKeyboardButton("Ввести дату заселения", callback_data="checkin"))
