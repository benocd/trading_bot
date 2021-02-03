#!/usr/bin/env python
import re
import time

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F910-\U0001F920"
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def price_variation_pcent(last_price, current_price):
    v = ((100*current_price)/last_price)-100
    return v

def median(maximum,minimum):
    m = maximum-((maximum-minimum)/2)
    return m

def write_log(filename, line):
    current_time = time.localtime()
    ts = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        line = '[' + ts + '] ' + line
        f.write(line.rstrip('\r\n') + '\n' + content)