from BaseLogistics import *
import html

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'acie'
        self.name = 'ACI Express'
        self.next = ('unipass', 'regmail-kr')

        # other options
        self.datef = '%Y년 %m월 %d일'
        self.timef = '%Y년 %m월 %d일 %H:%M'

        self.add_query(
            'get', 'html',
            'http://acieshop.com/pod.html'
        )

    def process(self, trackno, year):
        # preparing
        self.params['OrderNo'] = trackno
        self.fetch(True)

        info = get_info_base(self.code, trackno)
        trs = self.root.xpath('(//table//table)[1]/tr')
        for tr in trs:
            tds = tr.xpath('.//td')
            name = tds[0].text_content().strip()
            value = tds[1].text_content().strip()
            info['info'][name] = value

        trs = self.root.xpath('(//table//table)[2]/tr')
        for tr in trs[1:]:
            tds = tr.xpath('./td')
            date = tds[0].text_content().strip()
            time = tds[1].text_content().strip()
            location = tds[2].text_content().strip()
            detail = tds[3].text.strip()
            if time:
                dt = self.parse_time('{} {}'.format(date, time))
                info['prog'].append(ProgV3(dt, location, detail))
            else:
                date = self.parse_date(date)
                info['prog'].append(ProgV6(date, location, detail))

        return info
