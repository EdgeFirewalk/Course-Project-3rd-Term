import telebot
from telebot import types

BOT_TOKEN = ''
bot = telebot.TeleBot(BOT_TOKEN)

import ankiDB

from datetime import datetime, timedelta

import schedule
from threading import Thread
from time import sleep

from random import randrange
import math

available_decks = [] # Колоды пользователя, взятые из БД
selected_deck_name = '' # Имя выбранной колоды для повторения/добавления в неё слов или просмотра слов в ней

is_selecting_deck_to_repeat = False
words_from_repeating_deck = [] # Все слова из выбранной колоды для повторения кидаются сюда
IDs_of_already_repeated_words = [] # ID слов, которые уже были показаны из списка выше, помещаются сюда
repeating_job = 0 # Job объекта schedule, необходимого для создания таймера, присылающего пользователю слова
minutes_per_card = 5 # По-умолчанию карточки из повторяемой колоды присылаются раз в пять минут
is_setting_timer_up = False

is_selecting_deck_to_rename = False
is_renaming_deck = False

is_selecting_deck_to_view_words = False

is_selecting_deck_to_edit_word = False
is_selecting_word_to_edit = False
selected_word_to_edit = [] # Информация о слове, выбранном для редактирования (Id, DeckId, Word, Translation, RepeatDate, DateMultiplier)
is_editing_word = False

is_selecting_deck_to_delete_words = False
is_deleting_words_from_deck = False

is_selecting_deck_to_delete = False

is_creating_new_deck = False

is_selecting_deck_to_add_words = False
is_adding_words_to_deck = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = add_main_menu_buttons()
    bot.send_message(message.chat.id, 'Что Вы хотите сделать?', reply_markup = markup)

