"""
Let's do some playing with the FAA dTPPs...
https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dtpp/
"""
import untangle
import requests


__all__ = ['ParsedTPP']


record_fields = [
    'chartseq',
    'chart_code',
    'chart_name',
    'useraction',
    'pdf_name',
    'cn_flg',
    # 'cnsection', Some special stuff is needed for this. Do later.
    'cnpage',
    # 'bvsection', # Same as above. Special handling required.
    'bvpage',
    'procuid',
    'two_colored',
    'civil',
    'faanfd15',
    'faanfd18',
    'copter'
]


def get_crnt_aeronav():
    """
    Determine the location of the current d-TPP aeronav data
    :return:
    """
    # https://app.swaggerhub.com/apis/FAA/APRA/1.2.0
    base_aeronav = 'https://aeronav.faa.gov/d-tpp/'
    edition_api_url = 'https://soa.smext.faa.gov/apra/dtpp/info?edition=current&geoname=US'
    headers = {
        'accept': 'application/json',  # JSON, please...
    }
    r = requests.get(url=edition_api_url, headers=headers)
    eyear = r.json()['edition'][0]['editionDate'][-2:]  # Get the last two, because that's what we need
    enmbr = r.json()['edition'][0]['editionNumber']

    if enmbr < 10:
        enmbr = '0' + str(enmbr)
    else:
        enmbr = str(enmbr)

    return base_aeronav + eyear + enmbr + '/'


class ParsedTPP:
    def __init__(self):
        """
        Initialize
        :return:
        """
        self.apt_dict = {}  # Placeholder
        self.anav_base = get_crnt_aeronav()
        meta_url = self.anav_base + 'xml_data/d-TPP_Metafile.xml'
        self.parsed_tpp = untangle.parse(meta_url)
        self.to_dict()

    def return_parsed(self):
        """
        Just return the raw parsed file object. Nothing fancy.
        :return:
        """
        return self.parsed_tpp

    def return_dict(self):
        """
        Return the dictionary.
        :return:
        """
        return self.apt_dict

    def to_dict(self):
        """
        Make an actual dict, or something
        :return:
        """
        for state in self.parsed_tpp.digital_tpp.state_code:
            for city in state.city_name:
                if isinstance(city.airport_name, list):
                    airports = city.airport_name
                else:  # Single Airport
                    airports = [city.airport_name]

                for airport in airports:
                    self.apt_dict[airport['apt_ident']] = {
                        'location': {
                            'state_code': state['ID'],
                            'state_name': state['state_fullname'],
                            'city': city['ID'],
                        },
                        'volume': city['volume'],
                        'military': airport['military'],
                        'faa_ident': airport['apt_ident'],
                        'icao_ident': airport['icao_ident'],
                        'records': [],
                    }
                    current_airport = self.apt_dict[airport['apt_ident']]

                    if isinstance(airport.record, list):
                        records = airport.record
                    else:  # Single Record
                        records = [airport.record]

                    for record in records:
                        record_dict = {}
                        for field in record_fields:
                            record_dict[field] = getattr(record, field).cdata

                        current_airport['records'].append(record_dict)
