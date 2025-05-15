import json

TAMIL_PLANETS = {
    "சூரியன்", "சந்திரன்", "செவ்வாய்", "புதன்", "குரு", "சுக்ரன்", "சனி", "ராகு", "கேது", "லக்னம்"
}


def calculate_doshams(horoscope_data):
    rasi_houses = horoscope_data.get("ராசி வீடுகள்", {})
    navamsa_houses = horoscope_data.get("நவாம்ச வீடுகள்", {})
    lagna_rasi = horoscope_data.get("உதய லக்னம்", "")
    planets = horoscope_data.get("நிராயன ஸ்புடங்கள்", [])
    
    def find_rasi(planet_name):
        for rasi, bodies in rasi_houses.items():
            if planet_name in bodies:
                return rasi
        return None

    def find_navamsa(planet_name):
        for rasi, bodies in navamsa_houses.items():
            if planet_name in bodies:
                return rasi
        return None

    # Reference order for houses
    rasi_order = [
        "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
        "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
    ]

    def get_house_distance(from_rasi, to_rasi):
        if from_rasi not in rasi_order or to_rasi not in rasi_order:
            return None
        start = rasi_order.index(from_rasi)
        end = rasi_order.index(to_rasi)
        # Count forward from Lagna (start), wrapping around the zodiac
        if end >= start:
            return end - start + 1
        else:
            return (12 - start) + end + 1
  # Returns 1-12

    # Dosham 1: Suriyan-Chevva Dosham (Sun & Mars in same Rasi)
    suriyan_chevva_dosham = (
        (planet_rasi := find_rasi("சூரியன்")) is not None
        and find_rasi("செவ்வாய்") == planet_rasi
    )

    # Dosham 2: Chevva Dosham (Mars in 2, 4, 7, 8, 12 from Lagna)
    chevva_dosham = False
    mars_rasi = find_rasi("செவ்வாய்")
    if lagna_rasi and mars_rasi:
        dist = get_house_distance(lagna_rasi, mars_rasi)
        chevva_dosham = dist in {2, 4, 7, 8, 12}

    # Dosham 3: Naga Dosham (Rahu/Ketu in 1, 2, 5, 7, 8)
    rahu_rasi = find_rasi("ராகு")
    ketu_rasi = find_rasi("கேது")
    naga_dosham = False
    if lagna_rasi:
        rahu_dist = get_house_distance(lagna_rasi, rahu_rasi) if rahu_rasi else None
        ketu_dist = get_house_distance(lagna_rasi, ketu_rasi) if ketu_rasi else None
        naga_dosham = any(d in {1, 2, 5, 7, 8} for d in (rahu_dist, ketu_dist) if d is not None)
    # Dosham 4: Kula Sarga Dosham (Rahu or Ketu in 2 or 8)
    kula_sarga_dosham = any(
        (d := get_house_distance(lagna_rasi, r)) in {2, 8}
        for r in (rahu_rasi, ketu_rasi) if r is not None
    )

    # Dosham 5: Rahu Dosham (Rahu with Moon)
    rahu_dosham = (
        rahu_rasi is not None
        and any(p["planet"] == "சந்திரன்" and p.get("rasi") == rahu_rasi for p in planets)
    )

    # Dosham 6: Ketu Dosham (Ketu with Moon)
    ketu_dosham = (
        ketu_rasi is not None
        and any(p["planet"] == "சந்திரன்" and p.get("rasi") == ketu_rasi for p in planets)
    )

    # Dosham 7: Kalathira Dosham (Saturn in 7th house)
    sani_rasi = find_rasi("சனி")
    kalathira_dosham = False
    if lagna_rasi and sani_rasi:
        kalathira_dosham = get_house_distance(lagna_rasi, sani_rasi) == 7

    # Dosham 8: Chandra-Ketu Dosham in Navamsa
    chandra_ketu_dosham = (
        (nv1 := find_navamsa("சந்திரன்")) is not None
        and nv1 == find_navamsa("கேது")
    )

    return {
        "சூரியன்-செவ்வாய் தோஷம்": suriyan_chevva_dosham,
        "செவ்வாய் தோஷம்": chevva_dosham,
        "நாக தோஷம்": naga_dosham,
        "குலசாரக தோஷம்": kula_sarga_dosham,
        "ராகு தோஷம்": rahu_dosham,
        "கேது தோஷம்": ketu_dosham,
        "கலத்திர தோஷம்": kalathira_dosham,
        "சந்திரன்-கேது நவாம்ச தோஷம்": chandra_ketu_dosham
    }

