from BaseLogistics import *
import pycountry

def get_address(addr):
    addr = addr['address']
    items = []
    if 'addressLocality' in addr:
        items.append(addr['addressLocality'])
    if 'postalCode' in addr:
        items.append(addr['postalCode'])
    if 'countryCode' in addr:
        items.append(pycountry.countries.get(alpha_2=addr['countryCode']).name)

    return ', '.join(items)

def clean_desc(desc):
    sp = desc.find('(Homepage')
    if sp >= 0:
        desc = desc[0:sp].strip()
    return desc

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'dhl'
        self.name = 'DHL'
        self.timef = '%Y-%m-%dT%H:%M:%S'

        self.config = tracker.config.get('dhl',None)

        self.add_query(
            'get', 'json',
            'https://api-eu.dhl.com/track/shipments'
        )

        # source: https://developer.dhl.com/sites/default/files/2022-07/dpdhl_tracking-unified_1.3.2.yaml
        self.service = {
            'dgf':       'DHL Global Forwarding',  # DGF Global Forwarding
            'sameday':   'DGF SameDay',            # DGF SameDay
            'dsc':       'DHL Supply Chain',       # DSC (Connected View)
            'express':   'DHL Express',            # Express (XMLPI-ITS)
            'freight':   'DHL Freight',            # Freight (Active Tracing)
            'ecommerce': 'DHL eCS (US)',           # eCS (Americas/WebTrack)
            'ecommerce-apac': 'DHL eCS(APAC)',
            'ecommerce-europe': 'DHL eCS(EU)',
            'parcel-de': 'DHL eCS (DE)',           # eCS DE (Parcel DE/NOLP)
            'parcel-nl': 'DHL eCS (NL)',           # eCS NL (Parcel BNL/PDS)
            'parcel-pl': 'DHL eCS (PL)',           # eCS PL (Parcel PL/TNT)
            'parcel-uk': 'DHL eCS (UK)',           # eCS UK (Parcel UK)
            'post-de':   'Deutsche Post',          # Post Germany (Track Trace Brief)
        }
        self.status_code = {
            'pre-transit': '배송준비',
            'transit':     '배송중',
            'delivered':   '완료',
            'failure':     '실패',
            'unknown':     '확인안됨',
        }

    def process(self, trackNo, year):
        info = get_info_base(self.code, trackNo)
        if not self.config:
            print('https://developer.dhl/ 에서 발급받은 키를 config.yaml에 적어주세요.')
            return info

        self.headers['DHL-API-Key'] = self.config['key']
        self.params['trackingNumber'] = trackNo
        self.fetch(True)

        if 'shipments' in self.root and len(self.root['shipments']) == 1:
            ship = self.root['shipments'][0]
            info['info']['서비스'] = self.service.get(ship['service'], ship['service'])
            info['info']['제품'] = ship['details']['product']['productName']
            info['info']['출발지'] = get_address(ship['origin'])
            info['info']['도착지'] = get_address(ship['destination'])
            info['info']['무게'] = '{value} {unitText}'.format(**ship['details']['weight'])
            info['info']['현위치'] = get_address(ship['status']['location'])
            info['info']['상태'] = self.status_code.get(ship['status']['statusCode'], ship['status']['statusCode'])
            info['info']['시간'] = self.parse_time(ship['status']['timestamp'])
            if 'estimatedTimeOfDelivery' in ship:
                info['info']['예상배송일'] = self.parse_time(ship['estimatedTimeOfDelivery'])
            elif 'estimatedDeliveryTimeFrame' in ship:
                timeframe = ship['estimatedDeliveryTimeFrame']
                info['info']['예상배송일'] = '{} - {}'.format(self.parse_time(timeframe['estimatedFrom']).strftime('%m/%d %H:%M'), self.parse_time(timeframe['estimatedThrough']).strftime('%m/%d %H:%M'))
            if 'estimatedTimeOfDeliveryRemark' in ship:
                info['info']['배송안내'] = ship['estimatedTimeOfDeliveryRemark']
            info['info']['배달증명'] = '있음' if ship['details']['proofOfDeliverySignedAvailable'] else '없음'

            for event in reversed(ship['events']):
                if 'location' in event:
                    info['prog'].append(ProgV1(self.parse_time(event['timestamp']), get_address(event['location']), event['statusCode'], clean_desc(event['description'])))
                else:
                    info['prog'].append(ProgV5(self.parse_time(event['timestamp']), event['statusCode'], clean_desc(event['description'])))

        return info
