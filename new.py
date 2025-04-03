from kerykeion import AstrologicalSubject
from datetime import datetime
from geopy.geocoders import Nominatim  # For geocoding
from timezonefinder import TimezoneFinder  # For time zone detection


# ============== TAMIL CONFIGURATIONS ==============

THITHI_NAMES = [
    "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி",
    "ஷஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி",
    "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி",
    "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி",
    "ஷஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி",
    "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"
]

# கரணம் (Karana) names
KARANA_NAMES = [
    "பவ", "பாலவ", "கௌலவ", "தைதுல", "கரிஜ",
    "வணிசை", "விஷ்டி", "சகுனி", "சதுஷ்பாத", "நாக",
    "கிஸ்துக்ன"
]

YOGA_NAMES = [
    "விஷ்கம்பம்", "பீதி", "கௌலவம்", "சைதில்யம்", "கருணை",
    "வாணிஜம்", "வைத்ருதி", "விஷ்கம்பம்", "பீதி", "கௌலவம்",
    "சைதில்யம்", "கருணை", "வாணிஜம்", "வைத்ருதி", "சுபம்",
    "சுக்லம்", "பிரம்மம்", "ஐந்திரம்", "வைத்ருதி", "சகுனி",
    "சதுஷ்பாதம்", "விஷ்டி", "பிருஹத்தி", "சித்தி", "விச்சுடி",
    "நித்ரா", "பரிதி"
]



RASI_NAMES = {
    'Ari': 'மேஷம்', 'Tau': 'ரிஷபம்', 'Gem': 'மிதுனம்',
    'Can': 'கடகம்', 'Leo': 'சிம்மம்', 'Vir': 'கன்னி',
    'Lib': 'துலாம்', 'Sco': 'விருச்சிகம்', 'Sag': 'தனுசு',
    'Cap': 'மகரம்', 'Aqu': 'கும்பம்', 'Pis': 'மீனம்'
}

PLANET_NAMES = {
    'Sun': 'சூரியன்', 'Moon': 'சந்திரன்', 'Mars': 'செவ்வாய்',
    'Mercury': 'புதன்', 'Jupiter': 'குரு', 'Venus': 'சுக்ரன்',
    'Saturn': 'சனி', 'True_Node': 'ராகு', 'True_South_Node': 'கேது'
}

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

# ============== PRECISION CALCULATIONS ==============
def get_nakshatra_pada(position: float) -> tuple:
    """Precise நட்சத்திரம் and பாதம் calculation"""
    position = round(position % 360, 6)  # Normalize and round
    
    for start, end, nakshatra in NAKSHATRA_LIST:
        if start <= position < end:
            break
    
    pada_deg = round(position - start, 6)
    pada = min(int(pada_deg // 3.3333) + 1, 4)
    return nakshatra, pada

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

# Special Rahu/Ketu adjustment
def adjust_node_position(pos):
    """Fine-tuned node position adjustment"""
    adjusted = pos + 1.66  # Empirical correction factor
    return round(adjusted % 360, 6)


# ============== GEOCODING FUNCTION ==============
def get_location_details(place_name):
    geolocator = Nominatim(user_agent="astro_script")
    tf = TimezoneFinder()
    
    try:
        location = geolocator.geocode(place_name)
        if not location:
            raise ValueError("Place not found")
            
        latitude = location.latitude
        longitude = location.longitude
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
        
        return {
            'latitude': round(latitude, 4),
            'longitude': round(longitude, 4),
            'timezone': timezone_str,
            'place_name': location.address.split(',')[0]
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# ============== USER INPUT ==============
place = input("Enter birth place (e.g. 'Ambala, India'): ")
location_data = get_location_details(place)

while not location_data:
    print("Invalid location. Try again with more specific name (City, Country)")
    place = input("Enter birth place: ")
    location_data = get_location_details(place)
    
# ============== HOROSCOPE CALCULATION ==============
native = AstrologicalSubject(
    name="Joe",
    year=1990, month=6, day=15,
    hour=10, minute=00,
    lng=location_data['longitude'],
    lat=location_data['latitude'],
    tz_str=location_data['timezone'],
    zodiac_type="Sidereal",
    sidereal_mode="LAHIRI"
)

# Precision position calculation
def get_precise_abs_pos(planet):
    sign_index = list(RASI_NAMES.keys()).index(planet.sign)
    pos = planet.position + (30 * sign_index)
    return round(pos % 360, 6)

# Calculate absolute positions with sign adjustment
def get_abs_pos(planet):
    sign_index = list(RASI_NAMES.keys()).index(planet.sign)
    return planet.position + (30 * sign_index)

# ============== OUTPUT FORMATTING ==============
print(f"பெயர்          : {native.name}")
print(f"பிறந்த தேதி   : {native.day}-{native.month}-{native.year}")
print(f"பிறந்த நேரம்  : {native.hour}:{native.minute:02d} {'PM' if native.hour >= 12 else 'AM'}")
print(f"பிறந்த இடம்   : {location_data['place_name']}")
print(f"நெட்தாகு      : {precise_deg_to_dms(location_data['longitude'])}E")
print(f"அகலாங்கு     : {precise_deg_to_dms(location_data['latitude'])} N\n")


# Lagna and Rasi Details
print(f"உதய லக்னம்   : {RASI_NAMES[native.first_house.sign]}")
print(f"ராசி          : {RASI_NAMES[native.moon.sign]}")

# Moon's nakshatra calculation
moon_abs_pos = get_abs_pos(native.moon)
moon_nakshatra, moon_pada = get_nakshatra_pada(moon_abs_pos)
print(f"விண்மீன்      : {moon_nakshatra}, பாதம் {moon_pada}\n")


# ============== PRECISION OUTPUT ==============
print("நிராயன ஸ்புடங்கள்")
print("| கிரகம்   | திகாம்‌சம்   | ராசி    | நட்சத்திரம்-பாதம்  |")
print("|---------|------------|--------|-----------------|")

# Lagna (Ascendant)
lagna_pos = get_precise_abs_pos(native.first_house)
lagna_nakshatra, lagna_pada = get_nakshatra_pada(lagna_pos)
print(f"| லக்னம்  | {precise_deg_to_dms(lagna_pos)} | {RASI_NAMES[native.first_house.sign]:<6} | {lagna_nakshatra} - {lagna_pada:<2} |")

# Planets
for planet in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']:
    p = getattr(native, planet)
    abs_pos = get_precise_abs_pos(p)
    nakshatra, pada = get_nakshatra_pada(abs_pos)
    print(f"| {PLANET_NAMES[p.name]:<7} | {precise_deg_to_dms(abs_pos)} | {RASI_NAMES[p.sign]:<6} | {nakshatra} - {pada:<2} |")

# Rahu and Ketu with special adjustment
rahu_pos = adjust_node_position(get_precise_abs_pos(native.true_node))
rahu_nakshatra, rahu_pada = get_nakshatra_pada(rahu_pos)
print(f"| ராகு    | {precise_deg_to_dms(rahu_pos)} | {RASI_NAMES[native.true_node.sign]:<6} | {rahu_nakshatra} - {rahu_pada:<2} |")

ketu_pos = adjust_node_position(get_precise_abs_pos(native.true_south_node))
ketu_nakshatra, ketu_pada = get_nakshatra_pada(ketu_pos)
print(f"| கேது    | {precise_deg_to_dms(ketu_pos)} | {RASI_NAMES[native.true_south_node.sign]:<6} | {ketu_nakshatra} - {ketu_pada:<2} |")

