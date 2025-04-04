from flask import Flask, request, jsonify
from flask_cors import CORS
from kerykeion import AstrologicalSubject
from datetime import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS

# Tamil configurations (Keep these as they are)
# -------------------------------------------------
THITHI_NAMES = [
    "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி",
    "ஷஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி",
    "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி",
    "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி",
    "ஷஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி",
    "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"
]

KARANA_NAMES = ["பவ", "பாலவ", "கௌலவ", "தைதுல", "கரிஜ", "வணிசை", "விஷ்டி", "சகுனி", "சதுஷ்பாத", "நாக", "கிஸ்துக்ன"]

YOGA_NAMES = [
    "விஷ்கம்பம்", "பீதி", "கௌலவம்", "சைதில்யம்", "கருணை", "வாணிஜம்", "வைத்ருதி",
    "சுபம்", "சுக்லம்", "பிரம்மம்", "ஐந்திரம்", "வைத்ருதி", "சகுனி", "சதுஷ்பாதம்",
    "விஷ்டி", "பிருஹத்தி", "சித்தி", "விச்சுடி", "நித்ரா", "பரிதி"
]

RASI_NAMES = {
    'Ari': 'மேஷம்', 'Tau': 'ரிஷபம்', 'Gem': 'மிதுனம்', 'Can': 'கடகம்',
    'Leo': 'சிம்மம்', 'Vir': 'கன்னி', 'Lib': 'துலாம்', 'Sco': 'விருச்சிகம்',
    'Sag': 'தனுசு', 'Cap': 'மகரம்', 'Aqu': 'கும்பம்', 'Pis': 'மீனம்'
}

PLANET_NAMES = {
    'Sun': 'சூரியன்', 'Moon': 'சந்திரன்', 'Mars': 'செவ்வாய்',
    'Mercury': 'புதன்', 'Jupiter': 'குரு', 'Venus': 'சுக்ரன்',
    'Saturn': 'சனி', 'True_Node': 'ராகு', 'True_South_Node': 'கேது'
}
# Precision position calculation
def get_precise_abs_pos(planet):
    sign_index = list(RASI_NAMES.keys()).index(planet.sign)
    pos = planet.position + (30 * sign_index)
    return round(pos % 360, 6)

# Calculate absolute positions with sign adjustment
def get_abs_pos(planet):
    sign_index = list(RASI_NAMES.keys()).index(planet.sign)
    return planet.position + (30 * sign_index)

def precise_deg_to_dms(degree: float) -> str:
    """Ultra-precise degree conversion"""
    degree = round(degree, 6)
    deg = int(degree)
    minutes_full = (degree - deg) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60)
    
    # Handle 60 seconds rollover
    if seconds >= 60:
        seconds -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        deg += 1
    
    return f"{deg}:{minutes:02d}:{seconds:02d}"

# Geolocation function
def get_location_details(place_name):
    geolocator = Nominatim(user_agent="astro_script")
    tf = TimezoneFinder()
    
    location = geolocator.geocode(place_name)
    if not location:
        return None

    return {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'timezone': tf.timezone_at(lng=location.longitude, lat=location.latitude),
        'place_name': location.address.split(',')[0]
    }
def format_dasha_periods(dasha_periods):
    """
    Convert decimal years to 'years, months, days' format in Tamil.
    """
    formatted_dasha_periods = []
    
    for dasha in dasha_periods:
        planet, years_fraction = dasha.split(": ")
        years_fraction = float(years_fraction.split()[0])  # Extract numerical value

        # Convert decimal years to (years, months, days)
        years = int(years_fraction)
        remaining_months = (years_fraction - years) * 12
        months = int(remaining_months)
        days = round((remaining_months - months) * 30.4375)  # Approximate month length

        # Tamil translation for planets
        PLANET_TAMIL_NAMES = {
            "Sun": "சூரியன்",
            "Moon": "சந்திரன்",
            "Mars": "செவ்வாய்",
            "Rahu": "ராகு",
            "Jupiter": "குரு",
            "Saturn": "சனி",
            "Mercury": "புதன்",
            "Ketu": "கேது",
            "Venus": "சுக்ரன்"
        }

        # Format in Tamil
        formatted_dasha = f"{PLANET_TAMIL_NAMES[planet]} {years} வருடம், {months} மாதம், {days} நாள்"
        formatted_dasha_periods.append(formatted_dasha)

    return formatted_dasha_periods


