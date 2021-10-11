from os import name, replace
from typing import Text
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import Throttled
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

global CHECK_VAR

check = InlineKeyboardButton("Подтвердить", callback_data="ok")
back = InlineKeyboardButton("Назад", callback_data="back")

CHECK_VAR = InlineKeyboardMarkup(row_width=1).add(check, back)

token_bot = "2063640931:AAESYzXuzIxrECDgkB48QKSa5V8EI17LSNM"

bot = Bot(token=token_bot)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
print('start')


class States(Helper):
    mode = HelperMode.snake_case
    VARIABLES = ListItem()
    CHECK_VARIABLES = ListItem()
    RENAME_VARIABLES = ListItem()
    RENAME_ANSWERS = ListItem()
    ANSWER = ListItem()


@dp.message_handler(commands=["start"])
async def send_welcome(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    await msg.answer("Введите количество переменных от 2 до 3")
    await state.set_state(States.VARIABLES[0])


@dp.message_handler(state=States.VARIABLES[0])
async def variables(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    try:
        answer = int(msg.text)
        if 3 >= answer >= 2:
            await state.update_data(variables=answer)
            await bot.send_message(chat_id=msg.chat.id, text=f"Количество переменных: {answer}", reply_markup=CHECK_VAR)
            matrix = [[0 for i in range(answer)] for x in range(answer)]
            answer_matrix = [0 for i in range(answer)]
            await state.update_data(matrix=matrix)
            await state.update_data(answer_matrix=answer_matrix)
            await state.set_state(States.CHECK_VARIABLES[0])
        else:
            await msg.answer("Количество переменных должно быть от 1 до 5")
            await msg.answer("Введите количество переменных")
            await state.set_state(States.VARIABLES[0])
    except:
        await msg.answer("В сообщении присутствуют буквы или символы, пожалуйста используйте только цифры без плавающей точки")
        await msg.answer("Введите количество переменных")
        await state.set_state(States.VARIABLES[0])


@dp.callback_query_handler(state=States.CHECK_VARIABLES[0])
async def check_var(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    ok_var = str(call.data)
    var = await state.get_data()
    matrix = var["matrix"]
    if ok_var == "back":
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="Введите количество переменных")
        await state.set_state(States.VARIABLES[0])

    elif ok_var == "ok":
        g = []
        for x in range(len(matrix)):
            count = 0
            for i in matrix[x]:
                g.append(InlineKeyboardButton(f"{i}", callback_data=f"{x} {count}"))
                count += 1
        btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*g).add(check)
        show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[", "").replace("]", "")
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f"Сейчас под этим сообщением находятся кнопки, каждая кнопка это переменная в матрице соответствующая коэффицентам в уравнениях, которую вы создали. Нажав на кнопку с переменной вы можете её изменить. Когда вы поменяете все значения нажмите на кнопку 'подтвердить', чтобы отредактировать результаты уравнений\nВаша матрица:\n{show_matrix}",
                                    reply_markup=btn)
        await state.set_state(States.RENAME_VARIABLES[0])


@dp.message_handler(state=States.CHECK_VARIABLES[0])
async def check_var(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    var = await state.get_data()

    matrix = var["matrix"]
    x, i = list(map(int, var["index"].split(" ")))
    try:
        answer = int(msg.text)
        matrix[x][i] = answer
        await state.update_data(matrix=matrix)

    except:
        await msg.answer("Введите число")
        await state.set_state(States.CHECK_VARIABLES[0])

    g = []
    for x in range(len(matrix)):
        count = 0
        for i in matrix[x]:
            g.append(InlineKeyboardButton(f"{i}", callback_data=f"{x} {count}"))
            count += 1
    btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*g).add(check)
    show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[", "").replace("]", "")
    await bot.send_message(chat_id=msg.chat.id,
                           text=f"Сейчас под этим сообщением находятся кнопки, каждая кнопка это переменная в матрице соответствующая коэффицентам в уравнениях, которую вы создали. Нажав на кнопку с переменной вы можете её изменить. Когда вы поменяете все значения нажмите на кнопку 'подтвердить', чтобы отредактировать результаты уравнений\nВаша матрица:\n{show_matrix}",
                           reply_markup=btn)
    await state.set_state(States.RENAME_VARIABLES[0])



