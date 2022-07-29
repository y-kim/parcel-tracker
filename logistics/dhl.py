from BaseLogistics import *

def dhl_date_to_short(date):
    return short_month_name(date.split(', ')[1])

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'dhl'
        self.name = 'DHL'
        self.disabled = True

        self.add_query(
            'get', 'json',
            'http://www.dhl.com/shipmentTracking',
            params = {
                'countryCode': 'g0',
                'languageCode': 'en',
            }
        )

    def process(self, pid, year):
        self.params['AWB'] = pid
        self.fetch(True)

        info = get_info_base()
        dict_data = slef.root['results'][0]
        info['info'][dict_data['label']] = dict_data['id']
        info['info']['항선구분'] = dict_data['type']
        info['info']['Origin'] = dict_data['origin']['value']
        info['info']['Destination'] = dict_data['destination']['value']
        info['info']['현상황'] = dict_data['description'].replace(' - KOREA, REPUBLIC OF (SOUTH K.)', '').replace(' OUTSKIRT OF SEOUL', '')
        if 'edd' in dict_data:
            if 'date' in dict_data['edd']:
                info['info']['도착예정'] = '%s, %s' % (dhl_date_to_short(dict_data['edd']['date']), dict_data['edd']['product'])
            else:
                info['info']['도착예정'] = '%s' % (dict_data['edd']['product'])

        info['info']['수량'] = str(dict_data['pieces']['value'])

        for checkpoint in reversed(dict_data['checkpoints']):
            desc = '%s %s %s - %s' % (dhl_date_to_short(checkpoint['date']),
                                      checkpoint['time'],
                                      checkpoint['location'].replace(' - ', ', ').replace(', KOREA, REPUBLIC OF (SOUTH K.)', '').replace(' OUTSKIRT OF SEOUL', ''),
                                      checkpoint['description'].replace(checkpoint['location'], '').strip())
            info['prog'].append(desc)
        info['prog'] = natsorted(info['prog'])


        return info
