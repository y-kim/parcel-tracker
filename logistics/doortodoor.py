from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'doortodoor'
        self.name = '대한통운'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'http://ex.korex.co.kr:7004/fis20/KIL_HttpCallExpTrackingInbound_Ctr.do'
        )
        self.add_query(
            'get', 'html',
            'http://www.doortodoor.co.kr/tracking/jsp/cmn/Tracking_new.jsp',
            params = {
                'QueryType': 4
            }
        )

    def process(self, pid, year):
        self.params['rqs_HAWB_NO'] = pid
        self.fetch(True)

        info = get_info_base()
        info['info']['HBL'] = str(pid);

        if not 'HBL NO. NONEXISTENT' in self.text and not "We didn't find any matches for" in self.text:
            general_information = self.root.xpath('//table')[0]
            oversea_delivery_status = self.root.xpath('//table')[2]

            # general information
            gen_th = general_information.xpath('.//th')
            gen_td = general_information.xpath('.//td')

            if len(gen_th) != len(gen_td):
                raise Exception('Lengh of general item head %d and data %d mismatch' % (len(gen_th), len(gen_td)))

            for i in range(len(gen_th)):
                if type(gen_td[i].text) is str and len(gen_td[i].text.strip()) > 0:
                    info['info'][gen_th[i].text.strip()] = gen_td[i].text.strip()

            oversea_trs = oversea_delivery_status.xpath('.//tr')
            del oversea_trs[0]
            for oversea_tr in oversea_trs:
                message = re.sub(r'^.+?\((.+?)\)$', r'\1', oversea_tr.xpath('.//td')[0].text_content().strip())
                time = oversea_tr.xpath('.//td')[1].text_content().strip()
                if type(time) is str and len(time) > 0:
                    info['prog'].append('%s %s - %s' % (time[5:10], time[11:], message))

        self.params['pTdNo'] = pid
        if not info_added and not '시스템 점검' in self.text:
            info_table = self.root.xpath('//table')[0]
            ths = info_table.xpath('.//th')
            tds = info_table.xpath('.//td')

            for i in range(0,len(ths)):
                index = ths[i].text_content().strip()
                text  = tds[i].text_content().strip()
                if index == '운송장번호' and text == '':
                    break
                if len(index) > 0:
                    while index in info['info']:
                        index += '*'
                    info['info'][index] = text

        if ('검색된 결과값이 없습니다' not in self.text) and ('시스템 점검' not in self.text):
            trs = self.root.xpath('//tbody')[1].xpath('.//tr')
            for tr in trs:
                tds = tr.xpath('.//td')
                time = tds[3].text[5:-3]
                pla  = tds[0].text_content()
                msg  = tds[2].text.strip()
                add  = '' #tds[8].text.strip()
                if msg in ['사고', '배달출발'] and len(add) > 0:
                    desc = '%s %s - %s (%s)' % (time, pla, msg, add)
                else:
                    desc = '%s %s - %s' % (time, pla, msg)
                info['prog2'].append(desc)

        return info
