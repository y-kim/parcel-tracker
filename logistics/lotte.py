from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)

        self.code = 'lgl'
        self.name = '롯데글로벌로지스(ECMS)'
        self.disabled = True # Recently I doesn't use ECMS

        self.encoding = 'cp949'
        self.add_query(
            'post', 'html',
            'http://global.e-hlc.com/servlet/Tracking_View_DLV_ALL'
        )

    def process(self, pid, year):
        self.post['DvlInvNo'] = pid
        self.fetch(True)

        info = get_info_base()
        if not '조회결과가 없습니다.' in html_data:
            people = self.root.xpath('//tbody[@class="inp_01"]//span')
            info['info']['보내는 사람'] = people[0].text_content().strip()
            info['info']['보내는 주소'] = people[1].text_content().strip()
            info['info']['받는 사람'] = people[2].text_content().strip()
            info['info']['받는 주소'] = people[3].text_content().strip()

            tables = self.root.xpath('//table[@class="table_02"]')
            result = tables[0].xpath('.//td')
            info['info']['HBL'] = result[1].text_content().strip()
            info['info']['배달결과'] = result[2].text_content().strip()

            trs = tables[1].xpath('./tr')
            for tr in trs[1:]:
                tds = tr.xpath('./td')
                date = tds[0].text_content()[5:]
                time = tds[1].text_content().strip()
                loc = tds[2].text_content().strip()
                desc = tds[3].text_content().strip()
                info['prog'].append('{} {} ({}) - {}'.format(date, time, loc, desc))

        return info
