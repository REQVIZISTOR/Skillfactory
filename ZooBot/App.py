import json
import telebot
from Key import KEY
from telebot import types

class QuizBot:
    def __init__(self, token, data_file):
        self.bot = telebot.TeleBot(token)
        self.quiz_started = False
        self.user_responses = []
        self.token = token
        self.data_file = data_file
        with open(data_file, 'r', encoding='utf-8') as file:
            self.data = json.load(file)


    def start(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            self.bot.send_message(message.chat.id,
                                  "Привет! Я бот-викторина, который поможет тебе узнать, какое животное тебе подходит. "
                                  "Готов начать викторину? Просто нажми /quiz, и мы начнем! 🐾", reply_markup=markup)


        @self.bot.message_handler(commands=['quiz'])
        def start_quiz_from_command(message):
            if not self.quiz_started:
                self.quiz_started = True
                self.user_responses.clear()
                self.send_next_question(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, "Викторина уже начата.")


        @self.bot.callback_query_handler(func=lambda call: call.data == 'start_feedback')
        def start_feedback_handler(call):
            chat_id = call.message.chat.id
            self.bot.send_message(chat_id, "Оставьте свой отзыв:")
            self.bot.register_next_step_handler(call.message, save_feedback_handler)

        @self.bot.message_handler(func=lambda message: message.text and message.text.strip() != '' and message.text != 'Оставить отзыв' and not self.quiz_started)
        def save_feedback_handler(message):
            chat_id = message.chat.id
            if message.text:
                feedback_data = {'feedback_text': message.text}
                with open('feedback.json', 'a', encoding='utf-8') as file:
                    file.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
                    self.bot.send_message(chat_id, "Спасибо за ваш отзыв!")
            else:
                self.bot.send_message(chat_id, "Отзыв не может быть пустым. Пожалуйста, напишите отзыв.")

        @self.bot.message_handler(content_types=['text'])
        def check_answer(message):
            if self.quiz_started:
                if message.text.isdigit():
                    user_answer_index = int(message.text) - 1
                    if 0 <= user_answer_index <= 3:
                        self.user_responses.append(user_answer_index)
                        self.send_next_question(message.chat.id)
                    else:
                        self.bot.send_message(message.chat.id, "Пожалуйста, выберите номер варианта ответа от 1 до 4.")
                else:
                    self.bot.send_message(message.chat.id, "Пожалуйста, выберите номер варианта ответа от 1 до 4.")
            else:
                self.bot.send_message(message.chat.id, "Для начала викторины нажмите /quiz.")

        @self.bot.message_handler(content_types=['voice', 'audio', 'document', 'photo'])
        def handle_not_allowed_content(message):
            self.bot.reply_to(message,
                              "Извините, загрузка голосовых сообщений, аудио, фото или документов не разрешена. Пожалуйста, выберите номер варианта ответа от 1 до 4.")

    def send_next_question(self, chat_id):
            if len(self.user_responses) < len(self.data['questions']):
                question = self.data['questions'][len(self.user_responses)]
                self.bot.send_message(chat_id, question['question'])
                for index, option in enumerate(question['options']):
                    self.bot.send_message(chat_id, f"{index + 1}. {option}")
            else:
                self.calculate_result(chat_id)

    def send_try_again_button(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Попробовать ещё раз', callback_data='try_again'))
        markup.add(types.InlineKeyboardButton('Связаться с сотрудником зоопарка', callback_data='contact_employee'))
        markup.add(types.InlineKeyboardButton('Оставить отзыв', callback_data='start_feedback'))
        self.bot.send_message(chat_id,
                              "Хотите попробовать ещё раз, связаться с сотрудником зоопарка или оставить анонимный отзыв, чтобы сделать бота лучше?",
                              reply_markup=markup)

    def handle_try_again_button(self, message, chat_id):
        if message.text == "Попробовать ещё раз":
            self.bot.delete_message(chat_id, message.message_id)
            self.bot.send_message(chat_id, "Отлично! Начнем заново.")
            self.quiz_started = False
            self.user_responses = []
            self.send_next_question(chat_id)


    def calculate_result(self, chat_id):
        if len(self.user_responses) == len(self.data['questions']):
            total_score = 0
            for index, response in enumerate(self.user_responses):
                question = self.data['questions'][index]
                points_for_response = question['points'][response]
                total_score += points_for_response
            result_message = "Ваш результат: "
            url = "https://moscowzoo.ru/my-zoo/become-a-guardian/"

            # Загрузка или инициализация данных из файла "results.json"
            try:
                with open('results.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {"results": []}
            # Поиск результата текущего пользователя
            for result in data["results"]:
                if result["user_id"] == chat_id:
                    # Обновляем результаты текущего пользователя
                    result["score"] = total_score
                    break
            else:
                # Если результата для текущего пользователя нет, создаем новую запись
                user_result = {
                    "user_id": chat_id,
                    "score": total_score,
                }
                data["results"].append(user_result)
            # Запись результатов обратно в файл "results.json"
            with open('results.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            if 24 <= total_score <= 26:
                animal = "Медоед"
                photo = open('Foto/medoed.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + animal + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 27 <= total_score <= 29:
                result_message += "Гималайский Медведь"
                photo = open('Foto/medwed.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 30 <= total_score <= 32:
                result_message += "Черношейная Кобра"
                photo = open('Foto/kobra.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 33 <= total_score <= 35:
                result_message += "Монгольская Жаба"
                photo = open('Foto/zhaba.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 36 <= total_score <= 38:
                result_message += "Полярный Волк"
                photo = open('Foto/wolk.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 39 <= total_score <= 41:
                result_message += "Индийский Лев"
                photo = open('Foto/lew.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 42 <= total_score <= 45:
                result_message += "Благородный Зелено-Красный Попугай"
                photo = open('Foto/popugai.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 46 <= total_score <= 48:
                result_message += "Зебра Греви"
                photo = open('Foto/zebra.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 49 <= total_score <= 51:
                result_message += "Тупорылый Крокодил"
                photo = open('Foto/croko.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            elif 52 <= total_score <= 54:
                result_message += "Папуанский Пингвин"
                photo = open('Foto/pingwin.jpg', 'rb')
                self.bot.send_photo(chat_id, photo,
                                    caption=result_message + f" Вы можете взять под опеку это животное. Если хотите пройти викторину ещё раз нажмите /quiz. Или перейдите по ссылке, чтобы [подробнее узнать о программе опеки для этого или любого другого животного]({url})",
                                    parse_mode="Markdown")
                photo.close()
            self.send_try_again_button(chat_id)

        else:
            self.send_next_question(chat_id)
            pass


    def share_result_on_social_media(self, chat_id, result_text, result_image_path, result_sticker_path):
        # Отправка результата в текстовом формате
        self.bot.send_message(chat_id, result_text)

        # Отправка результата в виде изображения
        with open(result_image_path, 'rb') as photo:
            self.bot.send_photo(chat_id, photo)

        # Отправка результата в виде стикера
        with open(result_sticker_path, 'rb') as sticker:
            self.bot.send_sticker(chat_id, sticker)

    def create_bot_link(self):
        bot_username = self.bot.get_me().username
        return f"https://t.me/{bot_username}"

    def run(self):
        self.start()

        @self.bot.callback_query_handler(func=lambda call: call.data == 'try_again')
        def try_again_handler(call):
            chat_id = call.message.chat.id
            self.bot.delete_message(chat_id, call.message.message_id)
            self.bot.send_message(chat_id, "Отлично! Начинаем заново.")
            self.quiz_started = True
            self.user_responses = []
            self.send_next_question(chat_id)

        @self.bot.callback_query_handler(func=lambda call: call.data == 'contact_employee')
        def contact_employee_handler(call):
            employee_email = "employee@example.com"
            employee_phone = "12345"
            contact_info_message = f"Для получения дополнительной информации вы можете связаться с нами по следующим контактам:\n" \
                                   f"Электронная почта: {employee_email}\n" \
                                   f"Телефон: {employee_phone}"
            self.bot.send_message(call.message.chat.id, "Результат вашей викторины был отправлен нашему сотруднику. "
                                                        "Вы можете связаться с нами при помощи указанных контактов.")
            self.bot.send_message(call.message.chat.id, contact_info_message)

        self.bot.polling()

class QuizError(Exception):
    pass

if __name__ == "__main__":
    bot = QuizBot(KEY, 'databaseofquestions.json')
    bot.run()