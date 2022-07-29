from BaseLogistics import *

def hanjin_time_to_stc(date, time):
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = int(time[0:2])

    if hour < 12:
        apm = '오전'
    else:
        hour -= 12
        apm = '오후'

    if hour == 0:
        hour = 12

    return '%s년 %s월 %s일 %s %02d시' % (year, month, day, apm, hour)

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'hanjin'
        self.name = '한진택배'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'http://www.hanjin.co.kr/Delivery_html/inquiry/result_waybill.jsp'
        )

    def process(self, pid, year):
        self.params['wbl_num'] = pid
        self.fetch(True)

        info = get_info_base()
        if not 'result_error.jsp' in self.text:
            ths = self.root.xpath('//thead')[0].xpath('./tr')[0].xpath('./th')
            index = 0
            head_map = {}
            for header in ths:
                alt = re.sub('\s+', ' ', header.text_content()).strip(); #header.xpath('./img')[0].get('alt')
                head_map[index] = alt
                index += int(header.get('colspan', 1))
            head_map[index-1] = '주소'

            data_info, data_prgs = self.root.xpath('//tbody')
            items = data_info.xpath('.//td')
            i = 0
            for item in items:
                if head_map.get(i, '') == '운송장정보/ 항공사 · 선사 운송장번호':
                    hbl = item.xpath('.//strong')[0].text
                    mbl = item.text_content().replace(hbl, '').strip()

                    hbl = re.sub(r'\s+', '', hbl)
                    mbl = re.sub(r'\s+', '', mbl)
                    if len(hbl) > 0:
                        info['info']['HBL'] = hbl
                    info['info']['MBL'] = mbl
                elif i in head_map:
                    var = re.sub(r'\s+', ' ', item.text_content().strip())
                    if head_map[i] == '운송장정보':
                        info['info']['HBL'] = var.replace(' ','').replace('-','')
                    else:
                        info['info'][head_map[i]] = var
                i += 1

            items = data_prgs.xpath('.//tr')
            for item in items:
                sub_items = item.xpath('.//td')
                if len(sub_items) >= 4:
                    date = sub_items[0].text_content() #.replace('-', '/')
                    time = sub_items[1].text_content()
                    time_str = hanjin_time_to_stc(date, time)

                    location = re.sub(r'\s+', ' ', sub_items[2].text)
                    loc_map = {
                            'Heathrow AIRPORT터미널': 'LHR',
                            'Incheon Intl Airport터미널': 'ICN',
                    }
                    location = loc_map.get(location, location)

                    text = sub_items[3].text_content()
                    text = re.sub(r'\s+', ' ', text).strip()
                    text = re.sub(r'\.[0-9 ,-]+', '.', text)
                    HJ_REP = (
                        (location+'영업소로', ''),
                        (location+'영업소에서', ''),
                        (location+'공항터미널에서', ''),
                        (location+'물류터미널에서', ''),
                        (location+'에서', ''),
                        (location+'에', ''),
                        ('고객님 상품을', ''),
                        ('상품이', ''),
                        ('상품', ''),
                        ('하였습니다.', ''),
                        ('되었습니다.', ''),
                        ('진행중입니다.', '진행중'),
                        ('고객님 화물에 대해', ''),
                        ('집하하여  입고', '집하 & 입고'),
                        ('입고 중에 있습니다.', '입고 중'),
                        ('국내배송 예정입니다.', ''),
                        ('출고 대기 중입니다.', '출고 대기'),
                        ('출고되어 국내 배송지로 출발', '출고'),
                        ('항공으로', '항공: '),
                        ('출항 예정입니다.', '출항 예정'),
                        ('으로 이동중 입니다.', ': 이동중'),
                        ('로 이동중 입니다.', ': 이동중'),
                        ('배송원이 배송준비중 입니다.', '배송준비중'),
                        ('수입신고 중 입니다.', '수입신고중'),
                        ('관부가세 납부 대기 중입니다.', '관부가세 납부 대기 중'),
                        ('수입통관이 완료되어', '수입통관 완료'),
                        ('수입통관장에 반입', '수입통관장 반입'),
                        ('운송장 정보가 등록', '운송장 정보 등록'),
                    )
                    for rep in HJ_REP:
                        text = text.replace(*rep)
                    text = re.sub(r'\s+', ' ', text)
                    text = text.replace('<strong>','')
                    text = text.replace('</strong>','')
                    text = text.strip()

                    date = date[5:].replace('-','/').replace('/0','/')
                    date = date[1:] if date[0] == '0' else date

                    desc = '%s %s (%s) - %s' % (date, time, location, text)
                    info['prog'].append(desc)
            info['prog'] = natsorted(info['prog'])

        return info
