import telebot
import pymorphy2
from pymystem3 import Mystem

# Создание экземпляра бота
API_TOKEN = '7289037695:AAEwvYkSTnr6yalHhni8269nNy0zrvAWPAU'
bot = telebot.TeleBot(API_TOKEN)

# Словари для перевода частей речи, числа, рода и падежа
part_of_speech_dict = {
    'NOUN': 'существительное',
    'VERB': 'глагол',
    'ADJF': 'прилагательное, полное',
    'ADJS': 'прилагательное, краткое',
    'NUMR': 'числительное',
    'INFN': 'инфинитив',
    'PRTF': 'причастие, полное',
    'PRTS': 'причастие, краткое',
    'GRND': 'герундий',
    'ADV': 'наречие',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'PRCL': 'частица',
    'INTJ': 'междометие',
}

part_of_speech_dict2 = {
    'S': 'существительное',
    'V': 'глагол',
    'A': 'прилагательное, полное',
    'ADV': 'наречие',
    'PR': 'предлог',
    'PART': 'частица',
    'CONJ': 'союз',
    'PRON': 'местоимение',
    'NUM': 'числительное',
}
number_dict = {
    'sing': 'единственное',
    'plur': 'множественное',
}

number_dict2 = {
    'ед': 'единственное',
    'мн': 'множественное',
}
# Словарь для перевода рода
gender_dict = {
    'masc': 'мужской',
    'femn': 'женский',
    'neut': 'средний',
}
gender_dict2 = {
    'муж': 'мужской',
    'жен': 'женский',
    'ср': 'средний',
}
# Словарь для перевода падежа
case_dict = {
    'nomn': 'именительный',
    'gent': 'родительный',
    'datv': 'дательный',
    'accs': 'винительный',
    'ablt': 'творительный',
    'loct': 'предложный',
}
case_dict2 = {
    'им': 'именительный',
    'род': 'родительный',
    'дат': 'дательный',
    'вин': 'винительный',
    'твор': 'творительный',
    'предл': 'предложный',
}

def analyze_word(word):
    morph = pymorphy2.MorphAnalyzer()
    parsed_word = morph.parse(word)

    if parsed_word:
        best_analysis = parsed_word[1]
        part_of_speech = part_of_speech_dict.get(best_analysis.tag.POS, best_analysis.tag.POS)
        number = number_dict.get(best_analysis.tag.number, best_analysis.tag.number)
        gender = gender_dict.get(best_analysis.tag.gender, best_analysis.tag.gender)
        case = case_dict.get(best_analysis.tag.case, best_analysis.tag.case)

        return f"Слово: {word}\nЧасть речи: {part_of_speech}\nЧисло: {number}\nРод: {gender}\nПадеж: {case}"
    else:
        return "Не удалось определить слово."

def analyze_word2(word):
    m = Mystem()
    analysis = m.analyze(word)

    if not analysis:
        return f"Не удалось проанализировать слово: {word}"

    output = []
    for item in analysis:
        if 'analysis' in item and item['analysis']:
            gramm_info = item['analysis'][0].get('gr', '')
            parts = gramm_info.split(',')
            part_of_speech = part_of_speech_dict2.get(parts[0] if parts else None)
            number = [part for part in parts if part in ['ед', 'мн']]
            gender = [part for part in parts if part in gender_dict2]
            case = [part for part in parts if part in case_dict2]

            output.append(f"Слово: {word}")
            output.append(f"Часть речи: {part_of_speech}")
            output.append(f"Число: {number_dict2.get(number[0], 'Неизвестно') if number else 'Неизвестно'}")
            output.append(f"Род: {gender_dict2.get(gender[0], 'Неизвестно') if gender else 'Неизвестно'}")
            output.append(f"Падеж: {case_dict2.get(case[0], 'Неизвестно') if case else 'Неизвестно'}")

    return "\n".join(output)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите слово и выберите вариант разбора (1 - pymorphy2, 2 - pymystem3). Пример: 'кот 1'.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.split()
    if len(user_input) < 2:
        bot.reply_to(message, "Пожалуйста, введите слово и номер варианта разбора.")
        return

    word = user_input[0]
    variant = user_input[1]

    if variant == "1":
        result = analyze_word(word)
    elif variant == "2":
        result = analyze_word2(word)
    else:
        result = "Некорректный вариант разбора. Пожалуйста, введите 1 или 2."

    bot.reply_to(message, result)

if __name__ == "__main__":
    bot.polling(none_stop=True)