import telebot
from pymystem3 import Mystem
import string

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

token = read_file('token')
bot = telebot.TeleBot(token)
m = Mystem()

def expand_gr_tags(gr_tags):
    expanded_tags = []

    tag_dict = {
        'S': 'существительное',
        'V': 'глагол',
        'A': 'прилагательное',
        'ADV': 'наречие',
        'P': 'предлог',
        'NUM': 'числительное',
        'CONJ': 'союз',
        'PR': 'местоимение',
        'PART': 'частица',
        'INFIN': 'инфинитив',
        'sing': 'единственное число',
        'plur': 'множественное число',
        'masc': 'мужской род',
        'femn': 'женский род',
        'neut': 'средний род',
        'anim': 'одушевлённое',
        'inan': 'неодушевлённое',
        'gen': 'родительный падеж',
        'dat': 'дательный падеж',
        'acc': 'винительный падеж',
        'abl': 'творительный падеж',
        'loc': 'предложный падеж',
        'voc': 'звательный падеж',
        'imperf': 'несовершенный вид',
        'perf': 'совершенный вид',
        'past': 'прошедшее время',
        'pres': 'настоящее время',
        'fut': 'будущее время'
    }

    for tag in gr_tags.split(','):
        if '=' in tag:
            main_tag, variants = tag.split('=')
            expanded_tags.append(tag_dict.get(main_tag.strip(), main_tag.strip()))
            for variant in variants.split('|'):
                expanded_tags.append(tag_dict.get(variant.strip(), variant.strip()))
        else:
            expanded_tags.append(tag_dict.get(tag.strip(), tag.strip()))

    return ', '.join(expanded_tags)

@bot.message_handler(func=lambda message: True)
def analyze_sentence(message):
    bot.reply_to(message, "Начинаем анализ...")
    sentence = message.text.translate(str.maketrans('', '', string.punctuation))
    words = sentence.split()

    analysis_results = []
    for word in words:
        analysis = m.analyze(word)
        bot.reply_to(message, f"{analysis}")
        if analysis and 'analysis' in analysis[0] and analysis[0]['analysis']:
            lexeme = analysis[0]['analysis'][0]
            word_analysis = {
                'word': word,
                'lexeme': lexeme.get('lex', 'Unknown'),
                'grammemes': expand_gr_tags(lexeme.get('gr', ''))
            }
            analysis_results.append(word_analysis)

    if analysis_results:
        response = ""
        for result in analysis_results:
            response += f"{result['word']} - {result['lexeme']}\nГраммемы: {result['grammemes']}\n\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Не удалось завершить анализ")


# Запускаем бота
bot.infinity_polling()
