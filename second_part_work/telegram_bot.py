from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.types import InlineKeyboardButton

from keyboards.inline.remove_markup import remove_markup
from keyboards.inline.hotel_markup import hotel_markup
from keyboards.inline.start_markup import start_markup
from keyboards.inline.town_markup import town_markup
from keyboards.inline.check_in_markup import check_in_markup
from keyboards.inline.check_out_markup import check_out_markup

from sqlite3 import connect
from requests import request
from json import dump, load
from datetime import date, datetime
from emoji import emojize


class MyBot:
    def __init__(self, token: str, api_token: str) -> None:
        self.bot = Bot(token)
        self.dp = Dispatcher(self.bot)

        self.querystring = {"lang": "ru", "currency": "rub", "token": api_token}
        self.flag = False
        self.date_in = False
        self.date_out = False

    async def start(self, message: Message):
        if message.from_user.last_name is None:
            await self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.first_name}",
                reply_markup=remove_markup)
        else:
            await self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.first_name} {message.from_user.last_name}.",
                reply_markup=remove_markup
            )

        sql_connection = connect("/databases/telegram_bot.db")
        try:
            cursor = sql_connection.cursor()
            sqlite_query = f"""SELECT * FROM RequestHistory WHERE tg_id={message.from_user.id};"""
            sql = cursor.execute(sqlite_query)
            sql_connection.commit()

            if len(sql.fetchall()) != 0:
                self.flag_data = True
        finally:
            if sql_connection:
                sql_connection.close()

        await self.bot.send_message(
            message.from_user.id,
            "Я бот, предоставляющий информацию об отелях",
            reply_markup=hotel_markup
        )

    async def text_handler(self, message: Message):
        text = message.text.lower()
        id = message.chat.id

        if self.flag:
            data_test = {"lang": "ru", "lookFor": "both", "limit": "1"}
            try:
                data_test["query"] = text
                url = "http://engine.hotellook.com/api/v2/lookup.json?"
                response = request("GET", url, params=data_test)
                with open("../hotels.txt", "w", encoding="UTF-8") as file:
                    dump(response.json(), file, indent=4)

                with open("../hotels.txt", "r", encoding="UTF-8") as file:
                    dct = load(file)
                    if (response.status_code != 200) or (dct["results"]["locations"][0]["cityName"].lower() != text):
                        raise SyntaxError
                self.querystring["location"] = text.title()
                self.flag = False
                await self.input_data(message=message, data="checkin")
            except SyntaxError:
                await self.bot.send_message(id, "Некорректный ввод, попробуйте ещё раз")

        elif self.date_in:
            date = await self.make_date(text, id=message.chat.id)
            if date:
                self.querystring["checkIn"] = str(date)
                self.date_in = False
                await self.input_data(message=message, data="checkout")

        elif self.date_out:
            date = await self.make_date(text, id=message.chat.id)
            if date:
                self.querystring["checkOut"] = str(date)
                self.date_out = False
                await self.hotels(message=message, querystring=self.querystring)

    async def callback_handler(self, call: CallbackQuery):
        user_id = call.message.chat.id
        req = call.data.split("_")
        if req[0] == "hotel":
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)
            await self.input_data(message=call.message, data="town")

        elif req[0] == "town":
            self.flag = True

        elif req[0] == "checkin":
            self.date_in = True

        elif req[0] == "checkout":
            self.date_out = True

        elif req[0] == "datatown":
            sqlData = await self.sql_data(data="town", user_id=user_id)
            self.querystring["location"] = sqlData
            await self.bot.send_message(call.message.chat.id, f"Город: {sqlData.title()}")
            self.date_in = True
            await self.input_data(message=call.message, data="checkin")

        elif req[0] == "datacheckin":
            sqlData = await self.sql_data(data="checkin", user_id=user_id)
            made_date = await self.make_date(sqlData, call.message.chat.id)
            self.querystring["checkIn"] = str(made_date)
            date_in_mess = " ".join(self.querystring["checkIn"].split("-")[::-1])

            await self.bot.send_message(call.message.chat.id, f"Дата заселения: {date_in_mess}")
            self.date_out = True
            await self.input_data(message=call.message, data="checkout")


        elif req[0] == "datacheckout":
            sqlData = await self.sql_data(data="checkout", user_id=user_id)
            made_date = await self.make_date(sqlData, call.message.chat.id)
            self.querystring["checkOut"] = str(made_date)
            date_out_mess = " ".join(self.querystring["checkOut"].split("-")[::-1])
            await self.bot.send_message(call.message.chat.id, f"Дата выселения: {date_out_mess}")
            await self.hotels(call.message, querystring=self.querystring)

    async def hotels(self, message, querystring):
        url = "http://engine.hotellook.com/api/v2/cache.json?"

        year, month, day = list(map(int, querystring["checkOut"].split("-")))
        date_checkout = date(year, month, day)
        year, month, day = list(map(int, querystring["checkIn"].split("-")))
        date_checkin = date(year, month, day)
        last_date = date_checkout - date_checkin
        response = request("GET", url, params=querystring)

        with open("../hotels.txt", "w", encoding="UTF-8") as file:
            dump(response.json(), file, indent=4)

        with open("../hotels.txt", "r", encoding="UTF-8") as file:
            dct = load(file)
            for num in range(len(dct)):
                row = f"{'=' * 30}\nНазвание отеля: {dct[num]['hotelName']}" \
                      f"\nПериод проживания: {last_date.days} дней" \
                      f"\nПримерная цена за период проживания: {round(int(dct[num]['priceAvg']))} рублей" \
                      f"\nКоличество звёзд: {emojize(':star:') * int(dct[num]['stars'])}" \
                      f"\n{'=' * 30}"
                await self.bot.send_message(message.chat.id, row)

        sqlite_connection = connect("/databases/telegram_bot.db")
        try:
            cursor = sqlite_connection.cursor()
            sqlite_delete_query = f"""DELETE from RequestHistory WHERE tg_id={message.from_user.id}"""
            sqlite_insert_query = f"""INSERT INTO RequestHistory
                                        (tg_id, town, check_in, check_out)
                                        VALUES
                                        ({message.from_user.id}, "{querystring["location"]}", "{" ".join(querystring["checkIn"].split("-")[::-1])}", "{" ".join(querystring["checkOut"].split("-")[::-1])}");"""

            cursor.execute(sqlite_delete_query)
            sqlite_connection.commit()
            cursor.execute(sqlite_insert_query)
            sqlite_connection.commit()
            cursor.close()
        finally:
            if not sqlite_connection:
                return
            sqlite_connection.close()

        await self.bot.send_message(message.chat.id, "Хорошего отдыха", reply_markup=start_markup)

    async def input_data(self, message, data):
        data = data.lower()
        id = message.chat.id

        if data == "town":
            if self.flag_data:
                sqlData = await self.sql_data(data="town", user_id=id)
                sqlData = sqlData.title()
                if sqlData:
                    town_markup.add(InlineKeyboardButton(sqlData, callback_data="datatown"))
            await self.bot.send_message(
                id,
                "Нажмите на кнопку и введите город, информацию об отелях которого хотите узнать",
                reply_markup=town_markup
            )

        elif data == "checkin":
            if self.flag_data:
                sqlData = await self.sql_data(data="checkin", user_id=id)
                sqlData = sqlData.title()
                if sqlData:
                    check_in_markup.add(InlineKeyboardButton(sqlData, callback_data="datacheckin"))
            await self.bot.send_message(
                id,
                "Отлично, теперь нажмите кнопку и введите дату (день месяц год через пробел):",
                reply_markup=check_in_markup
            )

        elif data == "checkout":
            if self.flag_data:
                sqlData = await self.sql_data(data="checkout", user_id=id)
                sqlData = sqlData.title()
                if sqlData:
                    check_out_markup.add(InlineKeyboardButton(sqlData, callback_data="datacheckout"))
            await self.bot.send_message(
                id,
                "Дата заселения успешно введена, теперь нажмите на кнопку и введите дату выселения"
                "(день месяц год через пробел):",
                reply_markup=check_out_markup
            )

    async def make_date(self, text, id):
        day, month, year = list(map(int, text.split()))
        today_date = date(datetime.now().year, datetime.now().month,
                                   datetime.now().day)
        try:
            made_date = date(year, month, day)
            if made_date < today_date:
                raise SyntaxError
            return made_date
        except SyntaxError:
            await self.bot.send_message(id, "Некорректный ввод, попробуйте ещё раз")

    @staticmethod
    async def sql_data(data, user_id):
        sql_connection = connect("/databases/telegram_bot.db")
        try:
            cursor = sql_connection.cursor()
            sqlite_query = f"""SELECT * FROM RequestHistory WHERE tg_id={user_id};"""
            sql = cursor.execute(sqlite_query)
            sql_connection.commit()
            sql = sql.fetchall()

            if len(sql) == 0:
                return None

            if data.lower() == "town":
                return sql[0][1]
            elif data.lower() == "checkin":
                return sql[0][2]
            elif data.lower() == "checkout":
                return sql[0][3]
            cursor.close()
        finally:
            if sql_connection:
                sql_connection.close()

    def add_handlers(self) -> None:
        """
        Функция регистрирует все хэндлеры
        """
        self.dp.register_message_handler(self.start, commands=["start"])
        self.dp.register_message_handler(self.text_handler, content_types=ContentType.TEXT)
        self.dp.register_callback_query_handler(self.callback_handler, lambda message: True)

    def run(self):
        """
        Фукнция запуска бота
        """
        self.add_handlers()
        executor.start_polling(self.dp, skip_updates=True)
