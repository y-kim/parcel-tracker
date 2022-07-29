#!/usr/bin/env python3

import re
import logging
import telegram
import time

class TelegramLoginError (Exception): pass
class TelegramGeneralError (Exception): pass

class Telegram(object):
    SPLIT = b'\n'
    SENT_COUNT = 0

    def __init__(self, token, channel_id, header=None):
        self.bot = telegram.Bot(token=token)
        self.channel_id = channel_id
        self.sub_header = ''
        self.max_len = 4096
        if header:
            self.header = header.strip()+'\n'
        else:
            self.header = ''

    def set_sub_header(self, header):
        self.sub_header = header.strip()+'\n'

    def send_message(self, msg, chat_id=None, add_header=False):
        if len(msg.strip()) == 0:
            return

        if add_header:
            msg = self.header+self.sub_header+msg

        msg = re.sub(r'(\s*\r\n\s*)+', '\n', msg)
        enc_msg = msg.encode('utf-8')
        msg_list = []

        if not chat_id:
            chat_id = self.channel_id

        if len(enc_msg) > self.max_len:
            msg_list.append('[[잘린메시지]]')

        # split message before reaching the maximum length.
        # it normally is splitted by 'carriage return' but also available in the middle of message
        while len(enc_msg) > self.max_len:
            p = enc_msg.rfind(self.SPLIT, 0, self.max_len)
            if p == -1:
                p = enc_msg.rfind(b' ', 0, self.max_len)
            msg_list.append(enc_msg[0:p].decode('utf-8'))
            enc_msg = enc_msg[p+len(self.SPLIT):]

        msg_list.append(enc_msg.decode('utf-8'))

        for msg in msg_list:
            while True:
                try:
                    self.bot.sendMessage(chat_id=chat_id, text=msg)
                except telegram.error.RetryAfter as ex:
                    time.sleep(ex.retry_after)
                    continue
                break

class TelegramHandler(logging.Handler):
    def __init__(self, tg, chat_id):
        logging.Handler.__init__(self)
        self.tg = tg
        self.chat_id = chat_id

    def emit(self, record):
        if record.levelno > 30:
            self.tg.send_message(record.msg, self.chat_id, add_header=True)
