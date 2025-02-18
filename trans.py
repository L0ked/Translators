# pip install aiogram googletrans==3.1.0a0
# pip install translate (Microsoft)
# pip install goslate (Yandex)
# pip install PyGithub

from googletrans import Translator

from config import token_tg_trans, token_github
# from config import token_tg_test  # ПОМЕНЯТЬ

from github import Github

import json
import datetime

from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

translator = Translator()

storage = MemoryStorage()
bot = Bot(token=token_tg_trans)  # ПОМЕНЯТЬ
dp = Dispatcher(bot, storage=storage)

git = Github(token_github)
repo = git.get_user().get_repo('translatorsbot')
repo_data = repo.get_contents('dicts.json')  # ПОМЕНЯТЬ
dicts = json.loads(repo_data.decoded_content)

repo_data = repo.get_contents('stat.json')
statistic = json.loads(repo_data.decoded_content)

savetext = {}


def slov_save(slov: dict):
    repo_data = repo.get_contents('dicts.json')  # ПОМЕНЯТЬ
    repo.update_file(repo_data.path, 'loads', str(json.dumps(slov, indent=4)), repo_data.sha, branch='main')


def stat_save(slov: dict):
    repo_data = repo.get_contents('stat.json')
    repo.update_file(repo_data.path, 'loads', str(json.dumps(slov, indent=4)), repo_data.sha, branch='main')


LANGUAGES = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-CN', 'zh-TW',
             'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu',
             'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km',
             'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my',
             'ne', 'no', 'or', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si',
             'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy',
             'xh', 'yi', 'yo', 'zu']


class RefactLangFrom(StatesGroup):
    lang = State()
    lang2 = State()


class RefactLangTo(StatesGroup):
    lang = State()
    lang2 = State()


class LangDetect(StatesGroup):
    text = State()


class UtochLang(StatesGroup):
    lang = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    dicts[f"{message.from_user.id}"] = {"lang": ["en", f"{message.from_user.language_code}"],
                                        "settings": ["googletrans"]}
    lang = message.from_user.language_code
    kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('/menu')
    answer = [
        "Здравствуй дорогой пользователь, я - бот переводчик, могу переводить как сообщения от людей, так и различные статьи.",
        "Есть определения языка, то есть если вы перевели с английского на русский и хотите написать ответ на русском, "
        "язык менять не нужно, бот поймёт что надо перевести на английский",
        'Вызов меню с помощью /menu']
    answer = translator.translate(answer, dest=lang, src='ru')
    await message.answer(answer[0].text, reply_markup=kn)
    await message.answer(answer[1].text)
    a = await message.answer(answer[2].text)
    await bot.pin_chat_message(chat_id=message.from_user.id, message_id=a.message_id)
    slov_save(dicts)


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message, state: FSMContext):
    try:
        await state.finish()
    except:
        pass
    lang = message.from_user.language_code
    if dicts.get(f"{message.from_user.id}") != None:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/from', '/to').add('/lang_detect').add('Close menu')

        answer = ["В меню вы можете настроить с какого языка переводить и на какой. "
                  "Эти базовые настройки нужны для более точного определения речи",
                  'Вы всегда можете изменить их, вызвав меню с помощью /menu',
                  f'Сейчас перевод с {dicts.get(f"{message.from_user.id}").get("lang")[0]} на {dicts.get(f"{message.from_user.id}").get("lang")[1]}']
        answer = translator.translate(answer, dest=lang, src='ru')

        await message.answer(answer[0].text, reply_markup=kn)
        await message.answer(answer[1].text)
        await message.answer(answer[2].text)

    else:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang, src='ru').text,
                             reply_markup=kn)


@dp.message_handler(Text('Close menu'))
async def men(message: types.Message):
    lang = message.from_user.language_code
    await message.answer(translator.translate('Меню закрыто', dest=lang, src='ru').text,
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['lang_detect'])
async def detect(message: types.Message):
    lang = message.from_user.language_code
    if dicts.get(f"{message.from_user.id}") != None:
        answer = 'Введите текст на иностранном языке'
        await message.answer(translator.translate(answer, dest=lang, src='ru').text, reply_markup=ReplyKeyboardRemove())
        await LangDetect.text.set()
    else:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang, src='ru').text,
                             reply_markup=kn)


@dp.message_handler(state=LangDetect.text)
async def detectt(message: types.Message):
    lang = message.from_user.language_code
    text = message.text
    det = translator.detect(text=text)
    answer = f'Текс написан на {det.lang.upper()} с шансом {det.confidence * 100} %'
    await message.answer(translator.translate(answer, dest=lang, src='ru').text)


