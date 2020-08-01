import logging
import os
import subprocess
import time
import aria2p, re

# initialization, these are the default values
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",  # IP
        port=6800,  # 端口
        secret="eca8a37a216a051d8cb9"  # 密钥
    )
)

downloads = aria2.get_downloads()
logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                    filename='aria2p.log',
                    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    # 日志格式
                    )
         
# 删除空目录
def delete_gap_dir(dir):
    if os.path.isdir(dir):
        for d in os.listdir(dir):
            delete_gap_dir(os.path.join(dir, d))
        if not os.listdir(dir):
            os.rmdir(dir)
            logging.info('移除空目录: ' + dir)


def get_on_complete():
    while True:
        for download in downloads:
            if download.is_complete:
                # print(download.root_files_paths)
                # print(download.followed_by)
                download_path = download.dir
                # print(download.name, download.dir)
                for file in download.files:
                    # print(file)

                    download_path_list = str(download_path).split('\\')
                    file_path_list = str(file).split('\\')
                    new_file_path_list = file_path_list[len(download_path_list):-1]
                    to_path = '{0ALQbt_fX0eycUk9PVA}/' + '/'.join(new_file_path_list)
                    command = 'fclone move "{}" "gc:{}" -P -v'.format(str(file), to_path)
                    ret = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         encoding='utf-8', universal_newlines=True)
                    if ret.returncode == 0:
                        logging.info('{}--上传成功'.format(file.path))
                    else:
                        logging.info('{}--上传失败'.format(file.path))
                download.remove()
                delete_gap_dir(download.root_files_paths)


get_on_complete()
