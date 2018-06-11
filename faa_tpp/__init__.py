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
        self.tpp_dict = {}  # Placeholder
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
        return self.tpp_dict

    def to_dict(self):
        """
        Make an actual dict, or something
        :return:
        """
        for state in self.parsed_tpp.digital_tpp.state_code:
            self.tpp_dict[state['ID']] = {}
            current_state_dict = self.tpp_dict[state['ID']]
            current_state_dict['fullname'] = state['state_fullname']
            current_state_dict['cities'] = {}

            for city in state.city_name:
                current_state_dict['cities'][city['ID']] = {}
                current_city_dict = current_state_dict['cities'][city['ID']]
                current_city_dict['volume'] = city['volume']
                current_city_dict['airports'] = {}

                if isinstance(city.airport_name, list):
                    airports = city.airport_name
                else:  # Single Airport
                    airports = [city.airport_name]

                for airport in airports:
                    current_city_dict['airports'][airport['ID']] = {}
                    current_airport_dict = current_city_dict['airports'][airport['ID']]
                    current_airport_dict['military'] = airport['military']
                    current_airport_dict['apt_ident'] = airport['apt_ident']
                    current_airport_dict['icao_ident'] = airport['icao_ident']
                    current_airport_dict['records'] = []

                    if isinstance(airport.record, list):
                        records = airport.record
                    else:  # Single Record
                        records = [airport.record]

                    for record in records:
                        record_dict = {}
                        for field in record_fields:
                            record_dict[field] = getattr(record, field).cdata

                        current_airport_dict['records'].append(record_dict)
