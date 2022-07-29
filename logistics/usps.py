from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'usps'
        self.name = 'USPS'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://m.usps.com/m/TrackConfirmAction_detail'
        )
        self.add_query(
            'get', 'html',
            'https://tools.usps.com/go/TrackConfirmAction?tRef=fullpage&tLc=2&text28777=&tLabels={}',
            params = {
                'tRef': 'fullpage',
                'tLc': '2',
                'text28777': '',
            }
        )

    def process(self, pid, year):
        self.params['tLabels'] = pid
        self.fetch(True)

        self.params['tLabels'] = pid
        self.fetch()

        info = get_info_base()
        if 'Sorry! The Track application is having technical difficulties. Please try your search again.' in self.text:
            return info

        # information
        last_step = text.root.xpath('.//div[@class="delivery_status"]//strong')[0].text_content().strip()
        #last_date = re.sub('\s\s+', ' ', text.root.xpath('.//div[@class="package-note "]/span')[0].text_content().strip().replace(' ', ' '))
        last_desc = text.root.xpath('//div[@class="status_feed"]//p[@class="important"]')[0].text_content().strip()
        expected_delivery = strip_spaces(text.root.xpath('//div[@class="expected_delivery"]')[0].text_content())

        info['info']['Status'] = last_step
        #info['info']['Updated'] = last_date
        info['info']['Message'] = expected_delivery

        # history
        history = text.root.xpath('//div[@id="trackingHistory_1"]//span')

        prev_items = []
        for span in history:
            if span.xpath('.//strong'):
                if prev_items:
                    date = prev_items[0]
                    desc = prev_items[1]
                    place = prev_items[2]
                    info['prog'].append('{} ({}) {}'.format(date,place,desc))
                    prev_items = []
            prev_items.append(strip_spaces(span.text_content()))
        if prev_items:
            date = prev_items[0]
            desc = prev_items[1]
            place = prev_items[2]
            if len(prev_items) > 3:
                desc += ', '+prev_items[3]
            info['prog'].append('{} ({}) {}'.format(date,place,desc))
            prev_items = []
        prev_items.append(span.text_content())
        info['prog'].reverse()

        return info
