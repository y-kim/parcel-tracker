from BaseLogistics import *
import html

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'unipass'
        self.name = '대한민국 통관'

        # other options
        self.timef = '%Y%m%d%H%M%S'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'

        # fetch 0: get session information
        self.add_query(
            'post', 'html',
            'https://unipass.customs.go.kr/csp/myc/mainmt/MainMtCtr/menuExec.do',
            post = {
                'selectedId': 'MYC_MNU_00000450',
                'mblNo': '',
            }
        )
        # fetch 1: retrieve cargMtNo
        self.add_query(
            'post', 'json',
            'https://unipass.customs.go.kr/csp/myc/bsopspptinfo/cscllgstinfo/ImpCargPrgsInfoMtCtr/retrieveImpCargPrgsInfoLst.do',
            post = {
                'firstIndex': '0',
                'page': '1',
                'pageIndex': '1',
                'pageSize': '20',
                'pageUnit': '20',
                'recordCountPerPage': '20',
                'qryTp': '2',
                'cargMtNo': '',
                'mblNo': '',
            }
        )
        self.add_query('post', 'json',
            'https://unipass.customs.go.kr/csp/myc/bsopspptinfo/cscllgstinfo/ImpCargPrgsInfoMtCtr/retrieveImpCargPrgsInfoDtl.do',
            post = {
                'firstIndex': '0',
                'recordCountPerPage': '20',
                'page': '1',
                'pageIndex': '1',
                'pageSize': '20',
                'pageUnit': '20',
            }
        )

        self.uniitems = {
            'cargMtNo': ['화물관리번호', True, 1],
            'prgsStts': ['진행상태', True, 2],
            'shcoFlcoSgn': ['선사/항공사', True, 3],
            'mblNo': ['MBL 번호', True, 4],
            'hblNo': ['HBL 번호', True, 5],
            'cargTpcd': ['화물구분', True, 6],
            'sanm': ['선박/항공편명', True, 7],
            'csclPrgsStts': ['통관진행상태', True, 8],
            'prcsDttm': ['처리일시', True, 9],
            'shipCntyCdNm': ['선박국적', True, 10],
            'shipAgncNm': ['선박대리점', True, 11],
            'prnm': ['품명', True, 12],
            'loadPortAirptCd': ['적재항', True, 13],
            'cmdtGcnt': ['포장갯수', True, 14],
            'cmdtWght': ['총 중량', True, 15],
            'unldPortAirptCd': ['양륙항', True, 16],
            'etprCstmSgn': ['입항세관', True, 17],
            'cargMsrm': ['용적', True, 18],
            'blPcdNm': ['B/L유형', True, 19],
            'etprDt': ['입항일', True, 20],
            'vydfNo': ['항차', True, 21],
            'mtTrgtCargYnNm': ['관리대상지정여부', True, 22],
            'cntrGcnt': ['컨테이너개수', True, 23],
            'rlseDtyPridPassTpcd': ['반출의무과태료', True, 24],
            'dclrDelyAdtxYn': ['신고지연가산세', True, 25],
            'spcnCargCd': ['특수화물코드', True, 26],
            'cntrNo': ['컨테이너번호', True, 27],

            'prcsStcd': ['처리단계', True, -1],
            'cnsiAddr': ['주소', True, -1],
            'cnsiNm': ['이름', True, -1],
            'cnsiTelno': ['전화번호', True, -1],
            'snarKoreNm': ['장치장명', True, -1],
            'entsKoreNm': ['화물운송주선업자명', True, -1],
            'seaFlghTpcd': ['선박/항공구분', True -1],

            'blPcd': ['', False, -1], # B/L유형코드로 확인
            'cargTpcdCd': ['', False, -1],
            'cargTpcdEn': ['', False, -1],
            'prgsSttsEn': ['', False, -1],
            'shipCntyCd': ['', False, -1],
            'shipCntyCdEngNm': ['', False, -1],
            'ldpr': ['', False, -1],
            'frwrSgn': ['', False, -1],
            'pckGcnt': ['', False, -1],
            'ttwg': ['', False, -1],
            'pckKcd': ['', False, -1],
            'kg': ['', False, -1],
            'cargTrcnRelaBsopTpcd': ['', False, -1],
            'unldPortAirptNm': ['양륙항', False, -1],
            'totCnt': ['', False, -1],
            'trcoNm': ['', False, -1],

            # 검색 관련 항목들
            'firstIndex': ['', False, -1],
            'page': ['', False, -1],
            'pageIndex': ['', False, -1],
            'pageSize': ['', False, -1],
            'pageUnit': ['', False, -1],
            'lastIndex': ['', False, -1],
            'recordCountPerPage': ['', False, -1],
            'rows': ['', False, -1],
        }

        self.uld_code = {
            'AWP': '생물이 죽었음',
            'BKI': '포장단위내 물품파손',
            'BRK': '포장파손',
            'CND': '컨테이너 번호 다름',
            'CNN': '컨테이너 번호 없음',
            'CSL': '세관봉인대부착',
            'ETC': '기타',
            'IND': '품명상이',
            'MFN': '화물은 있으나 적하목록없음',
            'MGN': '적하목록은 있으나 화물없음',
            'OKY': '이상없음',
            'OVR': '포장갯수 과다',
            'OVW': '중량 초과',
            'PER': '부패',
            'SHT': '포장갯수 부족',
            'SHW': '중량 부족',
            'SLN': '봉인번호 다름',
            'SLW': '봉인번호 파손',
            'WET': '비에 젖음',
        }

    def process(self, trackno, year):
        # preparing
        self.post['hblNo'] = trackno
        self.post['blYy'] = year
        self.fetch(True)

        for node in self.root.xpath('//div[@id="MYC0405101Q_tab1"]/form/input[@class="savedtoken"]'):
            self.params[node.get('name')] = node.get('value')

        # process
        self.post['hblNo'] = trackno
        self.post['blYy'] = year
        self.fetch()

        info = get_info_base(self.code, trackno)
        if self.root['count'] == 1:
            info_raw = self.root['resultList'][0].copy()
            self.post['cargMtNo'] = info_raw['cargMtNo']
            self.fetch()
            info_raw.update(self.root['resultListM'])

            for key in sorted(info_raw):
                var = info_raw[key]
                if var is None or var == '':
                    continue
                var = html.unescape(str(var))
                if key in ('prcsDttm', ):
                    var = var #datetime_to_str(var)
                if key in self.uniitems:
                    if self.uniitems[key][1]:
                        info['info'][self.uniitems[key][0]] = var
                else:
                    info['info'][key] = var

            for item in reversed(self.root['resultListL']):
                desc = html.unescape(item['cargTrcnRelaBsopTpcd'])
                if desc == '하기결과 보고':
                    desc = '{} ({})'.format(desc, self.uld_code.get(item['rlbrBssNo'], item['rlbrBssNo']))
                info['prog'].append(ProgV2(self.parse_time(item['prcsDttm']), desc))

        return info
