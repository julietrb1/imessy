# This script fetches iMessages for a given chat and determines conversation statistics

import argparse
import sqlite3
import pandas as pd
import datetime as dt
import numpy as np
import os
import dateutil.parser as dtp
from matplotlib import pyplot as plt

def import_data(chat_id):
    conn = sqlite3.connect(os.path.expanduser('~/Library/Messages/chat.db'))
    c = conn.cursor()

    cmd1 = 'SELECT ROWID, text, handle_id, is_from_me, \
            datetime(date/1000000000 + strftime(\'%s\',\'2001-01-01\'), \'unixepoch\') as date_utc \
            FROM message T1 \
            INNER JOIN chat_message_join T2 \
                ON T2.chat_id=? \
                AND T1.ROWID=T2.message_id \
            ORDER BY T1.date'
    c.execute(cmd1, (chat_id,))
    df_msg = pd.DataFrame(c.fetchall(), columns=['id', 'text', 'sender', 'me', 'time'])
    df = df_msg
    df['time'] = [dt.datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + dt.timedelta(hours=12) for t in df['time']]
    return df

def get_messages(input, my_delays):
    deltas = []
    last_target = None
    for index, m in input.iterrows():
        if m['me'] != my_delays:
            last_target = m
        elif last_target is not None:
            diff = (m['time'] - last_target['time']).to_pytimedelta()
            deltas.append(diff)

    
    return deltas

def get_statistics(input):
    stats = {}

    my_replies = get_messages(input, True)
    stats['My replies'] = np.median(my_replies)
    stats['My slowest reply'] = np.max(my_replies)
    stats['My fastest reply'] = np.min(my_replies)
    stats['My last reply'] = my_replies[-1]

    their_replies = get_messages(input, False)
    stats['Their replies'] = np.median(their_replies)
    stats['Their slowest reply'] = np.max(their_replies)
    stats['Their fastest reply'] = np.min(their_replies)
    stats['Their last reply'] = their_replies[-1]
    
    for label, value in stats.items():
        print(f'{label}: {value}')

def graph_responses(input, figure_no):
    x = input['time'].values
    y = input['me'].values
    plt.xlim((np.min(input['time']), np.max(input['time'])))
    plt.title('Messages sent')
    plt.xticks()
    plt.yticks([1, 0], ['Me', 'Them'])
    plt.scatter(x,y, color='r', s=10)

def graph_days(input, sp):
    min_date = pd.to_datetime(np.min(input['time'])).date()
    max_date = pd.to_datetime(np.max(input['time'])).date()
    bar_width = 0.35
    indices = np.arange(min_date, max_date + dt.timedelta(days=1))
    indices_print = [dt.datetime.utcfromtimestamp((i - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')).date().strftime('%a %d') for i in indices]
    index = np.arange(len(indices))
    my_msgs = []
    their_msgs = []

    for i in indices:
        my_msgs.append(len([x for index, x in input.iterrows() if x['me'] and pd.to_datetime(x['time']).date() == i]))
        their_msgs.append(len([x for index, x in input.iterrows() if not x['me'] and pd.to_datetime(x['time']).date() == i]))

    plt.bar(index, my_msgs, bar_width,
                 color='b',
                 label='Me')
 
    plt.bar(index + bar_width, their_msgs, bar_width,
                    color='g',
                    label='Them')
    
    plt.xlabel('Date')
    plt.ylabel('Messages')
    plt.title('Messages per day')
    plt.xticks(index, indices_print)
    plt.legend()
    sp.plot()

def graph_length(data, should_block: bool):
    recent_hrs = 24
    me = list(d for idx, d in data.iterrows() if d['me'])
    me_recent = list(d for idx, d in data.iterrows() if d['me'] and (dt.datetime.now() - d['time']) < dt.timedelta(hours=recent_hrs))
    them = list(d for idx, d in data.iterrows() if not d['me'])
    them_recent = list(d for idx, d in data.iterrows() if not d['me'] and (dt.datetime.now() - d['time']) < dt.timedelta(hours=recent_hrs))
    box_data = []
    for d in [me, me_recent, them, them_recent]:
        box_data.append([len(t['text']) for t in d])

        
    plt.boxplot(box_data, labels = ['Me', 'Me 24hr', 'Them', 'Them 24hr'])
    plt.xlabel('Sender')
    plt.ylabel('Characters')
    plt.title('Message Length')

def print_delays(data: pd.DataFrame, sp):
    r = data.assign(delay = 0.0).drop(['id', 'sender'], 1)
    for idx, d in r.iterrows():
        if not d['me'] and (idx - 1) in r.index and r.at[idx - 1, 'me']:
            r.at[idx, 'delay'] = (d['time'] - r.at[idx - 1, 'time']).seconds/3600

    for idx, d in r.iterrows():
        if not d['delay']:
            r.drop(idx, inplace=True)


    plot = r.filter(['time', 'delay'], axis='columns')
    
    for idx, p in plot.iterrows():
        plot.at[idx, 'time'] = plot.at[idx, 'time'].date()

    s_times = [d.date().strftime('%a %d') for d in plot.groupby('time').groups.keys()]

    plot['time'] = plot['time'].astype(dt.date)
    
    plot.boxplot(by='time', ax=sp)
    plt.title('Reply Delays')
    plt.xlabel('Date')
    plt.xticks(np.arange(len(s_times)) + 1, s_times)
    plt.ylabel('Time / hrs')
    return r

def graph_times(data: pd.DataFrame, sp: plt.Subplot):
    d = data[['time', 'me']]
    not_me = d['me'] == 0
    d = d[not_me]

    hours = [t['time'].hour for idx, t in d.iterrows()]
    final = pd.DataFrame(hours)
    final.hist(ax=sp, bins=22)
    plt.title('Hours Messages Received')
    plt.xlabel('Hour Received')
    plt.ylabel('Total Messages')
    hr_labels = [0, 6, 12, 18]
    sp.axes.set_xticks(hr_labels)
    sp.axes.set_xticklabels([dt.time(h).strftime('%-I %p') for h in hr_labels])

def config_parser():
    parser = argparse.ArgumentParser(description='Fetch iMessages for a given chat and graph conversation statistics')
    parser.add_argument('chatid', metavar='C', type=int,
                    help='The ID of the iMessage chat to analyse')

    return parser.parse_args()

args = config_parser()
data = import_data(args.chatid)

delays = print_delays(data, plt.subplot(2,2,1))

graph_times(data, plt.subplot(2,2,2))

plt.subplot(2,2,3)
graph_length(data, True)

graph_days(data, plt.subplot(2,2,4))

plt.suptitle('Message Statistics')
plt.show()
