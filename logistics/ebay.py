from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'ebay'
        self.name = 'eBay'
        self.disabled = True

        self.add_query(
            'get', 'json',
            'https://parceltracking.pb.com/ptsapi/track-packages/{}'
        )

    @staticmethod
    def ebay_location(loc):
        items = []

        targets = ('city', 'countyOrRegion', 'country')
        for target in targets:
            if loc.get(target, None):
                items.append(loc[target])
        if len(items) == 0:
            return ''
        else:
            return ', '.join(items)

    @staticmethod
    def ebay_message(desc, comment):
        if not desc:
            return comment
        if not comment:
            return desc

        if desc in ('In Transit', 'Tracking Details Uploaded'):
            return comment
        if comment in ('DELIVERED', ):
            return desc

    def process(self, pid, year):
        self.urls[0] = self.urls[0].format(pid)
        self.fetch(True)

        info = get_info_base()
        info['info']['주문번호'] = self.root['orderId']
        info['info']['파트너 번호'] = self.root['partnerCode']
        info['info']['서비스 종류'] = self.root['service']
        info['info']['중량'] = '{} {}'.format(self.root['weight'], self.root['weightUnit'])
        info['info']['발송지'] = self.ebay_location(self.root['senderLocation'])
        info['info']['목적지'] = self.ebay_location(self.root['destinationLocation'])
        status = self.root['currentStatus']
        #info['info']['상태'] = self.ebay_message(status.get('eventDescription', None), status.get('generalComment', None))
        #info['info']['운송업자'] = status['authorizedAgent']
        for key, var in status.items():
            if key in ('eventDate', 'eventTime', 'eventLocation'):
                continue
            if var:
                info['info'][key] = var
        info['info']['시간'] = '{} {}'.format(status['eventDate'], ebay_simple_time(status['eventTime']))
        info['info']['위치'] = self.ebay_location(status['eventLocation'])

        self.root['scanHistory']['scanDetails'].insert(0, status)
        for history in reversed(self.root['scanHistory']['scanDetails']):
            info['prog'].append('{} {} ({})\n  {}'.format(
                history['eventDate'], ebay_simple_time(history['eventTime']),
                self.ebay_location(history['eventLocation']),
                self.ebay_message(history.get('eventDescription', None), history.get('generalComment', None))))

        return info
