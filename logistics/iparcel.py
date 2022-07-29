from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'iparcel'
        self.name = 'i-parcel'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://tracking.i-parcel.com/'
        )

    def process(self, pid, year):
        self.params['TrackingNumber'] = pid
        self.fetch(True)

        info = get_info_base()
        events = self.root.xpath('//div[@class="row result"]')

        for event in reversed(events):
            currdatetime = event.xpath('.//div[contains(@class, "date")]')[0]
            desc = event.xpath('.//div[contains(@class, "event")]')[1]

            date = currdatetime.xpath('.//strong')[0].text.strip()
            time = currdatetime.xpath('.//span')[0].text_content().replace(date, '')
            message_city = desc.xpath('.//span')
            message = message_city[0].text.strip()

            if len(message_city) == 2:
                city = message_city[1].text.strip()
                full_message = '%s %s (%s) - %s' % (date, time, city, message)
            else:
                full_message = '%s %s - %s' % (date, time, message)
            info['prog'].append(full_message)

        return info
