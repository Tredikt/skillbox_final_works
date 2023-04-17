data = dict()
entrepreneur_data = dict()

def entrepreneur():
    print(f"{'-' * 50}")
    while True:
        OGRNIP = input("Введите ОГРНИП: ")
        if len(OGRNIP) == 15:
            entrepreneur_data["ОГРНИП:"] = OGRNIP
            break
        print("ОГРНИП должен содержать 15 цифр")
    entrepreneur_data["ИНН"] = input("Введите ИНН: ")
    entrepreneur_data["Р/с"] = input("Введите расчётный счёт: ")
    entrepreneur_data["Банк"] = input("Введите название банка: ")
    entrepreneur_data["БИК"] = input("Введите БИК: ")
    entrepreneur_data["К/с"] = input("Введите корреспонденский счёт: ")

def own_information():
    print(f"{'-' * 50}")
    data["Имя:"] = input("Введите имя: ")
    data["Возраст:"] = int(input("Введите возраст: "))
    data["Телефон:"] = input("Введите номер телефона (+7ХХХХХХХХХХ): ")
    data["E-mail:"] = input("Введите адрес электронной почты: ")
    data["Индекс"] = input("Введите почтовый индекс: ")
    data["Адрес"] = input("Введите почтовый адрес (без индекса): ")

def information_update():
    print(f"{'-' * 50}"
          f"\nВВЕСТИ ИЛИ ОБНОВИТЬ ИНФОРМАЦИЮ")
    information = int(input("1 - Личная информация"
                            "\n2 - Информация о предпринимателе"
                            "\n0 - Назад"
                            "\nВыберите номер пункта: "))
    return information

print(f"Приложение MyProfile"
      f"\nСохраняй информацию о себе и выводи её в разных форматах")


print("ГЛАВНОЕ МЕНЮ")

while True:
    print(f"{'-' * 50}")
    main_menu = int(input("1 - Ввести или обновить информацию"
                    "\n2 - Вывести информацию"
                    "\n0 - Завершить работу"
                    "\nВыберите номер пункта: "))

    if main_menu == 0:
        break

    if main_menu == 1:
        while True:
            information = information_update()

            if information == 1:
                own_information()

            elif information == 2:
                entrepreneur()

            elif information == 0:
                break

    elif main_menu == 2:
        while True:
            print(f"{'-' * 50}")
            output_information = int(input("ВЫВЕСТИ ИНФОРМАЦИЮ"
                                            "\n1 - Общая информация"
                                            "\n2 - Вся информация"
                                            "\n0 - Назад"
                                            "\nВыберите номер пункта: "))

            if output_information == 0:
                break


            if output_information == 1:
                print(f"{'-' * 50}")
                for key, value in data.items():
                    print(key, value)

            elif output_information == 2:
                print(f"{'-' * 50}")
                for key, value in data.items():
                    print(key, value)

                print()

                for key, value in entrepreneur_data.items():
                        print(key, value)