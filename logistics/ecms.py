from BaseLogistics import *
import re

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'ecms'
        self.name = 'ECMS'
        self.add_query(
            'get', 'html',
            'https://consignee.ecmsglobal.com/brige/showtracking',
            params = {
                'lang': 'en'
            }
        )

    def process(self, trackno, year):
        self.params['trackingno'] = trackno
        self.fetch(True)

        info = get_info_base(self.code, trackno)
        first_time = None
        last_time = None
        if not 'We have not yet received' in self.text:
            items = self.root.xpath('//ul[contains(@class, "e-route")]')[0].xpath('.//li')
            for item in items:
                time = item.xpath('.//div[@class="time"]')[0].text
                if time:
                    if not first_time:
                        first_time = time.strip()
                    last_time = time.strip()

                    date = time.strip()[5:10] #.replace('/', '-')
                    time = time.strip()[11:16]
                    desc = item.xpath('.//div[@class="e-route-process"]/p')[0].text
                    what = item.xpath('.//div[@class="e-route-process"]/b')[0].text
                    city = strip_spaces(item.xpath('.//div[@class="e-route-process"]/span')[0].text_content())
                    if what:
                        what = strip_spaces(what)
                        info['prog'].append(ProgV3(date+time, city, desc, what))
                    else:
                        desc = strip_spaces(desc)
                        info['prog'].append(ProgV3(date+time, city, desc))
            if first_time:
                if first_time > last_time:
                    info['prog'].reverse()

        return info
