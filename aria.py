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
TOKEN = ""  # 填写你的机器人TOKEN
chat_list = [12345678]    # 使用权限。放进用户ID
send_time = 5  #发送消息的间隔。为int类型。不要加引号 由于telegram官方API限制，不要小于3
"""-----------------------------------------"""


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('欢迎使用aria2p_bot\r\n使用 /get_status_once 获取当前任务状态（单次）\r\n使用 /get_status_repeating 获取当前任务状态（持续）\r\n使用 /stop 停止获取任务状态（持续）\r\n使用 /add_magnet <magnet> 添加磁力任务（测试功能）')


def send_msg(context):
    global file_name
    job = context.job
    chat_id = job.context.chat_id
    msg_id = job.context.message_id
    downloads = aria2.get_downloads()
    text = ""
    wait_count = 0
    for download in downloads:
        if download.status == 'active':
            for file in download.files:
                file_name = str(file).split('\\')[-1] # win使用 符号为 \\  linux 使用 符号 /
            name = "Filename:{}\r\n".format(file_name)
            size = "Size:{:.2f}GB\r\n".format(download.total_length / 1024 / 1024 / 1024)
            progress = "Progress:[{}{}]{:.2f}%\r\n".format(int(download.progress / 5) * '█',
                                                               (20 - int(download.progress / 5)) * '#',
                                                               download.progress)
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
    context.bot.editMessageText(chat_id=chat_id, message_id=msg_id, text=text)


# 持续获取任务状态
def get_status_repeating(update,context):
    chat_id = update.message.chat_id
    if chat_id in chat_list:
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        send_message = update.message.reply_text('正在更新数据，请稍后')
        new_job = context.job_queue.run_repeating(send_msg, send_time, context=send_message)
        context.chat_data['job'] = new_job
    else:
        msgId = update.message.reply_text('你没有使用权限。').message_id
        time.sleep(2)
        context.bot.deleteMessage(chat_id=chat_id, message_id=msgId)

# 单次获取任务状态
def get_status_once(update,context):
    chat_id = update.message.chat_id
    if chat_id in chat_list:
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        send_message = update.message.reply_text('正在更新数据，请稍后')
        context.job_queue.run_once(send_msg, 0, context=send_message)
        #context.chat_data['job'] = new_job
    else:
        msgId = update.message.reply_text('你没有使用权限。').message_id
        time.sleep(2)
        context.bot.deleteMessage(chat_id=chat_id, message_id=msgId)


# 停止获取任务状态
def stop(update,context):
    chat_id = update.message.chat_id
    if chat_id in chat_list:
        if 'job' not in context.chat_data:
            update.message.reply_text('当前不是持续获取任务状态')
            return

        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']

        update.message.reply_text(f'持续获取任务状态已成功取消')
    else:
        msgId = update.message.reply_text('你没有使用权限。').message_id
        time.sleep(2)
        context.bot.deleteMessage(chat_id=chat_id, message_id=msgId)


# 添加磁力任务
def add_magnet(update, context):
    chat_id = update.message.chat_id
    if chat_id in chat_list:
        magnet_uri = context.args[0]
        download = aria2.add_magnet(magnet_uri)
        text = 'Filename:{}--Size:{}添加成功'.format(download.name,download.total_length)
        update.message.reply_text(text)
    else:
        msgId = update.message.reply_text('你没有使用权限。').message_id
        time.sleep(2)
        context.bot.deleteMessage(chat_id=chat_id, message_id=msgId)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("add_magnet", add_magnet))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("get_status_once", get_status_once,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("get_status_repeating", get_status_repeating,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("stop", stop, pass_chat_data=True))
    # dp.add_handler(MessageHandler(Filters.text,send_message))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
