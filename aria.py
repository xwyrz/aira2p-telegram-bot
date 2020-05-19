import time
import aria2p
from telegram.ext import Updater, CommandHandler
import logging

"""修改下面的IP,端口，密钥，机器人的TOKEN"""
aria2 = aria2p.API(
        aria2p.Client(
            host="http://127.0.0.1",  # IP
            port=6800,  # 端口
            secret="abcdefg12345678"  # 密钥
        )
    )
TOKEN = "填写你的机器人TOKEN"

"""-----------------------------------------"""


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('使用/add_magnet <magnet> 来添加任务\r\n使用/set获取当前下载中的任务状态')

# 获取正在下载的任务状态
def get_status(context):
    job = context.job
    msg_id = context.bot.send_message(job.context, text='更新数据中···').message_id
    downloads = aria2.get_downloads()
    text = ""
    wait_count = 0
    for download in downloads:
        if download.status == 'active':
            name = "Filename:{}\r\n".format(download.name)
            size = "Size:{:.2f}GB\r\n".format(download.total_length / 1024 / 1024 / 1024)
            progress = "Progress:[{}{}]{:.2f}%\r\n".format(int(download.progress / 5) * '█',
                                                           (20 - int(download.progress / 5)) * '#', download.progress)
            eta = "ETA:{}\r\n".format(download.eta)
            if download.download_speed > 1024:
                speed = "Speed:{:.2f}Mbps\r\n".format(download.download_speed / 1024 / 1024)
            else:
                speed = "Speed:{:.2f}Kbps\r\n".format(download.download_speed / 1024)
            text_temp = name + size + progress + speed + eta
            text += (text_temp + "\r\n")
        elif download.is_waiting:
            wait_count += 1
    text += "剩余任务数量：{}".format(wait_count)
    msgId = context.bot.editMessageText(chat_id=job.context, message_id=msg_id, text=text).message_id
    time.sleep(5)
    context.bot.deleteMessage(chat_id=job.context, message_id=msgId)


def add_magnet(update, context):
    magnet_uri = context.args[0]
    download = aria2.add_magnet(magnet_uri)
    text = 'Filename:{}--Size:{}添加成功'.format(download.name,download.total_length)
    update.message.reply_text(text)

def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_repeating(get_status, 5, context=chat_id)
        context.chat_data['job'] = new_job
        msg_id = update.message.reply_text('Timer successfully set!').message_id
        time.sleep(0.01)
        context.bot.deleteMessage(chat_id=chat_id,message_id=msg_id)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("add_magnet", add_magnet))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()