@dp.callback_query_handler(state=States.RENAME_VARIABLES[0])
async def rename(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    vars = str(call.data)
    var = await state.get_data()
    if vars == "ok":
        show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[","").replace("]", "")
        btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*[InlineKeyboardButton(f"{var['answer_matrix'][i]}", callback_data=f"{i}") for i in range(len(var["answer_matrix"]))]).add(check, back)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f"Отредактируйте результаты уравнений\n{show_matrix}", reply_markup=btn)
        await state.set_state(States.RENAME_ANSWERS[0])
    else:
        await state.update_data(index=vars)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="Введите значение")
        await state.set_state(States.CHECK_VARIABLES[0])


@dp.message_handler(state=States.RENAME_VARIABLES[0])
async def rename(msg: types.Message):
    state = dp.current_state(user=msg.from_user.id)
    var = await state.get_data()
    answer_matrix = var["answer_matrix"]
    i = int(var["index_answer"])
    try:
        answer_matrix[i] = int(msg.text)
        await state.update_data(answer_matrix=answer_matrix)
    except:
        await msg.answer("Введено не число")
        await state.set_state(States.RENAME_VARIABLES[0])
    show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[", "").replace("]", "")
    btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*[InlineKeyboardButton(f"{var['answer_matrix'][i]}", callback_data=f"{i}") for i in range(len(var["answer_matrix"]))]).add(check, back)
    await bot.send_message(chat_id=msg.chat.id,
                                text=f"Отредактируйте результаты уравнений\n{show_matrix}", reply_markup=btn)
    await state.set_state(States.RENAME_ANSWERS[0])

@dp.callback_query_handler(state=States.RENAME_ANSWERS[0])
async def rename_answer(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    vars = str(call.data)
    var = await state.get_data()
    matrix = var["matrix"]
    if vars == "ok":
        show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[","").replace("]", "")
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f"Ваша матрица:\n{show_matrix}", reply_markup=CHECK_VAR)
        await state.set_state(States.ANSWER[0])
    elif vars == "back":
        g = []
        for x in range(len(matrix)):
            count = 0
            for i in matrix[x]:
                g.append(InlineKeyboardButton(f"{i}", callback_data=f"{x} {count}"))
                count += 1
        show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[", "").replace("]", "")
        btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*g).add(check)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f"Сейчас под этим сообщением находятся кнопки, каждая кнопка это переменная в матрице соответствующая коэффицентам в уравнениях, которую вы создали. Нажав на кнопку с переменной вы можете её изменить. Когда вы поменяете все значения нажмите на кнопку 'подтвердить', чтобы отредактировать результаты уравнений\nВаша матрица:\n{show_matrix}",
                                    reply_markup=btn)
        await state.set_state(States.RENAME_VARIABLES[0])
    else:
        await state.update_data(index_answer=vars)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="Введите значение")
        await state.set_state(States.RENAME_VARIABLES[0])

