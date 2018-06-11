"""
Let's do some playing with the FAA dTPPs...
https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dtpp/
"""
import untangle
import requests


__all__ = ['ParsedTPP']


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


class Airport:
    """
    I wonder what this might represent...
    """
    def __init__(
            self,
            location_data,
            volume,
            military,
            faa_ident,
            icao_ident,
            name,
    ):
        self.location_data = location_data
        self.volume = volume
        self.military = military
        self.faa_ident = faa_ident
        self.icao_ident = icao_ident
        self.name = name

        self.records = []

    def get_record(self, cindex=None):
        """
        Return a particular record
        :param cindex: The specific index if known
        :return:
        """
        if cindex is None:
            print('Available Charts: ')
            for i, v in enumerate(self.records):
                print('\t[' + str(i) + '] (' + v.chart_code + ') ' + v.chart_name)
            cindex = int(input('Choice: '))

        return self.records[cindex]


class AirportRecord:
    """
    Represents an airport record
    """
    def __init__(self, anav_base, record_data):
        record_properties = [
            'chartseq',
            'chart_code',
            'chart_name',
            'useraction',
            'pdf_name',
            'cn_flg',
            'cnsection',  # Some special stuff is needed for this. Do later.
            'cnpage',
            'bvsection', # Same as above. Special handling required.
            'bvpage',
            'procuid',
            'two_colored',
            'civil',
            'faanfd15',
            'faanfd18',
            'copter'
        ]
        for field in record_properties:
            setattr(
                self,
                field,
                getattr(record_data, field).cdata
            )
        self.pdf_url = anav_base + self.pdf_name

    def get_pdf(self):
        """
        Gets the PDF data of the record
        :return:
        """
        r = requests.get(self.pdf_url)
        return r.content


class ParsedTPP:
    def __init__(self):
        """
        Initialize
        :return:
        """
        self.anav_base = get_crnt_aeronav()
        self.parsed_tpp = self._parse_current_meta()
        self.apt_dict = self._to_dict()
        self.state_dict = self._state_dict()  # Airports by state

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

    def return_state_airports(self, state_code=None):
        """
        Return airports for a given state
        :return:
        """
        if state_code is None:
            print('States: ')
            for sc in sorted(self.state_dict.keys()):
                print('\t[' + sc + '] ' + self.state_dict[sc]['state_name'])
            state_code = input('Choice: ')

        state_code = state_code.upper()
        return self.state_dict[state_code]['airports']

    def _to_dict(self):
        """
        Convert the parsed XML into a dictionary we can use
        :return:
        """
        apt_dict = {}
        for state in self.parsed_tpp.digital_tpp.state_code:
            for city in state.city_name:
                if isinstance(city.airport_name, list):
                    airports = city.airport_name
                else:  # Single Airport
                    airports = [city.airport_name]

                for airport in airports:
                    apt_data = {
                        'location_data': {
                            'state_code': state['ID'],
                            'state_name': state['state_fullname'],
                            'city': city['ID'],
                        },
                        'volume': city['volume'],
                        'military': airport['military'],
                        'faa_ident': airport['apt_ident'],
                        'icao_ident': airport['icao_ident'],
                        'name': airport['ID']
                    }
                    apt_dict[airport['apt_ident']] = Airport(**apt_data)
                    current_airport = apt_dict[airport['apt_ident']]

                    if isinstance(airport.record, list):
                        records = airport.record
                    else:  # Single Record
                        records = [airport.record]

                    for record in records:
                        current_airport.records.append(AirportRecord(anav_base=self.anav_base, record_data=record))

        return apt_dict

    def _parse_current_meta(self):
        """
        Fetch and parse the current metafile
        :return:
        """
        meta_url = self.anav_base + 'xml_data/d-TPP_Metafile.xml'
        return untangle.parse(meta_url)

    def _state_dict(self):
        """
        Build a dictionary of airports by state
        :return:
        """
        sd = {}
        for id, data in self.apt_dict.items():
            state_code = data.location_data['state_code']
            state_name = data.location_data['state_name']
            if state_code not in sd:
                sd[state_code] = {
                    'state_name': state_name,
                    'airports': []
                }

            sd[state_code]['airports'].append(data)

        return sd