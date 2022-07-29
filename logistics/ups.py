from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'ups'
        self.name = 'UPS'
        self.disabled = True

        self.add_query(
            'json', 'json',
            'https://www.ups.com/track/api/Track/GetStatus?loc=en_US',
            post = {
                'Locale': 'en_US',
            },
            params = {
                'loc': 'en_US',
            }
        )

    def process(self, pid, year):
        self.params['TrackNumber'] = pid
        self.fetch(True)

        info = get_info_base()
        detail = self.root['trackDetails'][0]
        info['Status'] = detail['packageStatus']
        if detail['scheduledDeliveryDate']:
            info['Scheduled Delivery'] = detail['scheduledDeliveryDate']
        info['Shipped Date'] = remove_pre0(detail['additionalInformation']['shippedOrBilledDate'])
        info['Service Name'] = detail['additionalInformation']['serviceInformation']['serviceName']
        info['Ship To'] = '{}, {}'.format(detail['shipToAddress']['city'].capitalize(), detail['shipToAddress']['country'])
        info['Weight'] = '{} {}'.format(detail['additionalInformation']['weight'], detail['additionalInformation']['weightUnit'])

        for prog in reversed(detail['shipmentProgressActivities']):
            if not prog['date']: continue

            date = remove_pre0(re.sub(r'/\d{4}', '', prog['date']))
            time = make_24h(prog['time'])
            location = prog['location']
            desc = prog['activityScan']

            if location:
                text = '{} {} ({}) {}'.format(date, time, location, desc)
            else:
                text = '{} {} / {}'.format(date, time, desc)
            info['prog'].append(text)

        return info
