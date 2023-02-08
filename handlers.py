import random

from aiogram import types
from loader import dp

max_count = 150
total = 0
new_game = False
duel = [] # id - мой и оппонента
first = 0
current = 0


@dp.message_handler(commands=['start', 'старт'])
async def mes_start(message: types.Message):
    name = message.from_user.first_name
    await message.answer(f'{name}, привет! Сегодня сыграем с тобой в конфеты! Для начала игры введи команду /new_game.' 
                         f'за ход можно взяять от 1 до 28 конфент'
                         f'Для настройки конфет введи команду /set и укажи количество конфет и только один раз,во время игры менять количество конфет нельзя!\n'
                         f'Или /duel и id оппонента, для игры вдвоем')
    print({message.from_user.id},{name}) # приходит id кто тыкнул старт
    await message.answer(f'{name} твой id {message.from_user.id}') # приходит id  после старт


@dp.message_handler(commands=['new_game'])
async def mes_new_game(message: types.Message):
    global new_game
    global total
    global max_count
    global first
    new_game = True
    total = max_count
    first = random.randint(0,1)
    if first:
        await message.answer(f'Игра началась. По жребию первым ходит {message.from_user.first_name}! Бери конфеты...')
    else:
        await message.answer(f'Игра началась. По жребию первым ходит Бот')
        await bot_turn(message)


@dp.message_handler(commands=['duel'])
async def mes_duel(message: types.Message):
    global new_game
    global max_count
    global total
    global duel
    global first_turn
    global current
    player = int(message.from_user.id)
    duel.append(player) # мой id (кто вызвал на поединок)
    if len(message.text.split()) > 1:  #обработка на ошибку "Если после /duel не ввели id оппонента"
        opponent = int(message.text.split()[1]) # добавляем split()[1] правую часть команды /duel id
        duel.append(opponent) # id оппонента
        total = max_count
        first_turn = random.randint(0,1)
        if first_turn:
            await dp.bot.send_message(duel[0], f'Первый ход за тобой! Бери конфеты (от 1 до 28)')
            await dp.bot.send_message(duel[1], f'Первый ход за твоим противником. Жди своего хода.')
        else: 
            await dp.bot.send_message(duel[1], f'Первый ход за тобой! Бери конфеты (от 1 до 28)')
            await dp.bot.send_message(duel[0], f'Первый ход за твоим противником. Жди своего хода.')
        current = duel[0] if first_turn ==1 else duel[1]
        new_game = True
    else:
        await message.answer(f'Введи команду /duel и укажи id оппонента через пробел или сыграй с ботом для этого жми /new_game ')


@dp.message_handler(commands=['set'])
async def mes_set(message: types.Message):
    global max_count
    global new_game
    name = message.from_user.first_name
    if len(message.text.split()) > 1:  # обработка на ошибку "Если после /set не ввели количество"
        count = message.text.split()[1]
        if not new_game:
            if count.isdigit():
                max_count = int(count)
                await message.answer(f'Теперь конфет в игре будет {max_count}, жми /new_game или /duel и укажи id оппонента через пробел')
            else:
                await message.answer(f'{name}, напиши цифрами')
        else:
            await message.answer(f'{name}, ЭЭЭ нельзя менять правила во время игры.КОНФЕТЫ НЕ МЕНЯЕМ')
    else:
        await message.answer(f'После команды /set НАПИШИ КОЛИЧЕСТВО КОНФЕТ один раз,или же доиграй игру просто вводя количество конфет от 1 до 28')

        

@dp.message_handler()
async def mes_take_candy(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global first
    name = message.from_user.first_name
    count = message.text
    if len(duel) == 0:
        if new_game:
            if message.text.isdigit() and 0 < int(message.text) < 29:
                total -= int(message.text)
                if total <= 0:
                    await message.answer(f'Ура! {name} ты победил!')
                    new_game = False
                else:
                    await message.answer(f'{name} взял {message.text} конфет. '
                                         f'На столе осталось {total}')
                    await bot_turn(message)
            else:
                await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')
    else:
        if current == int(message.from_user.id):
            name = message.from_user.first_name
            count = message.text
            if new_game:
                if message.text.isdigit() and 0 < int(message.text) < 29:
                    total -= int(message.text)
                    if total <= 0:
                        await message.answer(f'Ура! {name} ты победил!')
                        await dp.bot.send_message(enemy_id(), 'К сожалению ты проиграл! Твой оппонент оказался умнее! :)')
                        new_game = False
                    else:
                        await message.answer(f'{name} взял {message.text} конфет. '
                                             f'На столе осталось {total}')
                        await dp.bot.send_message(enemy_id(), f'Теперь твой ход, бери конфеты! На столе осталось ровно {total}')
                        switch_players()
                else:
                    await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28!')


async def bot_turn(message: types.Message):
    global total
    global new_game
    bot_take = 0
    if 0 < total < 29:
        bot_take = total
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                             f'На столе осталось {total} и бот одержал победу')
        new_game = False
    else:
        remainder = total%29
        bot_take = remainder if remainder != 0 else 28
        total -= bot_take
        await message.answer(f'Бот взял {bot_take} конфет. '
                             f'На столе осталось {total}')

def switch_players():
    global duel
    global current
    if current == duel[0]:
        current = duel[1]
    else:
        current = duel[0]


def enemy_id():
    global duel
    global current
    if current == duel[0]:
        return duel[1]
    else:
        return duel[0]
