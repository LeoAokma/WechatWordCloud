# WordCloud PJ
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import sqlite3 as db
import os
import sys
import numpy as np
from PIL import Image


def check_words(msg):
    state = True
    strange_words = ['xml version',
                     'sysmsg',
                     '<emoji',
                     '<location',
                     '撤回了一条消息',
                     'record fromUser',
                     'createTime',
                     '<img',
                     'pattedUser',
                     'quot wxid',
                     '<appmsg',
                     '<videomsg',
                     '<voicemsg',
                     ]
    for _ in strange_words:
        if _ in msg:
            state = False
    return state


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
    run_path = sys.argv[0].split('gen_wordcloud.py')[0]
    is_csv = input('Choose your input format(entering figure 1 or 2):\n1.csv\t2.sqlite db\n').strip() == '1'
    if is_csv:
        msg = read_from_csv('my.csv')
        chat_name = 'csv_chat'
    else:
        dbs = [_ for _ in get_sql_list(run_path) if 'message_' in _]
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
        chat_name = msg_lists[page - 1]['names'][choice]
        print('Choosing Message {}'.format(chat_name))
        target = read_from_sql(dbs[page - 1], 'SELECT * from {}'.format(chat_name))
        msg_df = pd.DataFrame(target,
                         columns=[
                             'TableVer',
                             'MesLocalID',
                             'MesSvrID',
                             'CreateTime',
                             'Message',
                             'Status',
                             'ImgStatus',
                             'Des',
                             'Type'
                         ])
        msg_text = msg_df.loc[msg_df['Type'] == 1]
        msg = list(msg_text["Message"].values)
        cnt = 0
        for _ in msg:
            if 'wxid_' in _:
                cnt +=1
        ratio = cnt / len(msg)
        if ratio >= 0.2:
            is_group = True
        else:
            is_group = False
    return msg, chat_name, is_group


def generate_overall_word_cloud(chat, msg, stopword_set, img=None, max_font=300, num_max=200):
    """
    Generating an overall word cloud of a message record regardless of the person who is speaking.
    This would generate an image file to the directory same as where your code locates.
    :param chat: the specific chat name, str type.
    :param msg: your message list loaded from csv or sql database.
    :param stopword_set: stop word set.
    :return: None
    """
    new_msg = []
    for _ in msg:
        if check_words(_):
            if ':\n' in _:
                proc = _.split(':\n')[-1]
                new_msg.append(proc)
            else:
                new_msg.append(_.strip())
    str_messages = " ".join(new_msg)
    word_split_jieba = jieba.cut(str_messages, cut_all=False)

    # img = np.array(Image.open('2.jpg'))
    word_space = ' '.join(word_split_jieba)
    my_wordcloud = WordCloud(
        width=2560,
        height=1440,
        background_color='black',  # 设置背景颜色
        mask=img,  # 背景图片
        max_words=num_max,  # 设置最大显示的词数
        stopwords=stopword_set,  # 设置停用词
        # 设置字体格式，字体格式 .ttf文件需自己网上下载，最好将名字改为英文，中文名路径加载会出现问题。
        font_path='Songti.ttc',
        max_font_size=max_font,  # 设置字体最大值
        random_state=50,  # 设置随机生成状态，即多少种配色方案
        colormap='Blues'
    ).generate(word_space)

    # plt.imshow(my_wordcloud)
    # plt.axis('off')
    # plt.show()
    my_wordcloud.to_file('{}.jpg'.format(chat))


def generate_individual_word_cloud(chat, msg, stopword_set):
    """
    Generating word clouds of a message record individually for everyone who speaks in a message group.
    Only works when target chat record belongs to a GROUP CHAT!
    This would generate an image file to the directory same as where your code locates.
    :param chat: the specific chat name, str type.
    :param msg: your message list loaded from csv or sql database.
    :param stopword_set: stop word set.
    :return: None
    """
    member_names = []
    member_messages = []
    member_counts = []
    if not os.path.isdir('{}'.format(chat)):
        os.mkdir('{}'.format(chat))
    for _ in msg:
        if check_words(_):
            if ':\n' in _:
                name = _.split(':\n')[0]
                proc = _.split(':\n')[1]
            else:
                name = 'yourself'
                proc = _.strip()

            if name not in member_names:
                member_names.append(name)
                member_messages.append([])
                member_counts.append(0)

            member_messages[member_names.index(name)].append(proc)
            member_counts[member_names.index(name)] += 1

    for msg in member_messages:
        member_name = member_names[member_messages.index(msg)]
        count = member_counts[member_messages.index(msg)]
        str_messages = " ".join(msg)
        word_split_jieba = jieba.cut(str_messages, cut_all=False)

        # img = np.array(Image.open('2.jpg'))
        word_space = ' '.join(word_split_jieba)
        try:
            my_wordcloud = WordCloud(
                width=2560,
                height=1440,
                background_color='black',  # 设置背景颜色
                # mask=img,  # 背景图片
                max_words=200,  # 设置最大显示的词数
                stopwords=stopword_set,  # 设置停用词
                # 设置字体格式，字体格式 .ttf文件需自己网上下载，最好将名字改为英文，中文名路径加载会出现问题。
                font_path='Songti.ttc',
                max_font_size=300,  # 设置字体最大值
                random_state=50,  # 设置随机生成状态，即多少种配色方案
                colormap='Blues'
            ).generate(word_space)

            # plt.imshow(my_wordcloud)
            # plt.axis('off')
            # plt.show()
            my_wordcloud.to_file('{}/{}_{}.jpg'.format(chat, member_name, count))
        except ValueError:
            pass


def main():
    messages, chat_name, is_group = data_loader()
    # Define the stopwords:
    stopwords = set()
    stopwords.update([
        'Doge', 'Smile', 'ThumbsUp', 'Sub', 'Shy', 'Hurt',
        '了', '吗', '咩', '你们', '我', '你', '的', '捂脸', '不', '没', 'wxid', '旺柴',
        '奸笑', '吧', '哦', '啊', '有', '没有', '在', '到', '是', '不是', '这个', '那个',
        '可以', '可能', 'record fromUser', 'wxid_', 'quot wxid', 'createTime', '呲牙',
        '这个', '那个', '这', '那', '和', '抠鼻', '发怒', '快哭', '快哭了', '就是', '所以', '也', '发抖', '还是', '把', '呢',
        '好', '去', '得', '不行', '行', '这样', '那样', '或者', '还', '那么', '一些', '还是', '又', '不过', 'Emm', '还要', '已经',
        '而且', '抠鼻', '两个', '什么', '吃瓜', '就', '他', '她',
    ])

    if is_group:
        print('Chosen chat is detected as a group chat,'
              ' do you want to generate the word cloud for every member individually?')
        is_indvidual = input('(Y/N)\n').strip().upper() == 'Y'
        if is_indvidual:
            print('Generating overall word cloud...')
            generate_overall_word_cloud(chat_name, messages, stopwords)
            print('Generating individual word cloud...')
            generate_individual_word_cloud(chat_name, messages, stopwords)
        else:
            generate_overall_word_cloud(chat_name,
                                        messages,
                                        stopwords,
                                        )
    else:
        generate_overall_word_cloud(chat_name,
                                    messages,
                                    stopwords,
                                    )


if __name__ == '__main__':
    main()

