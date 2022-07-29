from collections import namedtuple, OrderedDict
from datetime import datetime
import json
import lxml.html
import re

ProgV1 = namedtuple('ProgV1', 'dt loc code desc')
ProgV2 = namedtuple('ProgV2', 'dt desc')
ProgV3 = namedtuple('ProgV3', 'dt loc desc')
ProgV4 = namedtuple('ProgV4', 'dt loc desc desc2')
ProgV5 = namedtuple('ProgV5', 'dt code desc')

def decorate_prog(prog):
    dt = prog.dt.strftime('%m/%d %H:%M')
    if isinstance(prog, ProgV1):
        decorated = '{} ({}) - [{}] {}'.format(dt, prog.loc, prog.code, prog.desc)
    elif isinstance(prog, ProgV2):
        decorated = '{} - {}'.format(dt, prog.desc)
    elif isinstance(prog, ProgV3):
        decorated = '{} ({}) - {}'.format(dt, prog.loc, prog.desc)
    elif isinstance(prog, ProgV4):
        decorated = '{} ({}) - {} / {}'.format(dt, prog.loc, prog.desc, prog.desc2)
    elif isinstance(prog, ProgV5):
        decorated = '{} - [{}] {}'.format(dt, prog.code, prog.desc)

    return decorated

def strip_spaces(text):
    return re.sub(r'\s+', ' ', text.strip())

def remove_pre0(zerotext):
    return re.sub('0(\d+)', r'\1', zerotext)

def get_info_base():
    info = {}
    info['info'] = OrderedDict()
    info['prog'] = []
    return info

def make_24h(time_12h):
    time, unit = time_12h.split()
    hour, minute = (int(x) for x in time.split(':'))
    if unit.replace('.','') == 'PM':
        hour += 12

    return '{:02d}:{:02d}'.format(hour, minute)

def datetime_to_str(dt):
    return '%s/%s %s:%s' % (dt[4:6], dt[6:8], dt[8:10], dt[10:12])

def short_month_name(date):
    short_month = {
            'January'   : 'Jan',
            'February'  : 'Feb',
            'March'     : 'Mar',
            'April'     : 'Apr',
            'May'       : 'May',
            'June'      : 'Jun',
            'July'      : 'Jul',
            'August'    : 'Aug',
            'Septempber': 'Sep',
            'October'   : 'Oct',
            'November'  : 'Nov',
            'December'  : 'Dec',
            }

    for long_name, short_name in short_month.items():
        date = date.replace(long_name, short_name)
    return date

def normalize_month(year, month):
    return year*12 + month

def denormalize_month(nmonth):
    year  = int(nmonth/12)
    month = nmonth%12
    if month == 0:
        month = 12
        year -= 1
    return year, month

class BaseLogistics():
    def __init__(self, tracker):
        self.disabled = False

        self.encoding = 'utf-8'

        self.cfg_save_raw = tracker.cfg_save_raw
        self.cfg_raw_dir = tracker.cfg_raw_dir
        self.cfg_timeout = tracker.cfg_timeout

        self.session = tracker.session
        self.headers = tracker.headers.copy()

        self.req_types = []
        self.res_types = []
        self.urls = []
        self.posts = []
        self.paramses = []

        self.post = {}
        self.params = {}

        self.pos = 0

        self.next = []

    def add_query(self, req_type, res_type, url, params={}, post={}):
        if req_type not in ('get', 'post', 'json'):
            raise Exception('Unsupported request type: {}'.format(req_type))
        if res_type not in ('html', 'json'): # add xml
            raise Exception('Unsupported request type: {}'.format(req_type))

        self.req_types.append(req_type)
        self.res_types.append(res_type)
        self.urls.append(url)
        self.paramses.append(params)
        self.posts.append(post)

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def save_raw(self, raw_data, ext):
        with open('{}/{}.{}'.format(self.cfg_raw_dir, self.code, ext), 'w') as f:
            f.write(raw_data)
            f.close()

    def fetch(self, is_first=False):
        if is_first:
            self.pos = 0

        self.req_type = self.req_types[self.pos]
        self.res_type = self.res_types[self.pos]
        self.url = self.urls[self.pos]
        self.params.update(self.paramses[self.pos])
        self.post.update(self.posts[self.pos])

        if self.req_type == 'post':
            res = self.session.post(self.url, data=self.post, params=self.params, headers=self.headers, timeout=self.cfg_timeout)
        elif self.req_type == 'json':
            res = self.session.post(self.url, json=self.post, params=self.params, headers=self.headers, timeout=self.cfg_timeout)
        elif self.req_type == 'get':
            res = self.session.get(self.url, params=self.params, headers=self.headers, timeout=self.cfg_timeout)
        res.encoding = self.encoding

        if self.cfg_save_raw:
            self.save_raw(res.text, self.res_type)

        self.text = res.text
        if self.res_type == 'html':
            self.root = lxml.html.fromstring(res.text)
        elif self.res_type == 'json':
            self.root = json.loads(res.text, object_pairs_hook=OrderedDict)

        self.post = {}
        self.params = {}
        self.pos += 1
