#-*- coding:utf-8 -*-
from collections import defaultdict
import re
import os
import yaml

from django.conf import settings

__all__ = ['DFAFilter']

class DFAFilter():
    '''Filter Messages from keywords

    Use DFA to keep algorithm perform constantly
    
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
    '''
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'
    
    def add(self,keyword):
        if not isinstance(keyword,unicode):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[ chars[i] ]
            else:
                if not isinstance(level,dict):
                    break
                for j in range(i,len(chars)):
                    level[ chars[j] ] = {}
                    last_level,last_char = level,chars[j]
                    level = level[ chars[j] ]
                last_level[last_char] = {self.delimit:0}
                break
        if i == len(chars)-1:
            level[self.delimit] = 0

    
    def parse(self,path=settings.THESAURUS_PATH):
        with open(path) as f:
            keywords = yaml.load(f) or []
            for keyword in keywords:
                self.add(keyword.strip())

    def filter(self,message,repl="*"):
        self.parse()
        if not isinstance(message,unicode):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[ char ]:
                        level = level[ char ]
                    else:
                        ret.append( repl*step_ins )
                        start += step_ins - 1
                        break
                else:
                    ret.append( message[start] )
                    break
            start += 1

        return ''.join(ret)