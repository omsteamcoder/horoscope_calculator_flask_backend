from flask import Flask, request, jsonify
import swisseph as swe
import pytz
from datetime import datetime
import math
import os
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
EPHEM_PATH = os.path.join(os.getcwd(), 'ephe')
swe.set_ephe_path(EPHEM_PATH)

# Constants
RASIS = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
    "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

NAKSHATRAS = [
    "அஸ்வினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிடம்",
    "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்",
    "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "ஸ்வாதி",
    "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்",
    "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி",
    "உத்திரட்டாதி", "ரேவதி"
]

PLANET_CODES = {
    'SUN': swe.SUN,
    'MOON': swe.MOON,
    'MARS': swe.MARS,
    'MERCURY': swe.MERCURY,
    'JUPITER': swe.JUPITER,
    'VENUS': swe.VENUS,
    'SATURN': swe.SATURN,
    'RAHU': swe.MEAN_NODE,
    'KETU': -1
}

def convert_to_dms(decimal_degrees):
    degrees = int(decimal_degrees)
    remainder = (decimal_degrees - degrees) * 60
    minutes = int(remainder)
    seconds = round((remainder - minutes) * 60, 2)
    return f"{degrees}°{minutes}'{seconds:.2f}\""

def get_julian_day(date_str, time_str, timezone_str):
    tz = pytz.timezone(timezone_str)
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    localized_dt = tz.localize(dt)
    utc_dt = localized_dt.astimezone(pytz.utc)
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600
    )

def get_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd)

def get_nakshatra(sidereal_longitude):
    total_per_nakshatra = 360 / 27
    nakshatra_index = int(sidereal_longitude // total_per_nakshatra)
    remainder = (sidereal_longitude % total_per_nakshatra) / total_per_nakshatra
    pada = math.floor(remainder * 4) + 1
    return {
        'name': NAKSHATRAS[nakshatra_index % 27],
        'number': nakshatra_index % 27 + 1,
        'pada': pada,
        'percent': round(remainder * 100, 2)
    }

def get_ascendant(jd, lat, lon, ayanamsa):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL | swe.FLG_NONUT
    houses = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc = houses[1][0]  # Use the actual calculated value
    return {
        'degrees': asc,
        'rasi': RASIS[int(asc // 30) % 12],
        'exact': convert_to_dms(asc)
    }

def get_planet_positions(jd, ayanamsa):
    positions = {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    for planet, code in PLANET_CODES.items():
        if code == -1:
            continue  # Skip Ketu (handled later)
        # Compute actual positions
        pos = swe.calc_ut(jd, code, flags=flags)
        sidereal = pos[0][0]
        positions[planet] = {
            'sidereal': sidereal,
            'exact': convert_to_dms(sidereal),
            'rasi': RASIS[int(sidereal // 30) % 12],
            'nakshatra': get_nakshatra(sidereal)
        }
    # Add Ketu
    if 'RAHU' in positions:
        ketu_sidereal = (positions['RAHU']['sidereal'] + 180) % 360
        positions['KETU'] = {
            'sidereal': ketu_sidereal,
            'exact': convert_to_dms(ketu_sidereal),
            'rasi': RASIS[int(ketu_sidereal // 30) % 12],
            'nakshatra': get_nakshatra(ketu_sidereal)
        }
    return positions

@app.route('/horoscope', methods=['POST'])
def horoscope():
    data = request.json
    name=data['name']
    date = data['date']
    time = data['time']
    timezone = data['timezone']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    
    try:
        jd = get_julian_day(date, time, timezone)
        ayanamsa = get_ayanamsa(jd)
        ascendant = get_ascendant(jd, latitude, longitude, ayanamsa)
        planets = get_planet_positions(jd, ayanamsa)
        
        return jsonify({
            'name': name,
            'date': date,
            'time': time,
            'timezone': timezone,
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'ayanamsa': ayanamsa,
            'ascendant': ascendant,
            'planets': planets,
            'moon': {
                'rasi': planets['MOON']['rasi'],
                'nakshatra': planets['MOON']['nakshatra']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)