@bot.message_handler(content_types='text')
def message_reply(message):
    global available_decks
    global selected_deck_name

    global is_selecting_deck_to_repeat
    global words_from_repeating_deck
    global repeating_job
    global minutes_per_card
    global is_setting_timer_up

    global is_selecting_deck_to_rename
    global is_renaming_deck

    global is_selecting_deck_to_view_words

    global is_selecting_deck_to_edit_word
    global is_selecting_word_to_edit
    global selected_word_to_edit
    global is_editing_word

    global is_selecting_deck_to_delete_words
    global is_deleting_words_from_deck

    global is_selecting_deck_to_delete

    global is_creating_new_deck

    global is_selecting_deck_to_add_words
    global is_adding_words_to_deck

    # ===================== ГЛАВНОЕ МЕНЮ =======================
    if message.text == 'Повторить материал':
        stop_repeating_cards() # Останавливаем повторение слов из колоды, чтобы они не присылались во время работы с меню

        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, из которой хотите повторять слова.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_repeat = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.\n\nСоздайте новую колоду, чтобы добавлять, а затем повторять карточки.')
    
    elif message.text == 'Добавить материал':
        stop_repeating_cards()

        markup = add_create_material_buttons()
        bot.send_message(message.chat.id, 'Что Вы хотите добавить?', reply_markup = markup)

    elif message.text == 'Настройки и управление':
        markup = add_settings_buttons()
        bot.send_message(message.chat.id, 'Выберите желаемую опцию.', reply_markup = markup)
    # ==========================================================

    # =================== СОЗДАНИЕ МАТЕРИАЛА ===================
    elif message.text == 'Создать колоду':
        stop_repeating_cards()

        bot.send_message(message.chat.id, 'Введите название для новой колоды.\n\nВведите \"-\" для отмены.', reply_markup = types.ReplyKeyboardRemove())
        is_creating_new_deck = True
    
    elif message.text == 'Добавить карточки в существующую колоду':
        stop_repeating_cards()

        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, в которую вы хотите добавить слова.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_add_words = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками. Попробуйте добавить материал для изучения.')
    # ==========================================================

    # ================= НАСТРОЙКИ И УПРАВЛЕНИЕ =================
    elif message.text == 'Настроить таймер повторения':
        stop_repeating_cards()

        bot.send_message(message.chat.id, f'Интервал присылания карточек В МИНУТАХ на данный момент: ({minutes_per_card}).\n\nВведите новый интервал для присылания карточек В МИНУТАХ.\n\nВведите \"-\" для отмены.', reply_markup = types.ReplyKeyboardRemove())
        is_setting_timer_up = True

    elif message.text == 'Прекратить повторение колоды':
        stop_repeating_cards()

        bot.send_message(message.chat.id, 'Повторение карточек из выбранной колоды остановлено.')

    elif message.text == 'Посмотреть имеющиеся колоды':
        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks)
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Переименовать колоду':
        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, которую хотите переименовать.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_rename = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Удалить колоду':
        stop_repeating_cards()

        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, которую хотите удалить.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_delete = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Посмотреть карточки в колоде':
        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, карточки из которой вы хотите посмотреть.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_view_words = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Изменить карточку в колоде':
        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, карточку из которой вы хотите изменить.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_edit_word = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Удалить карточку(-и) из колоды':
        available_decks = ankiDB.get_available_decks_from_DB(message.from_user.id)
        if len(available_decks) != 0:
            send_available_decks(message.chat.id, available_decks, True, 'Введите номер колоды, карточку(-и) из которой вы хотите удалить.\n\nВведите \"-\" для отмены.')
            is_selecting_deck_to_delete_words = True
        else:
            bot.send_message(message.chat.id, 'Похоже, у Вас нет существующих колод с карточками.')

    elif message.text == 'Назад':
        markup = add_main_menu_buttons()
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup = markup)
    # ==========================================================

    # ========= КОМАНДЫ ВЫБОРА ИЛИ НЕИЗВЕСТНЫЕ КОМАНДЫ =========
    else:
        if is_selecting_deck_to_repeat:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Выбор колоды для повторения отменён.', reply_markup = markup)
                is_selecting_deck_to_repeat = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)
                        if len(words_from_deck) == 0:
                            bot.send_message(message.chat.id, 'Похоже, эта колода пуста...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
                        else:
                            words_from_repeating_deck = words_from_deck

                            IDs_of_already_repeated_words = [] # Очищаем ранее изученные карточки
                            repeating_job = schedule.every(minutes_per_card).minutes.do(send_card_to_repeat, message.chat.id)

                            bot.send_message(message.chat.id, f'Отлично, @{message.from_user.username}!\n\nТеперь повторяем слова из колоды \"{selected_deck_name}\".\n\nНе забывайте, что Вы можете изменить периодичность присылания слов в настройках бота!', reply_markup = markup)
                            is_selecting_deck_to_repeat = False
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')

        elif is_creating_new_deck:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Создание новой колоды отменено.', reply_markup = markup)
                is_creating_new_deck = False
            else:
                if (not ankiDB.check_if_deck_exists(message.from_user.id, message.text)):
                    ankiDB.add_new_deck_to_DB(message.from_user.id, message.text)

                    bot.send_message(message.chat.id, f'Колода с названием \"{message.text}\" успешно добавлена!', reply_markup = markup)
                    is_creating_new_deck = False
                else:
                    bot.send_message(message.chat.id, f'Колода с названием \"{message.text}\" уже существует, вы можете повторить материал из неё.\n\nВведите название для новой колоды.\n\nВведите \"-\" для отмены.')

        elif is_selecting_deck_to_add_words:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Выбор колоды для добавления отменён.', reply_markup = markup)
                is_selecting_deck_to_add_words = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        bot.send_message(message.chat.id, f'Колода \"{selected_deck_name}\" выбрана!\n\nВведите новое слово в формате \"Слово - Перевод\" или введите несколько таких записей, каждую на новой строке.\n\nВведите \"-\" для отмены.')
                        is_selecting_deck_to_add_words = False
                        is_adding_words_to_deck = True
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
        elif is_adding_words_to_deck:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Добавление карточек в колоду отменено.', reply_markup = markup)
                is_adding_words_to_deck = False
            else:
                try:
                    entries = message.text.split('\n') # Каждое новое слово должно быть на новой строчке
                    words = []
                    for i in range(0, len(entries)):
                        words.append(entries[i].split(' - ')) # Причём слово и перевод должны быть разделены " - "
                        for j in range(0, 2):
                            words[i][j] = ' '.join(words[i][j].split()) # Убираем лишние пробелы
                            if words[i][j] == '': # По обе стороны от " - " должен быть текст (слово и перевод соответственно)
                                raise Exception('No empty words!')

                    now = datetime.now()
                    for i in range(0, len(words)):
                        ankiDB.add_new_card_to_DB(message.from_user.id, selected_deck_name, words[i][0], words[i][1], now.strftime('%d.%m.%Y'))

                    bot.send_message(message.chat.id, f'Слова ({len(entries)}) успешно добавлены в колоду!\n\nВы можете выбрать её для повторения.', reply_markup = markup)
                    is_adding_words_to_deck = False
                except:
                    bot.send_message(message.chat.id, "Мне не удалось выделить слова для добавления из вашего сообщения...\n\nПопробуйте ещё раз или введите \"-\" для отмены.")

        elif is_setting_timer_up:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Изменение настроек таймера отменено.', reply_markup = markup)
                is_setting_timer_up = False
            else:
                try:
                    if int(message.text) > 0:
                        minutes_per_card = int(message.text)

                        bot.send_message(message.chat.id, f'Периодичность присылания карточек в минутах изменена до: ({minutes_per_card}).\n\nВыберите колоду для повторения с новыми настройками.', reply_markup = markup)
                        is_setting_timer_up = False
                    else:
                        bot.send_message(message.chat.id, 'Невозможно установить нулевую или отрицательную периодичность присылания карточек.\n\nВыберите другое время В МИНУТАХ или введите \"-\" для отмены.')
                except:
                    bot.send_message(message.chat.id, 'Невозможно установить введённую длительность интервала.\n\nВыберите другое время В МИНУТАХ или введите \"-\" для отмены.')

        elif is_selecting_deck_to_rename:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Выбор колоды для переименовывания отменён.', reply_markup = markup)
                is_selecting_deck_to_rename = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        bot.send_message(message.chat.id, f'Выберите новое имя для колоды \"{selected_deck_name}\".\n\nВведите \"-\" для отмены.')
                        is_selecting_deck_to_rename = False
                        is_renaming_deck = True
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
        elif is_renaming_deck:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Изменение названия колоды отменено.', reply_markup = markup)
                is_renaming_deck = False
            else:
                new_deck_name = message.text

                ankiDB.rename_deck(message.from_user.id, selected_deck_name, new_deck_name)
                bot.send_message(message.chat.id, f'Название колоды \"{selected_deck_name}\" успешно изменено на \"{new_deck_name}\".', reply_markup = markup)
                is_renaming_deck = False

        elif is_selecting_deck_to_delete:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Выбор колоды для удаления отменён.', reply_markup = markup)
                is_selecting_deck_to_delete = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        ankiDB.delete_deck_from_DB(message.from_user.id, selected_deck_name)
                        bot.send_message(message.chat.id, f'Колода \"{selected_deck_name}\" была успешно удалена.', reply_markup = markup)
                        is_selecting_deck_to_delete = False
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')

        elif is_selecting_deck_to_view_words:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Просмотр карточек из колоды отменён.', reply_markup = markup)
                is_selecting_deck_to_view_words = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)
                        if len(words_from_deck) == 0:
                            bot.send_message(message.chat.id, 'Похоже, эта колода пуста...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
                        else:
                            send_available_cards(message.chat.id, selected_deck_name, words_from_deck, markup)
                            is_selecting_deck_to_view_words = False
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')

        elif is_selecting_deck_to_edit_word:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Выбор колоды для изменения записи отменён.', reply_markup = markup)
                is_selecting_deck_to_edit_word = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)
                        if len(words_from_deck) == 0:
                            bot.send_message(message.chat.id, 'Похоже, эта колода пуста...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
                        else:
                            send_available_cards(message.chat.id, selected_deck_name, words_from_deck, None, 'Выберите номер карточки, которую вы хотите изменить или введите \"-\" для отмены.', )
                            is_selecting_deck_to_edit_word = False
                            is_selecting_word_to_edit = True
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
        elif is_selecting_word_to_edit:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Изменение карточки в колоде изменено.', reply_markup = markup)
                is_selecting_word_to_edit = False
            else:
                try:
                    words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)
                    if (int(message.text)-1 > len(words_from_deck)) or (int(message.text) <= 0):
                        raise Exception('Word is out of bounds!')
                
                    selected_word_to_edit = words_from_deck[int(message.text)-1]
                    bot.send_message(message.chat.id, 'Введите новое значение для карточки в формате \"Слово - Перевод\" или введите \"-\" для отмены.')
                    is_selecting_word_to_edit = False
                    is_editing_word = True
                except:
                    bot.send_message(message.chat.id, 'Похоже, в вводе были ошибки. Попробуйте ещё раз или введите \"-\" для отмены.')
        elif is_editing_word:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Изменение карточки в колоде изменено.', reply_markup = markup)
                is_editing_word = False
            else:
                try:
                    entry = message.text.split(' - ')
                    if len(entry) != 2:
                        raise Exception('Wrong word input!')

                    ankiDB.edit_word_in_deck(message.from_user.id, selected_deck_name, selected_word_to_edit[2], selected_word_to_edit[3], entry[0], entry[1])
                    bot.send_message(message.chat.id, 'Выбранное слово было успешно изменено в колоде.', reply_markup = markup)
                    is_editing_word = False
                except:
                    bot.send_message(message.chat.id, "Мне не удалось выделить новые слово и перевод из вашего сообщения.\n\nПопробуйте ещё раз в формате \"Слово - Перевод\" или введите \"-\" для отмены.")

        elif is_selecting_deck_to_delete_words:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Удаление карточек из колоды отменено.', reply_markup = markup)
                is_selecting_deck_to_delete_words = False
            else:
                try:
                    if int(message.text) > 0:
                        selected_deck_name = available_decks[int(message.text)-1][0]

                        words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)
                        if len(words_from_deck) == 0:
                            bot.send_message(message.chat.id, 'Похоже, эта колода пуста...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
                        else:
                            send_available_cards(message.chat.id, selected_deck_name, words_from_deck, None, 'Выберите номер карточки (или нескольких карточек, разделяя номера пробелами) для удаления из колоды или введите \"-\" для отмены.')
                            is_selecting_deck_to_delete_words = False
                            is_deleting_words_from_deck = True
                    else:
                        raise Exception('No negative deck numbers!')
                except:
                    bot.send_message(message.chat.id, 'Колоды с выбранным номером не существует...\n\nВведите другой номер колоды или введите \"-\" для отмены.')
        elif is_deleting_words_from_deck:
            markup = add_main_menu_buttons()
            if message.text == '-':
                bot.send_message(message.chat.id, 'Удаление карточек из колоды отменено.', reply_markup = markup)
                is_deleting_words_from_deck = False
            else:
                try:
                    word_numbers_to_delete = message.text.split(' ')
                    words_from_deck = ankiDB.get_cards_from_deck(message.from_user.id, selected_deck_name)

                    # Превращаем строки в числа и сразу проверяем валидность ввода
                    for i in range(0, len(word_numbers_to_delete)):
                        word_numbers_to_delete[i] = int(word_numbers_to_delete[i])

                        # Отнимается единица, потому что нумерация в выведенных карточках начинается с единицы
                        if (word_numbers_to_delete[i]-1 > len(words_from_deck)) or (word_numbers_to_delete[i] <= 0):
                            raise Exception('Word out of bounds!')

                    for i in range(0, len(word_numbers_to_delete)):
                        ankiDB.delete_card_from_deck(words_from_deck[word_numbers_to_delete[i]-1][0]) # Передаём ID карточки для удаления

                    bot.send_message(message.chat.id, f'Карточки ({len(word_numbers_to_delete)}) были успешно удалены из колоды \"{selected_deck_name}\".', reply_markup = markup)
                    is_deleting_words_from_deck = False
                except:
                    bot.send_message(message.chat.id, 'Похоже, в вводе были ошибки. Попробуйте ещё раз или введите \"-\" для отмены.')

        else:
            bot.send_message(message.chat.id, "Я не знаю такой команды... \n\nПопробуйте /start для начала работы со мной.", reply_markup = types.ReplyKeyboardRemove())
    # ==========================================================

# Проверяем кнопки под сообщениями с повторяемыми словами
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    word_info = call.data.split(';') # True/False, Id, RepeatDate, DateMultiplier

    if word_info[0] == 'True': # Если пользователь помнит карточку
        if word_info[3] == '1': # Если множитель даты равен одному
            word_info[3] = int(word_info[3]) * 2 # То слово откладывается на два дня
        else:
            word_info[3] = math.floor(int(word_info[3]) * 1.5) # В другом случае карточка откладывается на другое кол-во дней

        # Прибавляем к дате повторения коэффициент увеличения даты (то есть множитель)
        old_repeat_date = datetime.strptime(word_info[2], '%d.%m.%Y')
        new_repeat_date = old_repeat_date + timedelta(days=word_info[3])
        word_info[2] = new_repeat_date.strftime('%d.%m.%Y')
        bot.answer_callback_query(call.id, f"Так держать! Карточка отложена до {word_info[2]}.")

    else: # Если пользователь забыл слово
        word_info[3] = '1' # Сбрасываем количество дней, на которое откладывается карточка
        word_info[2] = datetime.now().strftime('%d.%m.%Y') # Сбрасываем дату повторения карточки
        # Т. е. процесс заучивания начинается заново
        bot.answer_callback_query(call.id, "Ничего страшного! Скоро слово будет выучено.")
    ankiDB.update_word_repeat_date(word_info[1], word_info[2], word_info[3])

def add_main_menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(types.KeyboardButton('Повторить материал'))
    markup.add(types.KeyboardButton('Добавить материал'))
    markup.add(types.KeyboardButton('Настройки и управление'))
    return markup

def add_create_material_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(types.KeyboardButton('Создать колоду'))
    markup.add(types.KeyboardButton('Добавить карточки в существующую колоду'))
    markup.add(types.KeyboardButton('Назад'))
    return markup

def add_settings_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(types.KeyboardButton('Настроить таймер повторения'))
    markup.add(types.KeyboardButton('Прекратить повторение колоды'))
    markup.add(types.KeyboardButton('Посмотреть имеющиеся колоды'))
    markup.add(types.KeyboardButton('Переименовать колоду'))
    markup.add(types.KeyboardButton('Удалить колоду'))
    markup.add(types.KeyboardButton('Посмотреть карточки в колоде'))
    markup.add(types.KeyboardButton('Изменить карточку в колоде'))
    markup.add(types.KeyboardButton('Удалить карточку(-и) из колоды'))
    markup.add(types.KeyboardButton('Назад'))
    return markup

def collect_available_decks(available_decks):
    # Формируется сообщение со всеми доступными колодами
    decks_mgs = 'Ваши колоды:\n'
    for i in range(0, len(available_decks)):
        decks_mgs += f'\n{i+1}. {str(available_decks[i][0])}' # Нумерация начинается с 1 для удобства
    return decks_mgs

def send_available_decks(chat_id, available_decks, hide_markup = False, msg_ending = ''):
    decks_msg = collect_available_decks(available_decks)
    decks_msg += f'\n\n{msg_ending}'
    if hide_markup:
        bot.send_message(chat_id, decks_msg, reply_markup = types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, decks_msg)

def send_available_cards(chat_id, selected_deck_name, words_from_deck, markup = None, msg_ending = ''):
    # Формируется сообщение со всеми доступными карточками
    words_msg = f'Карточки из колоды \"{selected_deck_name}\":\n'
    for i in range(0, len(words_from_deck)):
        words_msg += f'\n{i+1}. {words_from_deck[i][2]} - {words_from_deck[i][3]}' # Нумерация начинается с 1 для удобства
    words_msg += f'\n\n{msg_ending}' # Если есть, то прикрепится, в другом случае ТГ проигнорирует эти переносы
    bot.send_message(chat_id, words_msg, reply_markup = markup)

def add_answer_buttons(card_to_repeat):
    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    
    # True или False означает то, помнит пользователь слово или нет соответственно
    # Остальной текст — текст переданный из send_card_to_repeat()
    keyboard.add(types.InlineKeyboardButton('Помню', callback_data='True;' + card_to_repeat))
    keyboard.add(types.InlineKeyboardButton('Не помню', callback_data='False;' + card_to_repeat))
    return keyboard

def stop_repeating_cards():
    global repeating_job
    global IDs_of_already_repeated_words

    schedule.cancel_job(repeating_job) # Останавливается таймер для повторения текущей колоды
    IDs_of_already_repeated_words = [] # Список уже отправленных карточек очищается

def send_card_to_repeat(chat_id):
    global words_from_repeating_deck
    global IDs_of_already_repeated_words

    card_num_to_pick = 0
    for i in range(0, len(words_from_repeating_deck)):
        # Если дата слова равна сегодняшней и слово ещё не повторялось
        if (words_from_repeating_deck[i][4] == datetime.now().strftime('%d.%m.%Y')) and (words_from_repeating_deck[i][0] not in IDs_of_already_repeated_words):
            card_num_to_pick = i # Выбираем это слово
            break

        # Если дошли до конца массива со словами и так ничего и не нашли на сегодняшнюю дату
        if i == len(words_from_repeating_deck) - 1:
            card_num_to_pick = randrange(0, len(words_from_repeating_deck)) # Берём рандомное слово
            while words_from_repeating_deck[card_num_to_pick][0] in IDs_of_already_repeated_words: # Причём берём рандомные слова, которые ещё не повторялись
                card_num_to_pick = randrange(0, len(words_from_repeating_deck))

    # Прикрепляем к сообщению само слово и через несколько переносов перевод, закрытый спойлером
    word_msg = words_from_repeating_deck[card_num_to_pick][2] + '\n\n\n' + '<span class="tg-spoiler">' + words_from_repeating_deck[card_num_to_pick][3] + '</span>'

    # Собираем информацию о карточке, необходимую для реализации интервального повторения
    card_info_for_btn = []
    card_info_for_btn.append(words_from_repeating_deck[card_num_to_pick][0]) # Забираем Id карточки
    card_info_for_btn.append(words_from_repeating_deck[card_num_to_pick][4]) # Дату для повторения
    card_info_for_btn.append(words_from_repeating_deck[card_num_to_pick][5]) # Множитель даты для повторения
    
    # Разделяем инфу о слове точками с запятой и закидываем в одну строку
    # Id, RepeatDate, DateMultiplier отправляются в кнопки под словом, чтобы потом их можно было изменить и обновить в БД
    keyboard = add_answer_buttons(';'.join(str(el) for el in card_info_for_btn))

    IDs_of_already_repeated_words.append(words_from_repeating_deck[card_num_to_pick][0]) # Отмечаем, что карточка уже была отправлена на повторение
    bot.send_message(chat_id, word_msg, parse_mode='HTML', reply_markup = keyboard)

    if len(words_from_repeating_deck) == len(IDs_of_already_repeated_words): # Если все слова из колоды уже повторены
        bot.send_message(chat_id, 'Это была последняя карточка из колоды!\n\nВы можете выбрать другую колоду или продолжать получать слова из этой (карточки будут идти по кругу), но кнопки под словами не будут работать, пока вы не выберете колоду ещё раз.')
        IDs_of_already_repeated_words = []

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def main():
    scheduleThread = Thread(target = schedule_checker)
    scheduleThread.daemon = True
    scheduleThread.start()

    print('Bot should be running now...')
    bot.polling(non_stop = True)