from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'post-at'
        self.name = '오스트리아 우체국'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://www.post.at/en/track_trace.php/details'
        )

    def process(self, pid, year):
        self.params['pnum1'] = pid
        self.fetch(True)

        info = get_info_base()

        if 'No data found for your inquiry.' in self.text:
            return info

        status1 = self.root.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8"]')[0]
        for span in status1.xpath('.//span'):
            for items in span.text_content().split(';'):
                key, var = (x.strip() for x in items.split(':'))
                info['info'][key] = var

        status = self.root.xpath('//h4[@class="sendungsstatus-header"]')[0].text_content().strip()
        time = self.root.xpath('//p[@class="form-control-static"]')[0].text_content().strip()

        info['info']['Status'] = status
        info['info']['Time'] = time

        progs = self.root.xpath('//ul[@class="media-list media-list-shipment"]/li')
        for prog in reversed(progs):
            time, status = (x.text_content() for x in prog.xpath('.//b')[0:2])
            time = time[len('Date: '):]
            info['prog'].append('%s - %s' % (time, status))

        return info