@dp.message_handler(commands=['from'])
async def fro(message: types.Message):
    lang = message.from_user.language_code
    if dicts.get(f"{message.from_user.id}") != None:
        answer = ['Другой вариант', 'Отмена', "Выберите из уже предоставленных или введите свой вариант"]
        answer = translator.translate(answer, dest=lang, src='ru')

        kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('en', 'de', 'fr').add(
            'es', 'it', 'ru').add(answer[0].text, answer[1].text)
        await message.answer(answer[2].text, reply_markup=kn)
        await RefactLangFrom.lang.set()
    else:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang, src='ru').text,
                             reply_markup=kn)


@dp.message_handler(commands=['to'])
async def t(message: types.Message):
    lang = message.from_user.language_code
    if dicts.get(f"{message.from_user.id}") != None:
        answer = ['Другой вариант', 'Отмена', "Выберите из уже предоставленных или введите свой вариант"]
        answer = translator.translate(answer, dest=lang, src='ru')

        kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('en', 'de', 'fr').add(
            'es', 'it', 'ru').add(answer[0].text, answer[1].text)
        await message.answer(answer[2].text, reply_markup=kn)
        await RefactLangTo.lang.set()
    else:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang, src='ru').text,
                             reply_markup=kn)


@dp.message_handler(state=RefactLangFrom.lang)
async def fromm(message: types.Message, state: FSMContext):
    lang = message.from_user.language_code
    text = message.text
    if text == translator.translate('Другой вариант', dest=lang, src='ru').text:
        answer = ['Отмена', 'Введите код языка']

        answer = translator.translate(answer, dest=lang, src='ru')

        kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(answer[0].text)
        await RefactLangFrom.next()
        await message.answer(answer[1].text, reply_markup=kn)

    elif text == translator.translate('Отмена', dest=lang, src='ru').text:
        await state.finish()
        await message.answer(translator.translate(f'Отмена настройки', dest=lang, src='ru').text,
                             reply_markup=ReplyKeyboardRemove())

    else:
        await state.finish()
        for i in LANGUAGES:
            if text == i:
                dicts[f"{message.from_user.id}"]["lang"][0] = text
                slov_save(dicts)
                await message.answer(translator.translate(f'Язык изменён на {text}', dest=lang, src='ru').text,
                                     reply_markup=ReplyKeyboardRemove())
                break
        else:
            kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('/from').add('/menu')
            await message.answer(
                translator.translate(f'Вы ввели код языка не правильно, попробуйте ещё раз', dest=lang, src='ru').text,
                reply_markup=kn)


@dp.message_handler(state=RefactLangFrom.lang2)
async def fromm1(message: types.Message, state: FSMContext):
    await state.finish()
    lang = message.from_user.language_code
    text = message.text
    if text == translator.translate('Отмена', dest=lang, src='ru').text:
        await message.answer(translator.translate(f'Отмена настройки', dest=lang, src='ru').text,
                             reply_markup=ReplyKeyboardRemove())
    else:
        for i in LANGUAGES:
            if text == i:
                dicts[f"{message.from_user.id}"]["lang"][0] = text
                slov_save(dicts)
                await message.answer(translator.translate(f'Язык изменён на {text}', dest=lang, src='ru').text,
                                     reply_markup=ReplyKeyboardRemove())
                break
        else:
            kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('/from').add('/menu')
            await message.answer(
                translator.translate(f'Вы ввели код языка не правильно, попробуйте ещё раз', dest=lang, src='ru').text,
                reply_markup=kn)


@dp.message_handler(state=RefactLangTo.lang)
async def to(message: types.Message, state: FSMContext):
    lang = message.from_user.language_code
    text = message.text
    if text == translator.translate('Другой вариант', dest=lang, src='ru').text:
        answer = ['Отмена', 'Введите код языка']
        answer = translator.translate(answer, dest=lang, src='ru')

        kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(answer[0].text)
        await RefactLangFrom.next()
        await message.answer(answer[1].text, reply_markup=kn)
    elif text == translator.translate('Отмена', dest=lang, src='ru').text:
        await state.finish()
        await message.answer(translator.translate(f'Отмена настройки', dest=lang, src='ru').text,
                             reply_markup=ReplyKeyboardRemove())
    else:
        await state.finish()
        for i in LANGUAGES:
            if text == i:
                dicts[f"{message.from_user.id}"]["lang"][1] = text
                slov_save(dicts)
                await message.answer(translator.translate(f'Язык изменён на {text}', dest=lang, src='ru').text,
                                     reply_markup=ReplyKeyboardRemove())
                break
        else:
            kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('/to').add('/menu')
            await message.answer(
                translator.translate(f'Вы ввели код языка не правильно, попробуйте ещё раз', dest=lang, src='ru').text,
                reply_markup=kn)


