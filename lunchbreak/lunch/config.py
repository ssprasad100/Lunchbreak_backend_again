import random

COST_GROUP_ALWAYS = 0
COST_GROUP_ADDITIONS = 1
COST_GROUP_BOTH = 2

COST_GROUP_CALCULATIONS = (
    (COST_GROUP_ALWAYS, 'Altijd de groepsprijs'),
    (COST_GROUP_ADDITIONS, 'Duurder bij toevoegen, zelfde bij aftrekken'),
    (COST_GROUP_BOTH, 'Duurder bij toevoegen, goedkoper bij aftrekken')
)

ICONS = (
    (0, 'Onbekend'),
    # 1xx StoreCategories
    (100, 'Slager'),
    (101, 'Bakker'),
    (102, 'Broodjeszaak'),
    # 2xx Ingredients
    (200, 'Tomaten'),
    # 3xx FoodTypes
    (300, 'Broodje')
)

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7
WEEKDAYS = (
    (MONDAY, 'Maandag'),
    (TUESDAY, 'Dinsdag'),
    (WEDNESDAY, 'Woensdag'),
    (THURSDAY, 'Donderdag'),
    (FRIDAY, 'Vrijdag'),
    (SATURDAY, 'Zaterdag'),
    (SUNDAY, 'Zondag')
)

INPUT_AMOUNT = 0
INPUT_SI_VARIABLE = 1
INPUT_SI_SET = 2

INPUT_TYPES = (
    (INPUT_AMOUNT, 'Aantal'),
    (INPUT_SI_VARIABLE, 'Aanpasbaar o.b.v. SI-eenheid'),
    (INPUT_SI_SET, 'Vaste hoeveelheid o.b.v. SI-eenheid'),
)

TOKEN_IDENTIFIER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789'
TOKEN_IDENTIFIER_LENGTH = 64


def random_token():
    rnd = random.SystemRandom()
    return ''.join(rnd.choice(TOKEN_IDENTIFIER_CHARS) for _ in range(TOKEN_IDENTIFIER_LENGTH))


BELGIUM = 0
NETHERLANDS = 1
LUXEMBURG = 2
FRANCE = 3
GERMANY = 4
COUNTRIES = (
    (BELGIUM, 'Belgium'),
    (NETHERLANDS, 'The Netherlands'),
    (LUXEMBURG, 'Luxemburg'),
    (FRANCE, 'France'),
    (GERMANY, 'Germany'),
)

LANGUAGES = {
    BELGIUM: 'nl',
    NETHERLANDS: 'nl',
    LUXEMBURG: 'fr',
    FRANCE: 'fr',
    GERMANY: 'de'
}

CCTLDS = {
    BELGIUM: 'be',
    NETHERLANDS: 'nl',
    LUXEMBURG: 'lu',
    FRANCE: 'fr',
    GERMANY: 'de'
}
