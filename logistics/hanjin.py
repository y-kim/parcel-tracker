from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'hanjin'
        self.name = '한진택배'
        self.next = ('unipass',)

        self.mbl_name = '항공·해상 M-B/L'
        self.timef = '%Y-%m-%d %H:%M'
        self.add_query(
            'get', 'html',
            'https://www.hanjin.com/kor/CMS/DeliveryMgr/WaybillResult.do',
            params = {
                'mCode': 'MN038',
                'schLang': 'KR',
            }
        )

        self.loc_text = (
             ('{location}영업소로 ', ''),
             ('{location}영업소에서 ', ''),
             ('{location}공항터미널에서 ', ''),
             ('{location}물류터미널에서 ', ''),
             ('{location}에서 ', ''),
             ('{location}에 ', ''),
        )

    def process(self, trackno, year):
        self.params['wblnumText2'] = trackno
        self.fetch(True)

        info = get_info_base(self.code, trackno)

        ths = self.root.xpath('//table[@class="board-list-table delivery-tbl"]/thead/tr/th')
        tds = self.root.xpath('//table[@class="board-list-table delivery-tbl"]/tbody/tr/td')
        if len(ths) != len(tds):
            raise ParserError

        for th, td in zip(ths, tds):
            name = th.text_content()
            var = td.text_content()
            if var:
                info['info'][name] = var

        trs = self.root.xpath('//div[@class="waybill-tbl"]//tbody/tr')
        for tr in trs:
            tds = tr.xpath('./td')
            date = tds[0].text_content().strip()
            time = tds[1].text_content().strip()
            dt = self.parse_time(f'{date} {time}')
            location = tds[2].text_content().strip()
            desc = tds[3].xpath('./span')[0].text_content().strip()

            for rep in self.loc_text:
                desc = desc.replace(rep[0].format(location=location), rep[1])
            info['prog'].append(ProgV3(dt, location, desc.strip()))

        return info
