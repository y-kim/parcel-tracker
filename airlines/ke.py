from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'ke'
        self.name = '대한항공'
        self.mbls = ('180',)
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://cargo.koreanair.com/en/tracking'
        )
        self.add_query(
            'post', 'json',
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
            'pieces': '수량',
            'routes': '경로',
            'shipmentStatus': '현재 상태',
            'commodityDetail': {
                'shipmentDesc': '상품 종류'
            },
            'product': '상품',
            'sccList': 'SCC',
            'wgtDetail': '중량',
            'weight': '중량',
            'bookingStatus': '예약상황',
            'operationStatus': '운행상황',
            'fltSegNo': '항공기 번호',
            'routeNo': '루트 번호',
            'depDate': '출발일자',
            'ownerId': '고객번호',
        }

    def process(self, pid, year):
        self.params['awbNO'] = pid
        self.fetch(True)

        info = get_info_base()

        json_data = self.root.xpath('//script[@type="application/json"]')[0].text_content()
        dict_data = json.loads(json_data, object_pairs_hook=OrderedDict)

        self.post = {
            'generalInfo': {
                'lang': 'EN',
                'sessionId': dict_data['session_id'],
                'time': datetime.now().strftime('%d %b %Y %H:%M'),
                'txnId': 'iyixb7ax7{}'.format(int(datetime.now().timestamp()*1000)),
            },
            'payLoad': [{
                'awbDocNo': id_post,
                'awbPrefix': id_pre,
            }],
        }
        self.fetch()

        for key, var in self.root['payLoad'][0].items():
            if key in filt:
                if type(var) is str:
                    info['info'][filt[key]] = var
                elif type(var) is int:
                    info['info'][filt[key]] = str(var)
                elif key == 'wgtDetail':
                    unit = {'K': 'kg'}
                    info['info'][filt[key]] = '{} {}'.format(var['quantity'], unit[var['unit']])
                elif type(var) is list:
                    info['info'][filt[key]] = ', '.join(var)
                else:
                    if key == 'commodityDetail':
                        info['info'][filt[key]['shipmentDesc']] = var['shipmentDesc']

        i = 0
        for flts in self.root['payLoad'][0]['fltDetails']:
            i+=1

            info['info']['항공기{}'.format(i)] = '{}{}'.format(flts['fltDetail']['carCode'],flts['fltDetail']['fltNo'])
            info['info']['항공기{} - 형식'.format(i)] = '{} {}'.format(flts['fltDetail']['fltType'], flts['fltDetail']['aircraftType'])
            for key, var in flts.items():
                if key in filt:
                    if type(var) is str:
                        info['info']['항공기{} - {}'.format(i, filt[key])] = var


        for events in reversed(self.root['payLoad'][0]['eventDetails']):
            flt = ''
            if 'fltDetail' in events:
                if 'fltNo' in events['fltDetail']:
                    flt = '{}{}, '.format(events['fltDetail']['carCode'],events['fltDetail']['fltNo'])
                else:
                    flt = '{}, '.format(events['fltDetail']['carCode'])
            desc = '{} ({}) - {}{}'.format(re.sub('\d{4} ', '', events['eventDate']), events['arpCode'], flt, events['eventDesc'])
            info['prog'].append(desc)

        return info
