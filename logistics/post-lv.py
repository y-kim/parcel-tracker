from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'post-lv'
        self.name = '라트비아 우체국'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://track.pasts.lv/consignment/tracking',
            params = {
                'type': 'pasts',
                'button': 'Track',
            }
        )

    def process(self, pid, year):
        self.params['id'] = pid
        self.fetch(True)

        info = self.get_info_base()
        progs = self.root.xpath('//div[@class="b-delivery"]//tr')
        for prog in reversed(progs):
            tds = prog.xpath('.//td')
            time = tds[0].xpath('.//h4')[0].text_content().strip()
            date = tds[0].xpath('.//p')[0].text_content().strip().rsplit('.',1)[0]
            place = tds[1].text_content().strip()
            desc = tds[2].text_content().strip()
            info['prog'].append(ProgV3(date+time, place, desc))

        return info
