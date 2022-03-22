from time import sleep
import os
import telebot

from dialog_condition import DialogCondition
from moderator import Moderator
import mem_sender
import keyboard

BOT_TOKEN = ''
BOT_INTERVAL = 3
BOT_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN)
memSender = None
all_memes = []
bot_active_dialogs = {}
all_members = []
sending_everyone = False

timetable = ""
chat_link = ""
social_media = ""
maintainer = ""
moderator = None


def init():
    global timetable, maintainer, all_memes, chat_link, moderator, social_media, all_members
    timetable = ""
    chat_link = ""
    moderator = None
    all_members = []

    all_memes = []

    f = open('files/chat_link.txt', 'r', encoding="utf-8")
    for line in f:
        chat_link += line
    f.close()

    f = open('files/timetable.txt', 'r', encoding="utf-8")
    for line in f:
        timetable += line
    f.close()

    f = open('files/social_media.txt', 'r', encoding="utf-8")
    for line in f:
        social_media += line
    f.close()

    f = open('files/members.txt', 'r', encoding="utf-8")
    for line in f:
        all_members.append(line)
    all_members = [line.rstrip() for line in all_members]
    f.close()

    f = open('files/moderator.txt', 'r', encoding="utf-8")
    for line in f:
        moderator = Moderator()
        moderator.username = line
    f.close()

    f = open('files/moderator_id.txt', 'r', encoding="utf-8")
    for line in f:
        moderator.id = line
    f.close()

    f = open('files/maintainer.txt', 'r')
    maintainer = f.read()
    f.close()

    memsDir = 'mems'
    for dir, subdir, files in os.walk(memsDir):
        for file in files:
            all_memes.append(os.path.join(dir, file))


