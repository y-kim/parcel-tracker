from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'airline-ke'
        self.name = '대한항공'
        self.prefixes = ('180',)

        self.timef = '%d %b %Y %H:%M'

        self.add_query(
            'get', 'html',
            'https://cargo.koreanair.com/en/tracking'
        )
        self.add_query(
            'json', 'json',
            'https://cargo.koreanair.com/cargoportal/services/trackawb',
            post = {
                'userInfo': {
                    'agentCode': '',
                    'branch': '',
                    'region': 'Korea',
                    'userId': '',
                    'userType': 'GUEST'
                }
            }
        )

        self.filt = {
            'sequenceNo': '시퀀스 번호',
            'totalRecordCount': '전체 레코드 수',
            'origin': '출발지',
            'destination': '목적지',
            'routes': '경로',
            'shipmentStatus': '현재 상태',
            'commodityDetail': {
                'shipmentDesc': '상품 종류'
            },
            'product': '상품',
            'sccList': 'SCC',
            'pieces': '수량',
            'wgtDetail': '중량',
            'weight': '중량',
            'bookingStatus': '예약상황',
            'operationStatus': '운행상황',
            'fltSegNo': '항공기 번호',
            'routeNo': '루트 번호',
            'depDate': '계획출발시각',
            'estimatedDepDate': '예상출발시각',
            'actualDepDate': '실제출발시각',
            'arrvlDate': '계획도착시각',
            'estimatedArrvlDate': '예상도착시각',
            'actualArrvlDate': '실제도착시각',
            'ownerId': '고객번호',
        }

    def process(self, trackno, year):
        self.params['awbNO'] = trackno
        self.fetch(True)

        info = get_info_base(self.code, trackno)

        json_data = self.root.xpath('//script[@type="application/json"]')[0].text_content()
        dict_data = json.loads(json_data)

        self.post = {
            'generalInfo': {
                'lang': 'KO',
                'sessionId': dict_data['session_id'],
                'time': datetime.now().strftime('%d %b %Y %H:%M'),
                'txnId': 'wk3936f0x{}'.format(int(datetime.now().timestamp()*1000)),
            },
            'payLoad': [{
                'awbDocNo': trackno[3:],
                'awbPrefix': trackno[0:3],
            }],
        }
        self.fetch()

        for key, var in self.root['payLoad'][0].items():
            if key in self.filt:
                if type(var) is str:
                    info['info'][self.filt[key]] = var
                elif type(var) is int:
                    info['info'][self.filt[key]] = str(var)
                elif key == 'wgtDetail':
                    unit = {'K': 'kg'}
                    info['info'][self.filt[key]] = '{} {}'.format(var['quantity'], unit[var['unit']])
                elif type(var) is list:
                    info['info'][self.filt[key]] = ', '.join(var)
                else:
                    if key == 'commodityDetail':
                        info['info'][self.filt[key]['shipmentDesc']] = var['shipmentDesc']

        for i, flts in enumerate(self.root['payLoad'][0]['fltDetails'], 1):
            info['info']['항공기{}'.format(i)] = '{}{} ({} {})'.format(flts['fltDetail']['carCode'],flts['fltDetail']['fltNo'],flts['fltDetail']['fltType'], flts['fltDetail']['aircraftType'])
            for key, var in flts.items():
                if key in self.filt:
                    if isinstance(var, str):
                        try:
                            var = self.parse_time(var)
                        except: pass
                        info['info']['항공기{} - {}'.format(i, self.filt[key])] = var


        for events in reversed(self.root['payLoad'][0]['eventDetails']):
            flt = ''
            if 'fltDetail' in events:
                flt = '{}{}'.format(events['fltDetail']['carCode'],events['fltDetail'].get('fltNo', ''))
                info['prog'].append(ProgV4(self.parse_time(events['eventDate']), events['arpCode'], flt, events['eventDesc']))
            else:
                info['prog'].append(ProgV3(self.parse_time(events['eventDate']), events['arpCode'], events['eventDesc']))

        return info
