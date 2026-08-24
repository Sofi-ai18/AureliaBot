import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.request import HTTPXRequest
from procedures import procedures
from clinic import clinic_sections, clinic_menu
from contacts import contacts_data, contacts_menu
categories_order = {

    "Инъекционная косметология": [
        "Контурная пластика",
        "Биоревитализация",
        "Ботулинотерапия",
        "Мезотерапия"
    ],


    "Аппаратная косметология": [
        "SMAS-лифтинг",
        "RF-лифтинг",
        "Лазерное омоложение"
],


    "Уход за лицом": [
        "Уход за лицом",
        "Пилинг"
    ],

    "Коррекция тела": [
        "Лазерная эпиляция",
        "Коррекция фигуры",
        "Аппаратные программы тела"
]
   
}

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1384660027

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

google_credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")

if google_credentials_base64:
    google_credentials_json = base64.b64decode(
        google_credentials_base64
    ).decode("utf-8")

    google_credentials_info = json.loads(
        google_credentials_json
    )

    creds = Credentials.from_service_account_info(
        google_credentials_info,
        scopes=SCOPES
    )
else:
    creds = Credentials.from_service_account_file(
        "aureliabot-e207fc46fc4a.json",
        scopes=SCOPES
    )

client = gspread.authorize(creds)

sheet = client.open("Aurelia Clinic заявки").sheet1NAME, PHONE, PROCEDURE = range(3)
# =========================
# МЕНЮ
# =========================