@dp.callback_query_handler(state=States.ANSWER[0])
async def answer(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    vars = str(call.data)
    var = await state.get_data()
    m = var["matrix"]
    ans_m = var["answer_matrix"]
    if vars == "ok":
        print(m)
        print(ans_m)
        if var["variables"] == 2:
            delta_system = (m[0][0]*m[1][1])-(m[1][0]*m[0][1])
            if delta_system == 0:
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"Ответ:\nРешений нет или множество решений")
                await bot.send_message(chat_id=call.message.chat.id,
                                            text="Введите /start чтобы решить еще одно уравниение методом Крамера :)")
                await state.reset_state()
            else:
                delta1 = ans_m[0]*m[1][1] - m[0][1]*ans_m[1]
                delta2 = m[0][0]*ans_m[1] - ans_m[0]*m[1][0]

                answer1 = delta1/delta_system
                answer2 = delta2/delta_system

                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"Определитель системы: {delta_system}\nОпределители:\n Первый {delta1}, Второй {delta1}\nОтвет: x1 = {answer1}, x2 = {answer2}")
                await bot.send_message(chat_id=call.message.chat.id,
                                            text="Введите /start чтобы решить еще одно уравниение методом Крамера :)")
        elif var["variables"] == 3:
            delta_system = (m[0][0]*m[1][1]*m[2][2])+(m[0][1]*m[1][2]*m[2][0])+(m[0][2]*m[2][1]*m[1][0])-(m[0][2]*m[1][1]*m[2][0])-(m[0][1]*m[2][2]*m[1][0])-(m[0][0]*m[1][2]*m[2][1])
            if delta_system == 0:
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"Ответ:\nРешений нет или множество решений")
                await bot.send_message(chat_id=call.message.chat.id,
                                            text="Введите /start чтобы решить еще одно уравниение методом Крамера :)")
                await state.reset_state()
            else:
                delta1 = ans_m[0] * m[1][1] * m[2][2] + m[0][1] * m[1][2] * ans_m[2] + ans_m[1] * m[2][1] * m[0][2] - ans_m[2] * m[1][1] * m[0][2] - ans_m[1] * m[0][1] * m[2][2] - ans_m[0] * m[2][1] * m[1][2]
                delta2 = m[0][0] * ans_m[1] * m[2][2] + ans_m[0] * m[1][2] * m[2][0] + m[1][0] * ans_m[2] * m[0][2] - m[2][0] * ans_m[1] * m[0][2] - m[1][0] * ans_m[0] * m[2][2] - m[0][0] * ans_m[2] * m[1][2]
                delta3 = m[0][0] * m[1][1] * ans_m[2] + m[0][1] * ans_m[1] * m[2][0] + m[1][0] * m[2][1] * ans_m[0] - m[2][0] * m[1][1] * ans_m[0] - m[1][0] * m[0][1] * ans_m[2] - m[0][0] * m[2][1] * ans_m[1]

                answer1 = delta1/delta_system
                answer2 = delta2/delta_system
                answer3 = delta3/delta_system
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"Определитель системы: {delta_system}\nОпределители:\n Первый {delta1}, Второй {delta2}, Третий {delta3}\nОтвет: x1 = {answer1}, x2 = {answer2}, x3 = {answer3}")
                await bot.send_message(chat_id=call.message.chat.id,
                                            text="Введите /start чтобы решить еще одно уравниение методом Крамера :)")
        await state.reset_state()
    elif vars == "back":
        g = []
        for x in range(len(m)):
            count = 0
            for i in m[x]:
                g.append(InlineKeyboardButton(f"{i}", callback_data=f"{x} {count}"))
                count += 1
        show_matrix = "".join([f"{var['matrix'][i]} | {var['answer_matrix'][i]}\n" for i in range(len(var["matrix"]))]).replace("[","").replace("]", "")
        btn = InlineKeyboardMarkup(row_width=var["variables"]).add(*g).add(check)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=f"Сейчас под этим сообщением находятся кнопки, каждая кнопка это переменная в матрице соответствующая коэффицентам в уравнениях, которую вы создали. Нажав на кнопку с переменной вы можете её изменить. Когда вы поменяете все значения нажмите на кнопку 'подтвердить', чтобы отредактировать результаты уравнений\nВаша матрица:\n{show_matrix}",
                                    reply_markup=btn)
        await state.set_state(States.RENAME_VARIABLES[0])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# elif var["variables"] == 4:
        #     delta_system = (m[0][0]*((m[1][1]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][1])+(m[1][3]*m[3][2]*m[2][1])-(m[1][3]*m[2][2]*m[3][1])-(m[1][2]*m[3][3]*m[2][1])-(m[1][1]*m[2][3]*m[3][2])))+\
        #                    (m[0][1]*(-1)*((m[1][0]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][0])+(m[1][3]*m[3][2]*m[2][0])-(m[1][3]*m[2][2]*m[3][0])-(m[1][2]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][2])))+\
        #                    (m[0][2]*((m[1][0]*m[2][1]*m[3][3])+(m[1][1]*m[2][3]*m[3][0])+(m[1][3]*m[3][1]*m[2][0])-(m[1][3]*m[2][1]*m[3][0])-(m[1][1]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][1])))+\
        #                    (m[0][3]*(-1)*((m[1][0]*m[2][1]*m[3][2])+(m[1][1]*m[2][2]*m[3][0])+(m[1][2]*m[3][1]*m[2][0])-(m[1][2]*m[2][1]*m[3][0])-(m[1][1]*m[3][2]*m[2][0])-(m[1][0]*m[2][2]*m[3][1])))
        #     if delta_system == 0:
        #         await bot.edit_message_text(chat_id=call.message.chat.id,
        #                                     message_id=call.message.message_id,
        #                                     text=f"Ответ:\nРешений нет или множество решений")
        #         await state.reset_state()
        #     else:
        #         delta1 = (m[0][0]*((m[1][1]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][1])+(m[1][3]*m[3][2]*m[2][1])-(m[1][3]*m[2][2]*m[3][1])-(m[1][2]*m[3][3]*m[2][1])-(m[1][1]*m[2][3]*m[3][2])))+\
        #                    (m[0][1]*(-1)*((m[1][0]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][0])+(m[1][3]*m[3][2]*m[2][0])-(m[1][3]*m[2][2]*m[3][0])-(m[1][2]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][2])))+\
        #                    (m[0][2]*((m[1][0]*m[2][1]*m[3][3])+(m[1][1]*m[2][3]*m[3][0])+(m[1][3]*m[3][1]*m[2][0])-(m[1][3]*m[2][1]*m[3][0])-(m[1][1]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][1])))+\
        #                    (m[0][3]*(-1)*((m[1][0]*m[2][1]*m[3][2])+(m[1][1]*m[2][2]*m[3][0])+(m[1][2]*m[3][1]*m[2][0])-(m[1][2]*m[2][1]*m[3][0])-(m[1][1]*m[3][2]*m[2][0])-(m[1][0]*m[2][2]*m[3][1])))
        #         delta2 = (m[0][0]*((m[1][1]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][1])+(m[1][3]*m[3][2]*m[2][1])-(m[1][3]*m[2][2]*m[3][1])-(m[1][2]*m[3][3]*m[2][1])-(m[1][1]*m[2][3]*m[3][2])))+\
        #                    (m[0][1]*(-1)*((m[1][0]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][0])+(m[1][3]*m[3][2]*m[2][0])-(m[1][3]*m[2][2]*m[3][0])-(m[1][2]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][2])))+\
        #                    (m[0][2]*((m[1][0]*m[2][1]*m[3][3])+(m[1][1]*m[2][3]*m[3][0])+(m[1][3]*m[3][1]*m[2][0])-(m[1][3]*m[2][1]*m[3][0])-(m[1][1]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][1])))+\
        #                    (m[0][3]*(-1)*((m[1][0]*m[2][1]*m[3][2])+(m[1][1]*m[2][2]*m[3][0])+(m[1][2]*m[3][1]*m[2][0])-(m[1][2]*m[2][1]*m[3][0])-(m[1][1]*m[3][2]*m[2][0])-(m[1][0]*m[2][2]*m[3][1])))
        #         delta3 = (m[0][0]*((m[1][1]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][1])+(m[1][3]*m[3][2]*m[2][1])-(m[1][3]*m[2][2]*m[3][1])-(m[1][2]*m[3][3]*m[2][1])-(m[1][1]*m[2][3]*m[3][2])))+\
        #                    (m[0][1]*(-1)*((m[1][0]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][0])+(m[1][3]*m[3][2]*m[2][0])-(m[1][3]*m[2][2]*m[3][0])-(m[1][2]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][2])))+\
        #                    (m[0][2]*((m[1][0]*m[2][1]*m[3][3])+(m[1][1]*m[2][3]*m[3][0])+(m[1][3]*m[3][1]*m[2][0])-(m[1][3]*m[2][1]*m[3][0])-(m[1][1]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][1])))+\
        #                    (m[0][3]*(-1)*((m[1][0]*m[2][1]*m[3][2])+(m[1][1]*m[2][2]*m[3][0])+(m[1][2]*m[3][1]*m[2][0])-(m[1][2]*m[2][1]*m[3][0])-(m[1][1]*m[3][2]*m[2][0])-(m[1][0]*m[2][2]*m[3][1])))
        #         delta4 = (m[0][0]*((m[1][1]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][1])+(m[1][3]*m[3][2]*m[2][1])-(m[1][3]*m[2][2]*m[3][1])-(m[1][2]*m[3][3]*m[2][1])-(m[1][1]*m[2][3]*m[3][2])))+\
        #                    (m[0][1]*(-1)*((m[1][0]*m[2][2]*m[3][3])+(m[1][2]*m[2][3]*m[3][0])+(m[1][3]*m[3][2]*m[2][0])-(m[1][3]*m[2][2]*m[3][0])-(m[1][2]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][2])))+\
        #                    (m[0][2]*((m[1][0]*m[2][1]*m[3][3])+(m[1][1]*m[2][3]*m[3][0])+(m[1][3]*m[3][1]*m[2][0])-(m[1][3]*m[2][1]*m[3][0])-(m[1][1]*m[3][3]*m[2][0])-(m[1][0]*m[2][3]*m[3][1])))+\
        #                    (m[0][3]*(-1)*((m[1][0]*m[2][1]*m[3][2])+(m[1][1]*m[2][2]*m[3][0])+(m[1][2]*m[3][1]*m[2][0])-(m[1][2]*m[2][1]*m[3][0])-(m[1][1]*m[3][2]*m[2][0])-(m[1][0]*m[2][2]*m[3][1])))
        #
        #         answer1 =
        #         answer2 =
        #         answer3 =
        #         answer4 =
        #         await bot.edit_message_text(chat_id=call.message.chat.id,
        #                                 message_id=call.message.message_id,
        #                                 text=f"Ответ:\nОпределитель системы: {delta_system}\nОпределители: {}")