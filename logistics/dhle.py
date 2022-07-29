from BaseLogistics import *

class Logistics(BaseLogistics):
    def __init__(self, tracker):
        super(Logistics, self).__init__(tracker)
        self.code = 'dhle'
        self.name = 'DHL eCommerce'
        self.disabled = True

        self.add_query(
            'get', 'html',
            'https://consignee.ecmsglobal.com/brige/showtracking',
            'https://ecommerceportal.dhl.com/track/'
        )

    def process(self, pid, year):
        self.params['trackNo'] = pid
        self.fetch(True)

        info = get_info_base()
        if 'To serve you better, the DHL eCommerce Portal will be upgraded during our maintenance' in self.text:
            return info

        info['info']['Status'] = self.root.xpath('//label[contains(@class, "TrackStatus")]')[0].text_content()
        info['info']['Time'], info['info']['Place'] = (strip_spaces(x.text_content()) for x in self.root.xpath('//label[contains(@class, "TrackTimeAndDate")]'))
        locations = [strip_spaces(x.text_content()) for x in self.root.xpath('//label[contains(@class, "TrackingFromData")]')]
        info['info']['From'] = '{}, {}'.format(locations[0], locations[1])
        info['info']['To'] = '{}, {}'.format(locations[2], locations[3])

        lis = self.root.xpath('//ol[@class="timeline-delivered"]/li')
        for li in lis:
            if li.get('class') == 'timeline-spine': pass
            elif li.get('class') == 'timeline-start': pass
            elif li.get('class') == 'timelineDate':
                date = li.xpath('.//label')[0].text_content()
                date = re.sub(' \d{4}', '', date)
            elif li.get('class') == 'Timeline-event':
                time = strip_spaces(li.xpath('.//span[@class="timelineTime"]')[0].text_content())
                times = time.split()
                hour, minute = (int(x) for x in times[0].split(':'))
                if times[1] == 'PM':
                    hour += 12
                time = '{:02d}:{:02d} {}'.format(hour, minute, times[2])
                location = strip_spaces(li.xpath('.//div[@class="timeline-location"]//label')[0].text_content())
                desc = strip_spaces(li.xpath('.//div[@class="timeline-description"]//label')[0].text_content())

                text = '{} {} ({}) {}'.format(date, time, location, desc)
                info['prog'].append(text)
        info['prog'].reverse()

        return info
