from BaseLogistics import *
import html

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'unipass-ems'
        self.name = '대한민국 우편물 통관'

        # other options
        self.timef = '%Y%m%d%H%M%S'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'

        # fetch 0: get session information
        self.add_query(
            'post', 'json',
            'https://unipass.customs.go.kr/csp/myc/bsopspptinfo/csclinfo/PsmtCsclInfoQryCtr/retrievePsmtCsclRslt.do',
            post = {
                'psmtKcd': '',
                'psmtCsclMtNo': '',
            }
        )
        ## fetch 1: retrieve cargMtNo
        #self.add_query(
        #    'post', 'html',
        #    'https://unipass.customs.go.kr/csp/myc/trifadmndclr/spcncscl/retrieveIntnPsmtCsclApfm.do'
        #)

        self.ignores = ['firstIndex', 'lastIndex', 'pageIndex', 'pageSize', 'pageUnit', 'recordCountPerPage', 'page', 'rows', 'totCnt', 'sendCntyCd', 'ttwgUtCd', 'postCurrCd']
        self.trs_ko = {
            'psmtCsclMtNo': '통관관리번호',
            'psmtNo': '우편물번호',
            'psmtPrcsTpcd': '처리구분',
            'csclPsofCd': '우체국명',
            'psmtKcd': '항공소포',
            'brngArvlDt': '반입일자',
            'sendCntyCdNm': '발송국가',
            'rcivrNm': '수취인명',
            'postCrge': '우편요금',
            'postCurrCd': '우편통화코드',
            'ttwg': '총중량',
            'ttwgUtCd': '총중량 단위',
            'aprvDt': '통관일자',
            'adupTxTrgtTpcd': '합산과세여부',
            'txPrcWncrTamt': '총과세가격',
            'tamt': '세액',
            'homeDelivery': '통관절차대행수수료',
            'alSum': '합계',
            'psmtPrcsStcd': '처리상태',
        }


    def process(self, trackno, year):
        # preparing
        self.post['psmtNo'] = trackno
        self.fetch(True)

        info = get_info_base(self.code, trackno)
        if self.root['resultDtl']:
            items = self.root['resultDtl']
            for key, var in items.items():
                if key not in self.ignores:
                    name = self.trs_ko.get(key, key)
                    if key == 'ttwg':
                        var = '{} {}'.format(var, items['ttwgUtCd'])
                    elif key == 'tamt' and var == 0:
                        var = '심사중'
                    elif key == 'alSum' and items['tamt'] == 0:
                        var = '심사중'
                    elif key in ('tamt', 'alSum', 'homeDelivery'):
                        var = '{}원'.format(var)
                    elif key == 'postCrge' and var and items['postCurrCd']:
                        var = '{} {}'.format(items['postCurrCd'], var)

                    if var:
                        info['info'][name] = var

        return info
