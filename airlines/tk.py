from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'tk'
        self.name = '터키항공'
        self.mbls = ('235',)
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://comisportal.thy.com/public/shipment-tracking-public/{pid_pre}/{pid_post}'
        )

    def process(self, pid, year):
        self.fetch(True)

        info = get_info_base()
        tables = self.root.xpath('//table[@class="table-n"]')
        try:
            for tr in tables[0].xpath('.//tr'):
                tds = tr.xpath('.//td')
                con = tds[0].text_content().strip()
                text = tds[1].text_content().strip()
                info['info'][con] = text
        except:
            return info

        trs = tables[1].xpath('.//tr')
        i = 1
        for tr in trs[1:]:
            tds = tr.xpath('.//td')
            fno = tds[0].text_content().strip()
            fdate = tds[1].text_content().strip()
            fseg = tds[2].text_content().strip()
            info['info']['Flight %d' % i] = '%s %s %s' % (fno, fdate, fseg)
            i += 1

        trs = tables[2].xpath('.//tr')
        for tr in reversed(trs[1:]):
            tds = tr.xpath('.//td')
            status = tds[0].get('title').split('-')[1].strip()
            code = tds[1].text_content().strip()
            time = tds[4].text_content().strip()
            flight = tds[5].text_content().strip()
            msg = '%s - %s, %s, %s' % (time, code, status, flight)
            info['prog'].append(msg)

        return info
