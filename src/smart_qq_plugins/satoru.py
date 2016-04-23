# coding: utf-8
import json
import os
from random import randint
import re

from smart_qq_bot.logger import logger
from smart_qq_bot.messages import PrivateMsg
from smart_qq_bot.signals import on_group_message, on_private_message


class Satoru(object):

    def __init__(self, data_file):
        self.data = {}
        self.load(data_file)
        self.data_file = data_file
        self._learn_regex = re.compile("^!learn.?\{(.*?)\}\{(.*?)\}")
        self._remove_regx = re.compile("^!remove (.*)")

    def is_learn(self, key):
        result = re.findall(self._learn_regex, key)
        if result:
            return result[0]
        return None

    def is_remove(self, key):
        result = re.findall(self._remove_regx, key)
        if result:
            return result[0]
        return None

    def load(self, data_file):
        if os.path.isfile(data_file):
            with open(data_file, "r") as f:
                self.data = json.load(f)

    def add_rule(self, key, response):
        if key not in self.data:
            self.data[key] = []

        self.data[key].append(response)
        self.save()

    def remove_rule(self, key):
        if key in self.data:
            del self.data[key]

        self.save()
        logger.info("key [%s] removed" % key)

    def match(self, key):
        for m in self.data:
            if m in key:
                result = self.data[m]
                return result[randint(0, len(result) - 1)]
#         if key in self.data:
#             result = self.data[key]
#             return result[randint(0, len(result) - 1)]
        return None

    def save(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f)
        logger.info("Satoru's data file saved.")


satoru = Satoru("satoru.json")


@on_group_message(name="satoru")
def send_msg(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    group_code = str(msg.group_code)
    result = satoru.is_learn(msg.content)
    if result:
        key, value = result
        if '帮助列表' != key and group_code == '1910383045':
            satoru.add_rule(key, value)
            bot.reply_msg(msg,"学习成功！快对我说" + str(key) + "试试吧！")
    else:
        response = satoru.match(msg.content)
        if response:
            bot.reply_msg(msg, response)
        elif msg.content == '帮助列表':
            result = ""
            for key in satoru.data.keys():
                result += "关键字：{0}\t\t回复：{1}\n".format(key, " / ".join(satoru.data[key]))
            result = result[:-1]
            logger.info("RUNTIMELOG Replying the list of tucao for group {}".format(group_code))
            bot.reply_msg(msg, result)

@on_private_message(name="satoru")
def remove(msg, bot):
    result = satoru.is_remove(msg.content)
    if result:
        satoru.remove_rule(result)