def get_active_dasha(dasha_periods, birth_datetime):
    """
    Determine the active Dasha period at the time of birth.
    """
    start_date = birth_datetime
    for dasha in dasha_periods:
        planet, years_fraction = dasha.split(": ")
        years_fraction = float(years_fraction.split()[0])

        # Convert to timedelta (years -> days)
        dasha_duration = timedelta(days=years_fraction * 365.25)

        if start_date <= birth_datetime < start_date + dasha_duration:
            # Found the active dasha at birth
            active_dasha = format_dasha_periods([dasha])[0]
            return active_dasha

        # Move to next Dasha period
        start_date += dasha_duration
    
    return None 
def get_dasha_periods(moon_position):
    """
    Calculate the Dasha periods for the native based on the moon's nakshatra.
    """
    # The Dasha lengths in years for each planet
    DASHA_PERIODS = {
        "Sun": 6,
        "Moon": 10,
        "Mars": 7,
        "Rahu": 18,
        "Jupiter": 16,
        "Saturn": 19,
        "Mercury": 17,
        "Ketu": 7,
        "Venus": 20
    }

    # Nakshatra to Planet mapping based on the Moon's position
    nakshatra_planet_mapping = [
        ("அஸ்வினி", "Ketu"),
        ("பரணி", "Venus"),
        ("கிருத்திகை", "Sun"),
        ("ரோகிணி", "Moon"),
        ("மிருகசீரிஷம்", "Mars"),
        ("திருவாதிரை", "Rahu"),
        ("புனர்பூசம்", "Jupiter"),
        ("பூசம்", "Saturn"),
        ("ஆயில்யம்", "Mercury"),
        ("மகம்", "Ketu"),
        ("பூரம்", "Venus"),
        ("உத்திரம்", "Sun"),
        ("அஸ்தம்", "Moon"),
        ("சித்திரை", "Mars"),
        ("ஸ்வாதி", "Rahu"),
        ("விசாகம்", "Jupiter"),
        ("அனுஷம்", "Saturn"),
        ("கேட்டை", "Mercury"),
        ("மூலம்", "Ketu"),
        ("பூராடம்", "Venus"),
        ("உத்திராடம்", "Sun"),
        ("திருவோணம்", "Moon"),
        ("அவிட்டம்", "Mars"),
        ("சதயம்", "Rahu"),
        ("பூரட்டாதி", "Jupiter"),
        ("உத்திரட்டாதி", "Saturn"),
        ("ரேவதி", "Mercury")
    ]

    # Get Nakshatra and Planet based on the moon position
    nakshatra_index = int((moon_position % 360) // 13.3333)
    nakshatra, dasha_planet = nakshatra_planet_mapping[nakshatra_index]

    # Get the Dasha period of the planet based on the Nakshatra
    dasha_period = DASHA_PERIODS[dasha_planet]

    # Determine the position within the Nakshatra
    nakshatra_position = moon_position % 13.3333
    dasha_percentage = nakshatra_position / 13.3333

    # Calculate the starting Dasha period in years
    starting_dasha_years = dasha_period * dasha_percentage

    # Calculate the remaining Dasha period for the planet
    remaining_dasha_years = dasha_period - starting_dasha_years

    # Generate Dasha sequence
    dasha_sequence = [f"{dasha_planet}: {remaining_dasha_years:.2f} years"]

    # Add subsequent Dashas
    planets = list(DASHA_PERIODS.keys())
    planet_index = planets.index(dasha_planet)

    for i in range(1, 9):  # For the next 8 planets
        next_planet = planets[(planet_index + i) % len(planets)]
        dasha_sequence.append(f"{next_planet}: {DASHA_PERIODS[next_planet]} years")

    return dasha_sequence


def calculate_karana(sun_position, moon_position):
    karana_angle = abs(sun_position - moon_position) % 180
    karana_index = int(karana_angle // 16.4)  # 180 degrees / 11 Karanas
    return KARANA_NAMES[karana_index]

def calculate_tithi(sun_position, moon_position):
    """
    Calculate Tithi and determine whether it is Sukla Paksha (Waxing) or Krishna Paksha (Waning)
    """
    tithi_angle = (moon_position - sun_position) % 360  # Difference between Moon and Sun
    tithi_index = int(tithi_angle // 12)  # 360° divided into 30 Tithis

    if tithi_angle < 180:
        paksha = "சுக்லபஷம் (வளர்பிறை)"  # Waxing phase
    else:
        paksha = "கிருஷ்ணபஷம் (தேய்பிறை)"  # Waning phase

    tithi_name = THITHI_NAMES[tithi_index]
    return f"{tithi_name}, {paksha}"


def calculate_yoga(sun_position, moon_position):
    yoga_angle = abs(sun_position - moon_position) % 360
    yoga_index = int(yoga_angle // 13.3333)  # 360 degrees / 27 Yogas
    return YOGA_NAMES[yoga_index]


# Horoscope API Endpoint
@app.route('/horoscope', methods=['POST'])
def horoscope():
    try:
        # Extract input
        data = request.json
        name = data.get("name")
        place = data.get("place")
        birth_date = data.get("date")
        birth_time = data.get("time")

        # Convert date and time
        birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %I:%M %p")

        # Get location details
        location_data = get_location_details(place)
        if not location_data:
            return jsonify({"error": "Invalid place"}), 400

        # Generate horoscope
        native = AstrologicalSubject(
            name=name,
            year=birth_datetime.year, month=birth_datetime.month, day=birth_datetime.day,
            hour=birth_datetime.hour, minute=birth_datetime.minute,
            lng=location_data['longitude'], lat=location_data['latitude'],
            tz_str=location_data['timezone'], zodiac_type="Sidereal", sidereal_mode="LAHIRI"
        )

        # Get the absolute positions of the Sun and Moon
        sun_pos = get_abs_pos(native.sun)
        moon_pos = get_abs_pos(native.moon)

        # Calculate Tithi, Karana, and Yoga
        tithi = calculate_tithi(sun_pos, moon_pos)
        karana = calculate_karana(sun_pos, moon_pos)
        yoga = calculate_yoga(sun_pos, moon_pos)
        dasha_periods = get_dasha_periods(moon_pos)
        
        # Prepare response
        response = {
            "பெயர்": name,
            "பிறந்த நாள்": birth_date,
            "பிறந்த நேரம்": birth_time,
            "பிறந்த இடம்": location_data['place_name'],
            "நெட்டாங்கு": f"{location_data['longitude']}E",
            "அகலாங்கு": f"{location_data['latitude']}N",
            "ராசி": RASI_NAMES[native.moon.sign],
            "விண்மீன்": f"{get_nakshatra_pada(get_abs_pos(native.moon))}",
            "உதய லக்னம்": RASI_NAMES[native.first_house.sign],
            "நிராயன ஸ்புடங்கள்": [],
            "திதி": tithi,
            "கரணம்": karana,
            "யோகம்": yoga,
            "தசை இருப்பு":get_active_dasha(dasha_periods,birth_datetime)
        }

        # Populate planetary positions
        for planet in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'true_node', 'true_south_node']:
            p = getattr(native, planet)
            abs_pos = get_abs_pos(p)
            nakshatra, pada = get_nakshatra_pada(abs_pos)

            response["நிராயன ஸ்புடங்கள்"].append({
                "planet": PLANET_NAMES[p.name],
                "position": precise_deg_to_dms(abs_pos),
                "rasi": RASI_NAMES[p.sign],
                "nakshatra": nakshatra,
                "pada": pada
            })

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper functions
def get_abs_pos(planet):
    sign_index = list(RASI_NAMES.keys()).index(planet.sign)
    return planet.position + (30 * sign_index)

def get_nakshatra_pada(position):
    NAKSHATRA_LIST = [
        (0.0, 13.3333, "அஸ்வினி"), (13.3333, 26.6666, "பரணி"),
        (26.6666, 40.0, "கிருத்திகை"), (40.0, 53.3333, "ரோகிணி"),
        (53.3333, 66.6666, "மிருகசீரிஷம்"), (66.6666, 80.0, "திருவாதிரை"),
        (80.0, 93.3333, "புனர்பூசம்"), (93.3333, 106.6666, "பூசம்"),
        (106.6666, 120.0, "ஆயில்யம்"), (120.0, 133.3333, "மகம்"),
        (133.3333, 146.6666, "பூரம்"), (146.6666, 160.0, "உத்திரம்"),
        (160.0, 173.3333, "அஸ்தம்"), (173.3333, 186.6666, "சித்திரை"),
        (186.6666, 200.0, "ஸ்வாதி"), (200.0, 213.3333, "விசாகம்"),
        (213.3333, 226.6666, "அனுஷம்"), (226.6666, 240.0, "கேட்டை"),
        (240.0, 253.3333, "மூலம்"), (253.3333, 266.6666, "பூராடம்"),
        (266.6666, 280.0, "உத்திராடம்"), (280.0, 293.3333, "திருவோணம்"),
        (293.3333, 306.6666, "அவிட்டம்"), (306.6666, 320.0, "சதயம்"),
        (320.0, 333.3333, "பூரட்டாதி"), (333.3333, 346.6666, "உத்திரட்டாதி"),
        (346.6666, 360.0, "ரேவதி")
    ]
    for start, end, nakshatra in NAKSHATRA_LIST:
        if start <= position < end:
            return nakshatra, min(int((position - start) // 3.3333) + 1, 4)

if __name__ == '__main__':
    app.run(debug=True)
