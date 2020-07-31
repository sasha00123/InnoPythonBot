import logging

from telegram.ext import *

# Enable logging
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

"""
1. /add    => Добавление заметки, ввожу её заголовок и текст.
2. /delete => Удаление по заголовку
3. /read   => Чтение по заголовку
4. /list   => Вывести все заголовки
"""

TITLE, TEXT = range(2)


def start(update, context):
    update.message.reply_text('Hi!')


def add(update, context):
    update.message.reply_text("Введите заголовок:")
    return TITLE


def set_title(update, context):
    title = update.message.text

    context.user_data['title'] = title

    update.message.reply_text("Отлично! А теперь введите текст:")

    return TEXT


def set_text(update, context):
    title = context.user_data['title']
    del context.user_data['title']

    text = update.message.text

    # Если заметок не было ещё, создать ключ notes
    notes = context.user_data.setdefault('notes', {})
    notes[title] = text

    update.message.reply_text("Заметка успешно создана!")

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Успешно отменено!")
    return ConversationHandler.END


def get_notes(update, context):
    notes = context.user_data.get('notes', {})

    response = ""
    for pos, (title, text) in enumerate(notes.items(), start=1):
        response += f"{pos}. {title}: {text}\n"

    update.message.reply_text(response or "Заметок пока что нет!")


READ, REMOVE = range(2)


def read_entry(update, context):
    update.message.reply_text("Введите заголовок заметки, которую нужно прочитать:")
    return READ


def remove_entry(update, context):
    update.message.reply_text("Введите заголовок заметки, которую нужно удалить:")
    return REMOVE


def read(update, context):
    # Берём заголовок
    title = update.message.text

    # Находим такую заметку
    notes = context.user_data.get('notes', {})
    text = notes.get(title, None)

    # Возвращаем текст заметки или сообщаем, что её не существет
    update.message.reply_text(text or 'Такой заметки не существует!')

    # Выходим из диалога
    return ConversationHandler.END


def remove(update, context):
    # Берём заголовок
    title = update.message.text

    # Находим такую заметку
    notes = context.user_data.get('notes', {})
    text = notes.get(title, None)

    # Если не нашлось - сообщаем об этом
    if text is None:
        update.message.reply_text("Такой заметки не существует!")
        return

    # Удаляем
    del notes[title]
    update.message.reply_text("Удалено успешно!")

    # Выходим из диалога
    return ConversationHandler.END


def main():
    updater = Updater(config.TOKEN, use_context=True,
                      persistence=PicklePersistence(filename='bot.dat'))
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", get_notes))

    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("read", read_entry)],
            states={READ: [MessageHandler(Filters.text & ~Filters.command, read)]},
            fallbacks=[CommandHandler("cancel", cancel)]
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("delete", remove_entry)],
            states={REMOVE: [MessageHandler(Filters.text & ~Filters.command, remove)]},
            fallbacks=[CommandHandler("cancel", cancel)]
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add", add)],
            states={
                TITLE: [MessageHandler(Filters.text & ~Filters.command, set_title)],
                TEXT: [MessageHandler(Filters.text & ~ Filters.command, set_text)]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
    )

    if config.HEROKU_APP_NAME is None:
        # У нас на компьютере
        updater.start_polling()
    else:
        # На Heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=config.PORT,
                              url_path=config.TOKEN)
        updater.bot.set_webhook(f"https://{config.HEROKU_APP_NAME}.herokuapp.com/" + config.TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