def main_menu():

    keyboard = [

        ["Процедуры", "Записаться"],

        ["О клинике", "Контакты"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def directions_menu():

    keyboard = [

        ["~ Инъекционная косметология ~"],

        ["~ Аппаратная косметология ~"],

        ["~ Уход за лицом ~"],

        ["~ Коррекция тела ~"],

        ["← Назад"]
   ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def category_menu(category):

    keyboard = []


    for name, item in procedures.items():

        if item["category"] == category:

            keyboard.append([name])


    keyboard.append(["← Вернуться к направлениям"])


    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def procedure_menu(current, category):

    buttons = [

        ["✦ Записаться"],

        ["Подробнее"]

    ]


    procedures_list = categories_order[category]

    index = procedures_list.index(current)


    if index > 0:

        buttons.append(
            ["← Предыдущая"]
        )


    if index < len(procedures_list) - 1:

        buttons.append(
            ["→ Следующая"]
        )


    buttons.append(
        ["← Вернуться к направлениям"]
    )


    return ReplyKeyboardMarkup(

        buttons,

        resize_keyboard=True

    )
def confirm_procedure_menu():

    keyboard = [

        ["✓ Да, записаться"],

        ["Выбрать другую процедуру"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
def details_menu():

    keyboard = [

        ["✦ Записаться"],

        ["← Вернуться к процедуре"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
def appointment_procedure_menu():

    keyboard = []

    for name in procedures.keys():

        keyboard.append([name])

    keyboard.append(
        ["✦ Не знаю, нужна консультация"]
    )
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )    
def after_booking_menu():

    keyboard = [

        ["Посмотреть процедуры"],

        ["О клинике"],

        ["✓ Завершить"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
async def send_application_to_admin(context, data):

    text = (
        "🤍 Новая заявка Aurelia Clinic\n\n"
        f"Имя: {data.get('name')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Процедура: {data.get('procedure')}\n\n"
        "Ожидает связи с клиентом."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )
    sheet.append_row([
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        data.get("name"),
        data.get("phone"),
        data.get("procedure")
    ])
# =========================
# START
# =========================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("procedure", None)
    with open(
        "images/clinic.jpg",
        "rb"
    ) as photo:


        await update.message.reply_photo(

            photo=photo,


            caption=

            "AURELIA CLINIC\n\n"

            "Клиника эстетической медицины.\n\n"

            "Персональный подход.\n"
            "Естественная красота.\n"
            "Современные технологии.\n\n"

            "Выберите раздел:",


            reply_markup=main_menu()

        )



# =========================
# ПРОЦЕДУРЫ
# =========================


async def procedures_start(update, context):

    await update.message.reply_text(

        "Выберите направление:",

        reply_markup=directions_menu()

    )



async def show_category(update, context):

    category = update.message.text

    category = category.replace(
    "~",
    ""
).strip()


    await update.message.reply_text(

        "Выберите процедуру:",

        reply_markup=category_menu(category)

    )



# =========================
# КАРТОЧКА
# =========================


async def show_procedure(update, context):

    name = update.message.text


    if name in procedures:

        context.user_data["procedure"] = name


        item = procedures[name]


        image = item["image"]


        with open(
            image,
            "rb"
        ) as photo:


            await update.message.reply_photo(

                photo=photo,


                caption=

                item["title"]

                + "\n"
                "────────────\n\n"

                + item["description"]

                + "\n\n"

                + item["time"]

                + "\n\n"

                + item["price"],


               reply_markup=procedure_menu(
    name,
    item["category"]
)

            )



# =========================
# ПОДРОБНО
# =========================


async def show_details(update, context):

    name = context.user_data.get(
        "procedure"
    )


    if name:


        item = procedures[name]


        await update.message.reply_text(

            item["title"]

            + "\n"
            "────────────\n\n"

            + item["details"],


            reply_markup=details_menu()

        )

# =========================
# ПЕРЕКЛЮЧЕНИЕ ПРОЦЕДУР
# =========================



async def change_procedure(update, context, direction):

    current = context.user_data.get("procedure")


    if not current:
        return


    category = procedures[current]["category"]


    procedure_list = categories_order[category]


    index = procedure_list.index(current)


    new_index = index + direction


    if 0 <= new_index < len(procedure_list):

        new_procedure = procedure_list[new_index]


        context.user_data["procedure"] = new_procedure


        item = procedures[new_procedure]


        with open(
            item["image"],
            "rb"
        ) as photo:


            await update.message.reply_photo(

                photo=photo,


                caption=

                item["title"]

                + "\n"
                "────────────\n\n"

                + item["description"]

                + "\n\n"

                + item["time"]

                + "\n\n"

                + item["price"],


                reply_markup=procedure_menu(
                    new_procedure,
                    item["category"]
                )

            )
# =========================
# ОТМЕНА ЗАПИСИ
# =========================


async def cancel(update, context):

    context.user_data.clear()

    text = update.message.text


    if text == "Отмена":

        await update.message.reply_text(

            "Запись отменена.",

            reply_markup=main_menu()

        )


    elif text == "Процедуры":

        await procedures_start(
            update,
            context
        )


    elif text == "О клинике":

        await about(
            update,
            context
        )


    elif text == "Контакты":

        await contacts(
            update,
            context
        )


    elif text == "Записаться":

        await appointment(
            update,
            context
        )


    return ConversationHandler.END
# =========================
# ЗАПИСЬ
# =========================


async def appointment(update, context):
    context.user_data.pop("procedure", None)
    context.user_data.pop("name", None)
    context.user_data.pop("phone", None)
    await update.message.reply_text(

        "✦ Запись на консультацию\n\n"
        "Введите Ваше имя:",

        reply_markup=ReplyKeyboardMarkup(
            [["Отмена"]],
            resize_keyboard=True
        )

    )

    return NAME
async def confirm_appointment(update, context):

    await update.message.reply_text(
        "✦ Запись на консультацию\n\n"
        "Введите Ваше имя:",
        reply_markup=ReplyKeyboardMarkup(
            [["Отмена"]],
            resize_keyboard=True
        )
    )

    return NAME


async def get_name(update, context):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "Введите номер телефона:"
    )

    return PHONE




async def get_phone(update, context):

    context.user_data["phone"] = update.message.text


    procedure = context.user_data.get("procedure")


    if not procedure:

        await update.message.reply_text(

            "Выберите процедуру:",

            reply_markup=appointment_procedure_menu()

        )

        return PROCEDURE
    if procedure:

        print({
            "name": context.user_data.get("name"),
            "phone": context.user_data.get("phone"),
            "procedure": procedure
        })

    if not context.user_data.get("sent"):

        await send_application_to_admin(
            context,
            context.user_data
    )

        context.user_data["sent"] = True

    if procedure == "Нужна консультация специалиста":

        message = (

            "Спасибо 🤍\n\n"
            "Ваша заявка принята.\n\n"
            "Наш специалист поможет подобрать "
            "подходящую процедуру и ответит "
            "на все вопросы.\n\n"
            "Мы свяжемся с вами в ближайшее время.\n\n"
            "Выберите дальнейшее действие:"
    )

    else:

        message = (

            "Спасибо 🤍\n\n"
            "Ваша заявка принята.\n\n"
            f"Процедура: {procedure}\n\n"
            "Наш специалист свяжется с вами "
            "для уточнения удобного времени.\n\n"
            "Выберите дальнейшее действие:"
    )


    await update.message.reply_text(

        message,

        reply_markup=after_booking_menu()

)


    context.user_data.clear()

    return ConversationHandler.END


    

async def get_procedure(update, context):

    procedure = update.message.text


    if procedure == "✦ Не знаю, нужна консультация":

        context.user_data["procedure"] = (
            "Нужна консультация специалиста"
        )

    else:

        context.user_data["procedure"] = procedure


    if context.user_data.get("procedure") == "Нужна консультация специалиста":

        message = (

            "Спасибо 🤍\n\n"
            "Ваша заявка принята.\n\n"
            "Наш специалист поможет подобрать "
            "подходящую процедуру и ответит "
            "на все вопросы.\n\n"
            "Мы свяжемся с вами в ближайшее время.\n\n"
            "Выберите дальнейшее действие:"
    )

    else:

        message = (

            "Спасибо 🤍\n\n"
            "Ваша заявка принята.\n\n"
            f"Процедура: {context.user_data.get('procedure')}\n\n"
            "Наш специалист свяжется с вами "
            "для уточнения удобного времени.\n\n"
            "Выберите дальнейшее действие:"
    )


    await update.message.reply_text(

        message,

        reply_markup=after_booking_menu()

)


    print(context.user_data)

    if not context.user_data.get("sent"):

        await send_application_to_admin(
            context,
            context.user_data
        )

        context.user_data["sent"] = True
    context.user_data.clear()

    return ConversationHandler.END
# =========================
# О КЛИНИКЕ
# =========================

async def about(update, context):

    await update.message.reply_text(

        "Aurelia Clinic\n\n"
        "Выберите раздел:",

        reply_markup=ReplyKeyboardMarkup(
            clinic_menu,
            resize_keyboard=True
        )

    )

async def show_clinic_section(update, context):

    text = update.message.text

    for key, section in clinic_sections.items():

        if text == section["button"]:

            with open(
                section["photo"],
                "rb"
            ) as photo:

                await update.message.reply_photo(

                    photo=photo,

                    caption=section["text"],

                    reply_markup=ReplyKeyboardMarkup(
                        [
                            ["← Вернуться к разделам"]
                        ],
                        resize_keyboard=True
                    )

                )

            return

async def contacts(update, context):

    with open(
        contacts_data["photo"],
        "rb"
    ) as photo:

        await update.message.reply_photo(

            photo=photo,

            caption=contacts_data["text"],

            parse_mode="HTML",

            reply_markup=ReplyKeyboardMarkup(
                contacts_menu,
                resize_keyboard=True
            )
        )



# =========================
# ОБРАБОТЧИК
# =========================

async def button_handler(update, context):

    text = update.message.text


    if text in [
        "~ История клиники ~",
        "~ Команда ~",
        "~ Наш подход ~",
        "~ Лицензии и стандарты ~"
    ]:

        await show_clinic_section(
            update,
            context
        )

        return

    if text == "Процедуры" or text == "Посмотреть процедуры":

        await procedures_start(
            update,
            context
        )


    elif text.startswith("~"):

        await show_category(
            update,
            context
        )


    elif text in procedures:

        await show_procedure(
            update,
            context
        )


    elif text == "→ Следующая":

        await change_procedure(
            update,
            context,
            1
        )


    elif text == "← Предыдущая":

        await change_procedure(
            update,
            context,
            -1
        )
    elif text == "✦ Записаться":

        procedure = context.user_data.get(
            "procedure"
    )


        if procedure:

            await update.message.reply_text(

                "Вы выбрали:\n\n"
                f"{procedure}\n\n"
                "Записаться на эту процедуру?",

                reply_markup=confirm_procedure_menu()

        )

        else:

            await appointment(
                update,
                context
            )
    elif text == "Отмена":

        context.user_data.clear()

        await update.message.reply_text(

        "Запись отменена.",

            reply_markup=main_menu()

    )

    
    elif text == "Выбрать другую процедуру":

        context.user_data.clear()

        await update.message.reply_text(

            "Хорошо 🤍\n\n"
            "Выберите другую процедуру:",

            reply_markup=directions_menu()

    )
    elif text == "Подробнее":

        await show_details(
            update,
            context
        )


    elif text == "← Вернуться к процедуре":

        name = context.user_data.get("procedure")


        if name:

            item = procedures[name]


            with open(
                item["image"],
                "rb"
            ) as photo:


                await update.message.reply_photo(

                    photo=photo,


                    caption=

                    item["title"]

                    + "\n"
                    "────────────\n\n"

                    + item["description"]

                    + "\n\n"

                    + item["time"]

                    + "\n\n"

                    + item["price"],


                    reply_markup=procedure_menu(
                        name,
                        item["category"]
                    )

                )


    
    elif text == "О клинике":

        await about(
            update,
            context
        )

    elif text == "Контакты":

        await contacts(
            update,
            context
    )

    
    elif text == "✓ Завершить":

        await update.message.reply_text(

            "Спасибо за Ваше доверие.\n\n"
            "Будем рады видеть Вас в Aurelia Clinic.",
            

            reply_markup=main_menu()

    )

    elif text == "Контакты":

        await contacts(
            update,
            context
        )


    elif text == "← Вернуться к направлениям":

        await procedures_start(
            update,
            context
        )


    elif text == "← Вернуться к разделам":

        await about(
            update,
            context
        )

    elif text == "← Назад":

        await start(
            update,
            context
        )


# =========================
# ЗАПУСК
# =========================

async def set_commands(app):

    await app.bot.set_my_commands(
        [
            BotCommand(
                "start",
                "Начать"
            )
        ]
    )
def main():

    request = HTTPXRequest(
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60
    )


    app = Application.builder()\
        .token(TOKEN)\
        .request(request)\
        .post_init(set_commands)\
        .build()

    
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(

    ConversationHandler(

        entry_points=[

    MessageHandler(
        filters.Regex("^Записаться$"),
        appointment
    ),

    MessageHandler(
        filters.Regex("^✓ Да, записаться$"),
        confirm_appointment
    )

],


        states={

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex(
    "^(Процедуры|О клинике|Контакты|Записаться|Отмена|← Назад|← Вернуться к направлениям|Выбрать другую процедуру|✓ Да, записаться|~.*)$"
),
                    get_name
    )
],

            PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex(
    "^(Процедуры|О клинике|Контакты|Записаться|Отмена|← Назад|← Вернуться к направлениям|Выбрать другую процедуру|✓ Да, записаться|~.*)$"
),
                    get_phone
    )
],

            PROCEDURE: [
                MessageHandler(
                    filters.TEXT,
                    get_procedure
                )
            ]

        },


        fallbacks=[

            MessageHandler(

            filters.Regex("^(Процедуры|О клинике|Контакты|Отмена|Записаться)$"),

            cancel

    )

],
        


    )

)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            button_handler
        )
    )


    print(
        "Aurelia Clinic Bot запущен"
    )


    app.run_polling()



if __name__ == "__main__":

    main()