@dp.message_handler(state=RefactLangTo.lang2)
async def to1(message: types.Message, state: FSMContext):
    await state.finish()
    lang = message.from_user.language_code
    text = message.text
    if text == translator.translate('Отмена', dest=lang, src='ru').text:
        await message.answer(translator.translate(f'Отмена настройки', dest=lang, src='ru').text,
                             reply_markup=ReplyKeyboardRemove())
    else:
        for i in LANGUAGES:
            if text == i:
                dicts[f"{message.from_user.id}"]["lang"][1] = text
                slov_save(dicts)
                await message.answer(translator.translate(f'Язык изменён на {text}', dest=lang, src='ru').text,
                                     reply_markup=ReplyKeyboardRemove())
                break
        else:
            kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('/to').add('/menu')
            await message.answer(
                translator.translate(f'Вы ввели код языка не правильно, попробуйте ещё раз', dest=lang, src='ru').text,
                reply_markup=kn)


@dp.message_handler(state=None)
async def perev(message: types.Message):
    info = dicts.get(f"{message.from_user.id}")
    if info != None:
        lang_info = info.get("lang")
        text = message.text
        lang = translator.detect(text=text).lang
        if lang == lang_info[0]:
            per = translator.translate(text=text, src=lang, dest=lang_info[1])
            await message.answer(per.text, reply_markup=ReplyKeyboardRemove())
        elif lang == lang_info[1]:
            per = translator.translate(text=text, src=lang, dest=lang_info[0])
            await message.answer(per.text, reply_markup=ReplyKeyboardRemove())
        else:
            lang = message.from_user.language_code
            savetext[f"{message.from_user.id}"] = text
            await UtochLang.lang.set()
            kn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang_info[0]).add(
                lang_info[1])
            await message.answer(translator.translate('Язык не распознался, уточните на каком языке вы ввели текст',
                                                      dest=lang, src='ru').text, reply_markup=kn)

        """Статистика чисто """
        try:
            statistic[f"{message.from_user.id}"].append(datetime.datetime.now().strftime("%Y-%m-%d"))
        except KeyError:
            statistic[f"{message.from_user.id}"] = [datetime.datetime.now().strftime("%Y-%m-%d")]
        stat_save(statistic)
        """Статистика чисто ^"""
    else:
        lang = message.from_user.language_code
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang, src='ru').text,
                             reply_markup=kn)


@dp.message_handler(state=UtochLang.lang)
async def perev_ut(message: types.Message, state: FSMContext):
    await state.finish()
    lang = message.text
    lang_info = dicts[f"{message.from_user.id}"]["lang"]
    text = savetext.pop(f"{message.from_user.id}")
    if lang == lang_info[0]:
        per = translator.translate(text=text, src=lang, dest=lang_info[1])
        await message.answer(per.text, reply_markup=ReplyKeyboardRemove())
    elif lang == lang_info[1]:
        per = translator.translate(text=text, src=lang, dest=lang_info[0])
        await message.answer(per.text, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types='document')
async def perev_doc(message: types.Message):
    lang_us = message.from_user.language_code
    info = dicts.get(f"{message.from_user.id}")
    if info != None:
        lang_info = info.get("lang")
        await message.answer(
            translator.translate('Файл в переводе, это может занять некоторое время', dest=lang_us, src='ru').text)
        extension = message.document.file_name.split('.')[-1]
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        if extension == 'txt':
            await bot.download_file(file_path, "text.txt")
            with open("text.txt", 'r', encoding='utf-8') as file:
                text = file.read()
                lang = translator.detect(text=text).lang
                if lang == lang_info[0]:
                    per = translator.translate(text=text, src=lang, dest=lang_info[1])
                elif lang == lang_info[1]:
                    per = translator.translate(text=text, src=lang, dest=lang_info[0])
                else:
                    pass
            with open('text.txt', 'w', encoding="utf-8") as file:
                file.write(per.text)
            await bot.send_document(message.from_id, open("text.txt", 'rb'))

        elif extension == 'html':
            await bot.download_file(file_path, "text.html")
            with open("text.html", 'r', encoding='utf-8') as file:
                text = file.read()
                lang = translator.detect(text=text).lang
                if lang == lang_info[0]:
                    per = translator.translate(text=text, src=lang, dest=lang_info[1])
                elif lang == lang_info[1]:
                    per = translator.translate(text=text, src=lang, dest=lang_info[0])
                else:
                    pass
            with open('text.html', 'w', encoding="utf-8") as file:
                file.write(per.text)
            await bot.send_document(message.from_id, open("text.html", 'rb'))


    else:
        kn = ReplyKeyboardMarkup(resize_keyboard=True).add('/start')
        await message.answer(translator.translate(
            "Упс... Ваш аккаунт не найден в базе, сначала напишите /start", dest=lang_us, src='ru').text,
                             reply_markup=kn)


'''Команды админа'''


@dp.message_handler(commands=['/stat_save'])
async def stat(message: types.Message):
    stat_save(statistic)
    await message.answer('Сохранилось')


executor.start_polling(dp)
