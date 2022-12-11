from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pytube import YouTube
import config
import logging

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"""Здраствуйте, {message.from_user.full_name}
Я вам помогу скачать аудио или же видео с ютуба""")

class DownloadAudio(StatesGroup):
    download = State()

class DownloadVideo(StatesGroup):
    download = State()

def download(url, type):
    yt = YouTube(url)
    if type == "audio":
        yt.streams.filter(only_audio=True).first().download("audio", f"{yt.title}.mp3")
        return f"{yt.title}.mp3"
    elif type == "video":
        yt.streams.filter(progressive=True, file_extension="mp4").first().download("video", f"{yt.title}.mp4")
        return f"{yt.title}.mp4"

@dp.message_handler(text = ["Аудио", "аудио", "Audio", "audio"])
async def audio(message: types.Message):
    await message.answer("Отправьте ссылку на видео и я вам отправлю его в mp3")
    await DownloadAudio.download.set()

@dp.message_handler(text = ["Видео", "видео", "Video", "video"])
async def video(message: types.Message):
    await message.answer("Отправьте ссылку на видео в ютубе и я вам его отправлю")
    await DownloadVideo.download.set()

@dp.message_handler(state=DownloadAudio.download)
async def download_audio(message: types.Message, state : FSMContext):
    try:
        title = download(message.text, "audio")
        audio = open(f"audio/{title}", "rb")
        await message.answer("Скачиваем файл ожидайте...")
        try:
            await message.answer("Все скачалось вот держи")
            await bot.send_audio(message.chat.id, audio)
        except:
            await message.answer("Произошла ошибка, попробуйте позже")
        await state.finish()
    except:
        await message.answer("Неверная ссылка на видео")
        await state.finish()

@dp.message_handler(state=DownloadVideo.download)
async def download_video(message: types.Message, state : FSMContext):
    try:
        title = download(message.text, "video")
        video = open(f"video/{title}", "rb")
        await message.answer("Скачиваем видео файл ожидайте...")
        try:
            await message.answer("Все скачалось вот держи")
            await bot.send_video(message.chat.id, video)
        except:
            await message.answer("Произошла ошибка, попробуйте позже")
        await state.finish()
    except:
        await message.answer("Неверная ссылка на видео")
        await state.finish()

@dp.message_handler()
async def not_found(message: types.Message):
    await message.reply("Я вас не понял")

executor.start_polling(dp)