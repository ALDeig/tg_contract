from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import config
from db import get_reviews, insert_reviews
from misc import dp, bot
import keyboards


class Reviews(StatesGroup):
    answer = State()
    insert = State()


@dp.message_handler(text='😀 Отзывы', state='*')
async def start_reviews(message: Message, state: FSMContext):
    reviews = get_reviews()
    if len(reviews) > 3:
        await message.answer(f'Ваши отзывы о нас:\n\n'
                             f'1. {reviews[0][0]}\n'
                             f'2. {reviews[1][0]}\n'
                             f'3. {reviews[2][0]}\n\n'
                             f'Оставьте свой отзыв или пожелания', reply_markup=keyboards.reviews_key)
        await state.update_data({'reviews': reviews, 'cnt': 3})
        await Reviews.answer.set()
    else:
        if len(reviews) == 0:
            await message.answer('Отзывов пока нет. Оставьте свой отзыв или пожелания', reply_markup=keyboards.key_cancel)
            await Reviews.answer.set()
            return
        text = str()
        cnt = 1
        for review in reviews:
            text += f'{cnt}. {review[0]}\n'
            cnt += 1
        await message.answer(f'{text}\nОставьте свой отзыв или пожелания')
        await Reviews.answer.set()


@dp.message_handler(text='Еще', state=Reviews.answer)
async def send_more_reviews(message: Message, state: FSMContext):
    data = await state.get_data()
    text = str()
    cnt = data['cnt'] + 1
    for review in data['reviews'][cnt:]:
        if cnt < data['cnt'] + 3:
            text += f'{cnt}. {review[0]}\n'
            cnt += 1
        else:
            break

    if cnt < len(data['reviews']):
        keyboard = keyboards.reviews_key
        await state.update_data(cnt=cnt)
    else:
        keyboard = None
    await message.answer(f'{text}\n Оставьте свой отзыв или пожелания.', reply_markup=keyboard)


@dp.message_handler(state=Reviews.answer)
async def get_review(message: Message, state: FSMContext):
    await bot.send_message(chat_id=config.ADMIN_ID, text=f'Новый отзыв:\n{message.text}')
    await message.answer('Спасибо за ваш отзыв!')
    await state.finish()


@dp.message_handler(text='Отзыв', user_id=config.ADMIN_ID, state='*')
async def write_review(message: Message, state: FSMContext):
    await message.answer('Пришли отзыв!')
    await Reviews.insert.set()


@dp.message_handler(state=Reviews.insert, user_id=config.ADMIN_ID)
async def get_review_on_write(message: Message, state: FSMContext):
    insert_reviews(message.text)
    await message.answer('Отзыв записан в базу')
    await state.finish()