data={
    "அகலாங்கு": "30.3843674N",
    "அயனாம்சம்": "23.9166° (Lahiri approximation)",
    "உதய லக்னம்": "கடகம்",
    "கரணம்": "பத்தரை (விஷ்டி)",
    "சுத்த ஜாதகம்": "86.75% சுத்தம்",
    "தசை இருப்பு": "ராகு 3 வருடம், 4 மாதம், 28 நாள்",
    "திதி": "சப்தமி, கிருஷ்ணபஷம் (தேய்பிறை)",
    "நவாம்ச வீடுகள்": {
        "கடகம்": [],
        "கன்னி": [],
        "கும்பம்": [],
        "சிம்மம்": [],
        "தனுசு": [
            "செவ்வாய்"
        ],
        "துலாம்": [
            "சூரியன்"
        ],
        "மகரம்": [
            "சனி"
        ],
        "மிதுனம்": [],
        "மீனம்": [
            "சந்திரன்",
            "லக்னம்"
        ],
        "மேஷம்": [
            "புதன்",
            "குரு"
        ],
        "ரிஷபம்": [
            "ராகு"
        ],
        "விருச்சிகம்": [
            "சுக்ரன்",
            "கேது"
        ]
    },
    "நிராயன ஸ்புடங்கள்": [
        {
            "nakshatra": "மிருகசீரிஷம்",
            "pada": 3,
            "planet": "சூரியன்",
            "position": "60:06:14",
            "rasi": "மிதுனம்"
        },
        {
            "nakshatra": "சதயம்",
            "pada": 4,
            "planet": "சந்திரன்",
            "position": "317:28:20",
            "rasi": "கும்பம்"
        },
        {
            "nakshatra": "ரோகிணி",
            "pada": 1,
            "planet": "புதன்",
            "position": "41:25:46",
            "rasi": "ரிஷபம்"
        },
        {
            "nakshatra": "பரணி",
            "pada": 4,
            "planet": "சுக்ரன்",
            "position": "24:40:58",
            "rasi": "மேஷம்"
        },
        {
            "nakshatra": "ரேவதி",
            "pada": 1,
            "planet": "செவ்வாய்",
            "position": "347:05:21",
            "rasi": "மீனம்"
        },
        {
            "nakshatra": "புனர்பூசம்",
            "pada": 1,
            "planet": "குரு",
            "position": "82:05:40",
            "rasi": "மிதுனம்"
        },
        {
            "nakshatra": "உத்திராடம்",
            "pada": 2,
            "planet": "சனி",
            "position": "270:19:23",
            "rasi": "மகரம்"
        },
        {
            "nakshatra": "திருவோணம்",
            "pada": 2,
            "planet": "ராகு",
            "position": "284:23:15",
            "rasi": "மகரம்"
        },
        {
            "nakshatra": "பூசம்",
            "pada": 4,
            "planet": "கேது",
            "position": "104:23:15",
            "rasi": "கடகம்"
        },
        {
            "nakshatra": "ஆயில்யம்",
            "pada": 4,
            "planet": "லக்னம்",
            "position": "119:39:02",
            "rasi": "கடகம்"
        }
    ],
    "நெட்டாங்கு": "76.770421E",
    "பிறந்த இடம்": "Ambala",
    "பிறந்த நாள்": "15-06-1990",
    "பிறந்த நேரம்": "10:00 AM",
    "பெயர்": "Jebin",
    "யோகம்": "ப்ரீதி",
    "ராசி": "கும்பம்",
    "ராசி வீடுகள்": {
        "கடகம்": [
            "கேது",
            "லக்னம்"
        ],
        "கன்னி": [],
        "கும்பம்": [
            "சந்திரன்"
        ],
        "சிம்மம்": [],
        "தனுசு": [],
        "துலாம்": [],
        "மகரம்": [
            "சனி",
            "ராகு"
        ],
        "மிதுனம்": [
            "சூரியன்",
            "குரு"
        ],
        "மீனம்": [
            "செவ்வாய்"
        ],
        "மேஷம்": [
            "சுக்ரன்"
        ],
        "ரிஷபம்": [
            "புதன்"
        ],
        "விருச்சிகம்": []
    },
    "விண்மீன்": "சதயம்"
}
    
resul = calculate_doshams(data)
print(json.dumps(resul, indent=2, ensure_ascii=False))