def bot_polling():
    global bot
    print("Starting bot polling now")
    while True:
        try:
            print("New bot instance started")
            init()
            bot_actions()
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex:
            print("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            print("Bot polling loop finished")
            break


def define_acquaintance_request_answer(message):
    is_moderator = str(message.chat.id) == moderator.id
    is_maintainer = message.chat.username == maintainer
    global memSender
    if memSender is None:
        memSender = mem_sender.MemSender()
    if message.chat.username == maintainer:
        bot.send_message(message.chat.id, "Отлично, начинаем. Id игры = " + str(memSender.game_id),
                         reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
        bot.send_message(message.chat.id, "Введите размер группы: ",
                         reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
    else:
        bot.send_message(message.chat.id, "Введи id игры:",
                         reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))


def define_id_request_answer(message):
    is_moderator = str(message.chat.id) == moderator.id
    is_maintainer = message.chat.username == maintainer
    if int(message.text) == memSender.game_id:
        if message.chat.id not in memSender.participants:
            memSender.add_participant(message.chat.id)
        bot.send_message(message.chat.id, "Поздравляю ты в игре! Жди от меня мема 😎",
                         reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
    else:
        bot.send_message(message.chat.id, "Неверный id!", reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))


def define_group_number_answer(message):
    is_moderator = str(message.chat.id) == moderator.id
    is_maintainer = message.chat.username == maintainer
    gr_number = int(message.text)
    if gr_number in range(2, 11):
        memSender.group_number = gr_number
        bot.send_message(message.chat.id, 'Отлично. Размер группы ' + message.text,
                         reply_markup=keyboard.getGameKeyboard())
    else:
        bot.send_message(message.chat.id, 'Не подойдет. Размер группы должен быть от 2 до 10 человек',
                         reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))


def find_appeal(chat_id):
    return bot_active_dialogs.get(chat_id)


def save_question(question):
    f = open("files/tricky_questions.txt", "a", encoding="utf-8")
    f.write(question + "\n")
    f.close()


def save_need(need):
    f = open("files/prayer_needs.txt", "a", encoding="utf-8")
    f.write(need + "\n")
    f.close()


def save_member(chat_id):
    f = open("files/members.txt", "a", encoding="utf-8")
    print(all_members)
    if str(chat_id) not in all_members:
        all_members.append(chat_id)
        f.write(str(chat_id) + "\n")
    f.close()


def get_all_questions():
    result = ""
    f = open('files/tricky_questions.txt', 'r', encoding="utf-8")
    for line in f:
        result += line
    f.close()
    return result


def get_all_needs():
    result = ""
    f = open('files/prayer_needs.txt', 'r', encoding="utf-8")
    for line in f:
        result += line
    f.close()
    return result


def bot_actions():
    @bot.message_handler(commands=['start'], content_types=['text'])
    def send_welcome(message):
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, "Привет, " + message.chat.first_name + "!",
                             reply_markup=keyboard.getStartKeyboard(str(message.chat.id) == moderator.id,
                                                                    message.chat.username == maintainer))
            save_member(message.chat.id)
            if message.chat.username == moderator.username and moderator.id == "":
                moderator.id = message.chat.id
                f = open("files/moderator_id.txt", "w", encoding="utf-8")
                f.write(str(message.chat.id))
                f.close()
                bot.send_message(message.chat.id, "Ты назначен оператором конференции",
                                 reply_markup=keyboard.getStartKeyboard(True, message.chat.username == maintainer))

    @bot.message_handler(content_types=['text'])
    def bot_managering(message):
        global memSender, moderator, sending_everyone, all_members, sending_everyone
        if message.chat.type == 'private':
            appeal = find_appeal(message.chat.id)
            is_moderator = str(message.chat.id) == moderator.id
            is_maintainer = message.chat.username == maintainer

            # region handling queries
            if appeal is not None and appeal == DialogCondition.HELP and message.text != keyboard.main:
                bot.send_message(moderator.id, message.text, reply_markup=keyboard.getReplyKeyBoard(message.chat.id))
                bot.send_message(message.chat.id, keyboard.thanks_for_question,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
                bot_active_dialogs.pop(message.chat.id)
            elif appeal is not None and appeal == DialogCondition.TRICKY_QUESTION and message.text != keyboard.main:
                bot.send_message(message.chat.id, keyboard.thanks_for_tricky_question,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
                bot_active_dialogs.pop(message.chat.id)
                save_question(message.text)
            elif appeal is not None and appeal == DialogCondition.PRAYER_NEED and message.text != keyboard.main:
                bot.send_message(message.chat.id, keyboard.we_will_pray,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
                bot_active_dialogs.pop(message.chat.id)
                save_need(message.text)
            elif message.text == keyboard.main:
                if appeal is not None:
                    bot_active_dialogs.pop(message.chat.id)
                bot.send_message(message.chat.id, keyboard.choose_required_chapter,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif str(message.chat.id) == str(moderator.id) and moderator.opponent_id != "":
                bot.send_message(moderator.opponent_id, message.text,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
                bot.send_message(message.chat.id, keyboard.replied,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))

            # region base information
            elif message.text == keyboard.timetable:
                bot.send_message(message.chat.id, timetable, reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif message.text == keyboard.social_media:
                bot.send_message(message.chat.id, social_media, reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif message.text == keyboard.chat:
                bot.send_message(message.chat.id, chat_link, reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif message.text == keyboard.help:
                bot.send_message(message.chat.id, keyboard.write_your_question, reply_markup=keyboard.getMainKeyboard())
                bot_active_dialogs[message.chat.id] = DialogCondition.HELP
            elif message.text == keyboard.ask_tricky_question:
                bot.send_message(message.chat.id, keyboard.write_your_question, reply_markup=keyboard.getMainKeyboard())
                bot_active_dialogs[message.chat.id] = DialogCondition.TRICKY_QUESTION
            elif message.text == keyboard.write_prayer_need:
                bot.send_message(message.chat.id, keyboard.write_your_need, reply_markup=keyboard.getMainKeyboard())
                bot_active_dialogs[message.chat.id] = DialogCondition.PRAYER_NEED
            elif message.text == keyboard.acquaintance:
                define_acquaintance_request_answer(message)
            elif message.text == keyboard.show_all_questions:
                bot.send_message(message.chat.id, get_all_questions(), reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif message.text == keyboard.show_all_needs:
                bot.send_message(message.chat.id, get_all_needs(), reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))
            elif message.text == keyboard.send_everyone:
                sending_everyone = True
                bot.send_message(message.chat.id, keyboard.type_message, reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))

            # region game elifs
            elif message.chat.username != maintainer and message.text.isdigit():
                define_id_request_answer(message)
            elif message.chat.username == maintainer and message.text.isdigit():
                define_group_number_answer(message)
            elif message.text == keyboard.parts_number:
                answer = keyboard.parts_number + ": " + str(len(memSender.participants))
                bot.send_message(message.chat.id, answer, reply_markup=keyboard.getGameKeyboard())
            elif message.text == keyboard.start_game:
                memSender.send_memes(all_memes, bot)
                bot.send_message(message.chat.id, keyboard.game_started, reply_markup=keyboard.getFinishGameKeyboard())
            elif message.text == keyboard.finish_game:
                memSender = None
                bot.send_message(message.chat.id, keyboard.game_finished,
                                 reply_markup=keyboard.getStartKeyboard(is_moderator, is_maintainer))

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        moderator.opponent_id = call.data
        bot.send_message(call.from_user.id, keyboard.answer, reply_markup=keyboard.getForceReplyKeyboard())

    @bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact', 'poll'])
    def forwarding_messages(message):
        global sending_everyone
        is_maintainer = message.chat.username == maintainer
        if is_maintainer and sending_everyone:
            sending_everyone = False
            for m in all_members:
                bot.forward_message(m, message.chat.id, message.id)


bot_polling()
