from collections import Counter
import logging
import requests
import bs4

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MIN_NUM_MEMBERS = 1

def cache(path):
    """Context manager for caching retrieved objects"""
    pass

def _get_member_ids():
    logger.debug('Scraping member ids (intressentid) from search page...')
    url = (
        'http://data.riksdagen.se'
        '/Data/Ledamoter/Skapa-sokfraga-for-ledamotsdata/')
    html = requests.get(url).text
    html = bs4.BeautifulSoup(html, "html.parser")
    dropdowns = html('select', attrs={'name': 'iid'})
    assert len(dropdowns) == 1, 'There should be only one <select> with members'
    dropdown, = dropdowns

    options = dropdown('option')
    assert options[0].text == 'Alla ledamöter'

    member_ids = set([option['value'] for option in options[1:]])
    n = len(member_ids)
    assert n > MIN_NUM_MEMBERS, 'Expected >= {} members, found only {}'.format(
        MIN_NUM_MEMBERS, n)
    logger.debug('Found {} member ids'.format(n))

    assert all((10 <= len(mid) <= 13 for mid in member_ids))

    return member_ids

_ELECTION_AREAS = [
    "Blekinge län",
    "Dalarnas län",
    "Gotlands län",
    "Gävleborgs län",
    "Göteborgs kommun",
    "Hallands län",
    "Jämtlands län",
    "Jönköpings län",
    "Kalmar län",
    "Kronobergs län",
    "Malmö kommun",
    "Norrbottens län",
    "Skåne läns norra och östra",
    "Skåne läns södra",
    "Skåne läns västra",
    "Stockholms kommun",
    "Stockholms län",
    "Södermanlands län",
    "Uppsala län",
    "Värmlands län",
    "Västerbottens län",
    "Västernorrlands län",
    "Västmanlands län",
    "Västra Götalands läns norra",
    "Västra Götalands läns södra",
    "Västra Götalands läns västra",
    "Västra Götalands läns östra",
    "Örebro län",
    "Östergötlands län",
]

_MISSING_PEOPLE = [
    '0818762925009',
    '0631064113607',
    '0462649924092',
    '0553241385804'
    ]

def _get_gender(s):
    s = s.lower()
    assert s in ['man', 'kvinna']

    return s

    raise ValueError("the string '{}' is not a valid gender".format(s))

def _transform_member(raw):
    member = {}

    transforms = {
        'external_id': ('intressent_id', str),
        'first_name': ('tilltalsnamn', str),
        'last_name': ('efternamn', str),
        'birth_year': ('fodd_ar', int),
        'gender': ('kon', _get_gender),
        'image_url_sm': ('bild_url_80', str),
        'image_url_md': ('bild_url_192', str),
        'image_url_lg': ('bild_url_max', str),
    }

    for dst_key, (src_key, transform) in transforms.items():
        member[dst_key] = transform(raw[src_key])

    return member


def get_members(since):
    member_ids = _get_member_ids()

    def get(**query):
        params = {
            'rdlstatus': 'samtliga',
            'utformat': 'json'
        }
        params.update(query)
        logger.debug('Downloading members with params {}'.format(params))

        response = requests.get(
            'http://data.riksdagen.se/personlista/', params=params).json()

        stated_num = int(response['personlista']['@hits'])

        members = response['personlista'].get('person', [])
        assert stated_num == len(members), (
            'Expected {} members, found {}'.format(stated_num, len(members)))

        return members

    # Now try to get all of these members in a not-too-inefficient way
    all_members = []
    # Look through all election areas ("valkrets").
    # However, not all records have a "valkrets", but it seems like space (" ")
    # matches all those which are returned with "valkrets": null.
    for area in _ELECTION_AREAS + [' ']:
        all_members.extend(get(valkrets=area))
        logger.debug('Found {}/{}'.format(len(all_members), len(member_ids)))

    found_ids = {m['intressent_id'] for m in all_members}
    remaining_ids = member_ids - found_ids

    # A small number of members are not found in the above searches.
    # Let's try to get them specifically.
    for mid in remaining_ids:
        all_members.extend(get(iid=mid))

    found_ids = {m['intressent_id'] for m in all_members}
    remaining_ids = member_ids - found_ids

    # Anyone who is still missing now must be in the list of potentially
    # missing people.

    for mid in remaining_ids:
        assert mid in _MISSING_PEOPLE, 'Member {} is missing.'.format(mid)

        msg = (
            "Skipping a member with iid='{}' who is missing."
            " We expected this, so don't worry.").format(mid)
        logger.warning(msg)

    return [_transform_member(raw) for raw in all_members]

# print(len(get_members(None)))
# print(Counter(['a','a ']))

logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
print(get_members(None)[0:2])
