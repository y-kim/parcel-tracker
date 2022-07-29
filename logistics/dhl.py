from BaseLogistics import *
import pycountry

def get_address(addr):
    addr = addr['address']
    if 'addressLocality' in addr:
        return addr['addressLocality']
    elif 'countryCode' in addr:
        return pycountry.countries.get(alpha_2=addr['countryCode']).name
    else:
        return str(addr)

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

    def process(self, trackNo, year):
        info = get_info_base()
        if not self.config:
            print('https://developer.dhl/ 등록 후 키를 발급 받으세요')
            return info

        self.headers['DHL-API-Key'] = self.config['key']
        self.params['trackingNumber'] = trackNo
        self.fetch(True)

        if 'shipments' in self.root and len(self.root['shipments']) == 1:
            ship = self.root['shipments'][0]
            info['info']['서비스'] = ship['service']
            info['info']['제품'] = ship['details']['product']['productName']
            info['info']['출발지'] = get_address(ship['origin'])
            info['info']['도착지'] = get_address(ship['destination'])
            info['info']['무게'] = '{value} {unitText}'.format(**ship['details']['weight'])
            info['info']['현위치'] = get_address(ship['status']['location'])
            info['info']['상태'] = ship['status']['statusCode']
            info['info']['시간'] = datetime.strptime(ship['status']['timestamp'], self.timef)

            for event in reversed(ship['events']):
                if 'location' in event:
                    info['prog'].append(ProgV1(datetime.strptime(event['timestamp'], self.timef), get_address(event['location']), event['statusCode'], clean_desc(event['description'])))
                else:
                    info['prog'].append(ProgV5(datetime.strptime(event['timestamp'], self.timef), event['statusCode'], clean_desc(event['description'])))

        return info
