from BaseLogistics import *
import re

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'regmail-kr'
        self.name = '대한민국 등기'

        self.timef = '%Y.%m.%d %H:%M'

        self.add_query(
            'get', 'html',
            'https://service.epost.go.kr/trace.RetrieveDomRigiTraceList.comm',
            params = {
                'displayHeader': 'N'
            }
        )

    def process(self, trackno, year):
        self.params['sid1'] = trackno
        self.fetch(True)

        # general information
        try:
            gen_info = self.root.xpath('//table[@class="table_col"]')[0]
        except:
            if 'window.open("http://www.epost.go.kr/popup/main_notice.html",\'_self\')' in self.text:
                raise LogisticsInMaintenanceError
            else:
                raise
        gen_th = gen_info.xpath('./thead//th')
        gen_td = gen_info.xpath('./tbody//th|./tbody//td')

        if len(gen_th) != len(gen_td):
            if '배달정보를 찾지 못했습니다' in gen_info.xpath('(./tbody//td)[6]')[0].text_content():
                raise NoInformationError
            raise Exception('Lengh of general item head %d and data %d mismatch' % (len(gen_th), len(gen_td)))

        info = get_info_base(self.code, trackno)

        for i in range(len(gen_th)):
            if type(gen_td[i].text) is str and len(gen_td[i].text.strip()) > 0:
                info['info'][gen_th[i].text.strip()] = gen_td[i].text.strip()

        progs = self.root.xpath('//table[@class="table_col detail_off"]//tr')[1:]

        for prog in progs:
            tds = prog.xpath('./td')
            date = tds[0].text_content().strip()
            time = tds[1].text_content().strip()
            dt = '{} {}'.format(date, time)
            for br in tds[2].xpath('.//br'):
                br.tail = ' '+br.tail
            location = merge_spaces(tds[2].text_content().strip())
            for br in tds[3].xpath('.//br'):
                br.tail = ' '+br.tail
            desc = merge_spaces(tds[3].text_content().replace('( ', '(').replace(' )', ')').strip())
            info['prog'].append(ProgV3(self.parse_time(dt), location, desc))

        return info
