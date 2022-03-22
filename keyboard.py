import telebot.types as keyboards

# Кнопки
timetable = "Расписание"
help = "Помощь"
ask_tricky_question = "Задать каверзный вопрос для спикера"
write_prayer_need = "Написать молитвенную нужду"
acquaintance = "Знакомство"
social_media = "Соцсети"
chat = "Чат"
main = "Главная"
reply = "Ответить"

# Кнопки maintainer
start_game = "Начать знакомство"
parts_number = "Количество участников"
finish_game = "Завершить игру"
send_everyone = "Отправить всем"
show_all_questions = "Все каверзные вопросы"
show_all_needs = "Все нужды"

# Ответы бота
thanks_for_question = "Спасибо за твой вопрос. Мы постараемся ответить как можно скорее!"
thanks_for_tricky_question = "Спасибо за твой вопрос!"
we_will_pray = "Будем молиться 🙏"
write_your_question = "Напиши свой вопрос"
write_your_need = "Напиши свою молитвенную просьбу"
answer = "Ответ:"
game_started = "Игра началась!"
game_finished = "Игра окончена"
choose_required_chapter = "Выбери нужный раздел"
replied = "Ответ отправлен"
type_message = "Напишите сообщение"


def getStartKeyboard(is_moderator, is_maintainer):
    keyboard = keyboards.ReplyKeyboardMarkup(True, False)
    keyboard.row(timetable, acquaintance, chat)
    keyboard.row(write_prayer_need, ask_tricky_question, social_media)
    if not is_moderator and not is_maintainer:
        keyboard.row(help)
    if is_maintainer:
        keyboard.row(send_everyone, show_all_needs, show_all_questions)
    return keyboard


def getMainKeyboard():
    keyboard = keyboards.ReplyKeyboardMarkup(True, False)
    keyboard.row(main)
    return keyboard


def getGameKeyboard():
    keyboard = keyboards.ReplyKeyboardMarkup(True, False)
    keyboard.row(start_game, parts_number)
    return keyboard


def getFinishGameKeyboard():
    keyboard = keyboards.ReplyKeyboardMarkup(True, False)
    keyboard.row(finish_game)
    return keyboard


def getReplyKeyBoard(opponent_id):
    keyboard = keyboards.InlineKeyboardMarkup()
    keyboard.add(keyboards.InlineKeyboardButton(reply, callback_data=str(opponent_id)))
    return keyboard


def getForceReplyKeyboard():
    keyboard = keyboards.ForceReply(False)
    return keyboard
