from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'els'
        self.name = 'ELS'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'http://www.xiuglobal.com/search/trace_view.asp?hawb_no=%s'
        )

    def process(self, pid, year):
        self.params['hawb_no'] = pid
        self.fetch(True)

        info = get_info_base()

        tables = self.root.xpath('//table')
        # info
        trs = tables[0].xpath('.//tr')
        for tr in trs:
            tds = tr.xpath('.//td')
            info['info'][tds[0].text_content().strip()] = tds[1].text_content().strip()

        # progress
        trs = tables[1].xpath('.//tr')
        trs.pop(0)
        for tr in trs:
            tds = tr.xpath('.//td')
            date = tds[0].text_content().strip()
            time = tds[1].text_content().strip()
            loc  = tds[2].text_content().strip()
            stat = tds[3].text_content().strip()
            note = tds[4].text_content().strip()

            info['prog'].append('%s %s (%s) - %s [%s]' % (date, time, loc, stat, note))

        return info
