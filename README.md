faa_tpp
=======

Do stuff with the FAAs Digital Terminal Procedures Publication.

Grabs the current edition.

## Installation

`pip install faa-tpp`

## Usage

Initialize as so:
```
from faa_tpp import ParsedTPP

ptpp = ParsedTPP()
```

Get cycle data. Returns a dictionary:
```
ptpp.return_cycle_info()
```

Will return a `dict` something like:
```
{
    "cycle": "1811",
    "cycle_start": "2018-10-11T09:01:00+00:00",
    "cycle_end": "2018-11-08T09:01:00+00:00"
}
```
Cycle times given in ISO 8601 format.


Get the front matter:
```
# Just the URI
ptpp.return_front_matter()

# Get the actual PDF data
ptpp.return_front_matter(return_pdf=True)
```

Get a list of `Airport` objects for a given state code:
```
mi_airports = ptpp.return_state_airports('MI')
```

Get a `dict` of `Airport` objects, keyed by FAA identifier:
```
airport_dict = ptpp.return_dict()

ozw = airport_dict['OZW']  # Capitalized
```

See the available records (IAPs, Minimums, diagrams, etc):
```
ozw.list_available_records()
```

Will print something like:
```
[0] (MIN) TAKEOFF MINIMUMS
[1] (MIN) ALTERNATE MINIMUMS
[2] (STAR) CRUXX SIX
[3] (STAR) FOREY ONE (RNAV)
[4] (STAR) LLEEO TWO
[5] (STAR) OKLND ONE (RNAV)
[6] (STAR) PETTE ONE (RNAV)
[7] (STAR) RRALF ONE (RNAV)
[8] (IAP) ILS OR LOC RWY 13
[9] (IAP) RNAV (GPS) RWY 13
[10] (IAP) RNAV (GPS) RWY 31
[11] (DP) BARII ONE (RNAV)
[12] (DP) CCOBB ONE (RNAV)
[13] (DP) CLVIN ONE (RNAV)
[14] (DP) HHOWE ONE (RNAV)
[15] (DP) KAYLN ONE (RNAV)
[16] (DP) LIDDS ONE (RNAV)
[17] (DP) MIGGY ONE (RNAV)
[18] (DP) PAVYL ONE (RNAV)
[19] (DP) SNDRS ONE (RNAV)
[20] (DP) TRMML ONE (RNAV)
[21] (DP) ZETTR ONE (RNAV)
```

The number in the square brackets indicates the index.


Grab a record:
```
ils_13 = ozw.records[8]
```

Get the URI for the PDF:
```
pdf_uri = ils_13.get_pdf_uri()
```

Get the actual PDF data:
```
pdf_data = ils_13.get_pdf()
```


## Doing something neat?
If you're doing something neat with this, I'd love to hear about it! Open up an issue and let me know.
