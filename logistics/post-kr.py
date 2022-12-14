from BaseLogistics import *
import re

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'post-kr'
        self.name = '대한민국 우체국'
        self.next = ('unipass-ems',)

        self.timef = '%Y.%m.%d %H:%M'

        self.add_query(
            'post', 'html',
            'https://service.epost.go.kr/trace.RetrieveEmsRigiTraceList.comm',
            post = {
                'displayHeader': ''
            }
        )

    def process(self, trackno, year):
        self.post['POST_CODE'] = trackno
        self.fetch(True)

        # general information
        try:
            gen_info = self.root.xpath('//table[@class="table_col ma_b_5"]')[0]
        except:
            if 'window.open("http://www.epost.go.kr/popup/main_notice.html",\'_self\')' in self.text:
                raise LogisticsInMaintenanceError
            else:
                raise
        gen_th = gen_info.xpath('./thead//th')
        gen_td = gen_info.xpath('./tbody//th|./tbody//td')

        if len(gen_th) != len(gen_td):
            if len(gen_td) > 5 and '기록 취급하지 않는 일반우편물' in gen_td[5].text_content():
                return
            raise Exception('Lengh of general item head %d and data %d mismatch' % (len(gen_th), len(gen_td)))

        #if len(html_data) < 500:
        #    return
        info = get_info_base(self.code, trackno)

        for i in range(len(gen_th)):
            if type(gen_td[i].text) is str and len(gen_td[i].text.strip()) > 0:
                info['info'][gen_th[i].text.strip()] = gen_td[i].text.strip()

        progs = self.root.xpath('//table[@class="table_col detail_off ma_t_5"]//tr')[1:]
        for prog in progs:
            tds = prog.xpath('./td')
            time = tds[0].text_content().strip()
            code = tds[1].text_content().strip()
            po = tds[2].text_content().strip()
            for br in tds[3].xpath('.//br'):
                br.tail = '[br]'+br.tail
            messages = []
            for line in tds[3].text_content().split('[br]'):
                line = re.sub(r'\s+', ' ', line).strip()
                if not line: continue
                elif ':' not in line:
                    messages.append(line)
                else:
                    key, var = (x.strip() for x in line.split(':'))
                    if var:
                        info['info'][key] = var
            message = ', '.join(messages)
            if message:
                info['prog'].append(ProgV1(self.parse_time(time), po, code, message))
            else:
                info['prog'].append(ProgV3(self.parse_time(time), po, code))

        # Clean up 발송횟수 by deleting duplicated information
        if '발송횟수' in info['info']:
            info['info']['발송횟수'] = info['info']['발송횟수'].replace(info['info'].get('발송국', ''), '')
            info['info']['발송횟수'] = info['info']['발송횟수'].replace(re.sub(r'\(.+\)', '', info['info'].get('도착예정 교환국', '')), '')

        return info
