# WordCloud PJ
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import sqlite3 as db
import os
import numpy as np
from PIL import Image


def get_sql_list(folder_dir):
    """
    Get the sqlite file list of given directory.
    :param folder_dir: The folder path you want to check
    :return: the list containing sqlite files.
    """
    sql_list = [_ for _ in os.listdir(folder_dir) if ('sqlite' in _.split('.')[-1]) and not ('-' in _.split('.')[-1])]
    return sql_list


def read_from_sql(sql_dir, cmd):
    conn = db.connect(sql_dir)
    cursor = conn.cursor()  # 该例程创建一个 cursor，将在 Python 数据库编程中用到。
    conn.row_factory = db.Row  # 可访问列信息
    cursor.execute(cmd)  # 该例程执行一个 SQL 语句
    rows = cursor.fetchall()  # 该例程获取查询结果集中所有（剩余）的行，返回一个列表。当没有可用的行时，则返回一个空的列表。
    return rows


def read_from_csv(file_dir):
    """
    Defining a function aimed for loading data from csv files.
    :param file_dir: Your .csv file path
    :return: Str, your messages
    """
    df = pd.read_csv(file_dir,
                     names=[
                         'TableVer',
                         'MesLocalID',
                         'MesSvrID',
                         'CreateTime',
                         'Message',
                         'Status',
                         'ImgStatus',
                         'Type',
                         'Des'
                     ])
    df_text = df.loc[df['Type'] == 1]
    msg = list(df_text["Message"].values)
    return msg


def data_loader():
    is_csv = input('Choose your input format(entering figure 1 or 2):\n1.csv\t2.sqlite db\n').strip() == '1'
    if is_csv:
        msg = read_from_csv('my.csv')
    else:
        dbs = [_ for _ in get_sql_list('/Users/leohe/Documents/WechatDB/DB') if 'message_' in _]
        msg_lists = []
        for database in dbs:
            print('Page {}\tDB:{}'.format(dbs.index(database)+1, database))
            msg_list = read_from_sql(database, 'SELECT * from sqlite_sequence')
            df = pd.DataFrame(msg_list, columns=['names', 'numbers']).sort_values('numbers')
            msg_lists.append(df)
            print(df)
            while True:
                if 'Y' == input('Next Page(?)(Y/N)').strip().upper():
                    break
        page = int(input('Choose the page your message locates(A figure)').strip())
        print('Presenting Your Chosen Page...')
        print(msg_lists[page - 1])
        choice = int(input('Choose the index your message locates').strip())
        print('Choosing Message {}'.format(msg_lists[page - 1]['names'][choice]))
        target = read_from_sql(dbs[page - 1], 'SELECT * from {}'.format(msg_lists[page - 1]['names'][choice]))
        msg_df = pd.DataFrame(target,
                         columns=[
                             'TableVer',
                             'MesLocalID',
                             'MesSvrID',
                             'CreateTime',
                             'Message',
                             'Status',
                             'ImgStatus',
                             'Type',
                             'Des'
                         ])
        msg_text = msg_df.loc[msg_df['Type'] == 1]
        msg = list(msg_text["Message"].values)
    return msg


def main():
    messages = data_loader()
    new_msg = []
    for _ in messages:
        if 'xml version' in _:
            pass
        elif 'sysmsg' in _:
            pass
        elif '<emoji' in _:
            pass
        elif '<location' in _:
            pass
        elif '撤回了一条消息' in _:
            pass
        elif ':' in _:
            proc = _.split(':\n')[-1]
            new_msg += proc
        else:
            new_msg.append(_.strip())
    #print(new_msg)
    str_messages = " ".join(new_msg)

    word_split_jieba = jieba.cut(str_messages, cut_all=False)
    stopwords = set()

    stopwords.update(
        'Doge', 'Smile', 'ThumbsUp', 'Sub', 'Shy', 'Hurt',
        '了', '吗', '咩', '你们', '我', '你', '的', '捂脸', '不', '没'
    )

    # img = np.array(Image.open('2.jpg'))
    word_space = ' '.join(word_split_jieba)
    my_wordcloud = WordCloud(
        width=1400,
        height=800,
        background_color='black', # 设置背景颜色
        # mask=img,  # 背景图片
        max_words=200, # 设置最大显示的词数
        stopwords=stopwords, # 设置停用词
        # 设置字体格式，字体格式 .ttf文件需自己网上下载，最好将名字改为英文，中文名路径加载会出现问题。
        font_path='Songti.ttc',
        max_font_size=200, # 设置字体最大值
        random_state=50, # 设置随机生成状态，即多少种配色方案
        ).generate(word_space)

    plt.imshow(my_wordcloud)
    plt.axis('off')
    plt.show()
    my_wordcloud.to_file('pic.jpg')


if __name__ == '__main__':
    main()
