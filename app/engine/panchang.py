from skyfield.api import load, Topos
from skyfield.almanac import sunrise_sunset, find_discrete, risings_and_settings, moon_phases
from skyfield.magnitudelib import planetary_magnitude
import datetime

# Masa (Months)
MASA_LIST = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", 
    "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
]

PAKSHA_LIST = ["Shukla", "Krishna"]

class SmaranEngine:
    def __init__(self):
        self.ts = load.timescale()
        self.eph = load('de421.bsp') # Will download if not present
        self.sun = self.eph['sun']
        self.moon = self.eph['moon']
        self.earth = self.eph['earth']

        self._yearly_cache = {}

    def get_tithi(self, time):
        """
        Calculate the Tithi for a given Skyfield Time object.
        Returns Tithi index (1-30).
        1-15: Shukla Paksha
        16-30: Krishna Paksha
        """
        astrometric_sun = self.earth.at(time).observe(self.sun).apparent()
        astrometric_moon = self.earth.at(time).observe(self.moon).apparent()

        _, lon_sun, _ = astrometric_sun.ecliptic_latlon()
        _, lon_moon, _ = astrometric_moon.ecliptic_latlon()

        angle = (lon_moon.degrees - lon_sun.degrees) % 360
        tithi_float = angle / 12.0
        tithi_index = int(tithi_float) + 1
        return tithi_index

    def find_new_moons(self, year):
        # We search throughout the year for New Moons
        t0 = self.ts.utc(year - 1, 12, 15) # Start slightly before year
        t1 = self.ts.utc(year + 1, 2, 1)   # End slightly after
        
        t_phases, phases = find_discrete(t0, t1, moon_phases(self.eph))
        
        # Filter for New Moons (phase == 0)
        new_moons = [t for t, p in zip(t_phases, phases) if p == 0]
        return new_moons

    def get_ayanamsa_approx(self, time):
        # Lahiri Ayanamsa approximation
        # Base: ~23.85 degrees in 2000
        # Rate: ~0.0139 degrees per year
        t = time.utc_datetime()
        year_diff = t.year - 2000 + (t.timetuple().tm_yday / 366.0)
        return 23.85 + (year_diff * 0.0139)

    def get_solar_rashi(self, time):
        """Returns the Nirayana (Sidereal) Rashi index (0-11) of the Sun at a given time."""
        _, sun_lon, _ = self.earth.at(time).observe(self.sun).apparent().ecliptic_latlon()
        tropical_deg = sun_lon.degrees
        ayanamsa = self.get_ayanamsa_approx(time)
        sidereal_deg = (tropical_deg - ayanamsa) % 360
        return int(sidereal_deg / 30)

    def get_yearly_panchang(self, year, latitude, longitude):
        """
        Efficiently calculates Panchang for every day of the year.
        Returns a dict: { (masa_name, paksha_name, tithi_int): [date_obj, ...] }
        """
        cache_key = (year, round(latitude, 2), round(longitude, 2))
        if cache_key in self._yearly_cache:
            return self._yearly_cache[cache_key]
            
        mapping = {}
        topos_location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        
        # 1. Pre-calculate Lunar Months (New Moons)
        new_moons = self.find_new_moons(year)
        lunar_months = []
        
        for i in range(len(new_moons) - 1):
            nm_current = new_moons[i]
            nm_next = new_moons[i+1]
            
            # Determine Masa Name based on Solar Rashi at New Moon
            # Standard logic: Solar Rashi at NM determines masa.
            # Rashi 0 (Aries) -> Vaishakha? No.
            # Usually: 
            # Aries (0) -> Vaishakha (1)
            # Pisces (11) -> Chaitra (0)
            # So Masa Index = (Rashi + 1) % 12
            
            rashi = self.get_solar_rashi(nm_current)
            masa_idx = (rashi + 1) % 12
            
            # Is Adhika? 
            # If two New Moons fall in same Rashi... 
            # Strict logic: Compare Rashi of this NM vs Next NM?
            # Creating simplified list for now: [Start_Time, End_Time, Masa_Name]
            
            lunar_months.append({
                "start": nm_current,
                "end": nm_next,
                "masa": MASA_LIST[masa_idx] 
                # Note: Adhika logic is complex to perfect here in one pass without iterating solar transitions,
                # but this aligns with our dynamic logic in get_panchang_from_date
            })

        # 2. Iterate every day of the year
        curr = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        one_day = datetime.timedelta(days=1)
        
        while curr <= end:
            # A. Calculate Sunrise
            t_start = self.ts.utc(curr.year, curr.month, curr.day, 0)
            t_end = self.ts.utc(curr.year, curr.month, curr.day, 23, 59)
            t_almanac, y_almanac = find_discrete(t_start, t_end, sunrise_sunset(self.eph, topos_location))
            
            sunrise_moment = None
            for t_event, type_event in zip(t_almanac, y_almanac):
                if type_event == 1:
                    sunrise_moment = t_event
                    break
            
            if sunrise_moment is None:
                # Fallback to noon
                sunrise_moment = self.ts.utc(curr.year, curr.month, curr.day, 12, 0)
                
            # B. Get Tithi
            tithi_idx = self.get_tithi(sunrise_moment)
            paksha = "Shukla" if tithi_idx <= 15 else "Krishna"
            tithi_val = tithi_idx if tithi_idx <= 15 else tithi_idx - 15
            
            # C. Determine Masa
            # Find which lunar month interval contains this sunrise
            # We compare Times.
            masa_name = None
            for lm in lunar_months:
                # Comparison of Skyfield Time objects? 
                # Need to use .tt (Terrestrial Time) float for comparison or check docs.
                # Actually Time objects support comparison operators.
                if lm["start"].tt <= sunrise_moment.tt < lm["end"].tt:
                    masa_name = lm["masa"]
                    break
            
            if masa_name:
                key = (masa_name, paksha, tithi_val)
                if key not in mapping:
                    mapping[key] = []
                mapping[key].append(curr)
                
            curr += one_day
            
        self._yearly_cache[cache_key] = mapping
        return mapping





    def find_event_date(self, year, masa, paksha, tithi, latitude, longitude, recurrence_type="yearly", return_all=False):
        """
        Find the Gregorian Date(s) for a specific Hindu Event.
        Handles Recurrence:
        - yearly: Needs masa, paksha, tithi
        - monthly: Needs paksha, tithi (masa is ignored/None). Finds occurrences in current year.
        - paksha: Needs tithi (masa, paksha ignored). Finds occurrences.
        
        If return_all is True, returns a list of ALL matching dates in that year.
        If return_all is False, returns the first date >= Today (or None if none left in year).
        """
        topos_location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        
        # 1. Broadly search for New Moons covering the year
        new_moons = self.find_new_moons(year)
        
        candidates = []

        # 2. Iterate through Lunar Months
        for i in range(len(new_moons) - 1):
            nm_start = new_moons[i]
            nm_end = new_moons[i+1]
            
            rashi_start = self.get_solar_rashi(nm_start)
            rashi_end = self.get_solar_rashi(nm_end)
            is_adhika = (rashi_start == rashi_end)
            
            # Masa Index Calculation
            current_masa_index = -1
            if not is_adhika:
                current_masa_index = rashi_end % 12
            else:
                current_masa_index = (rashi_start + 1) % 12
            
            current_masa_name = MASA_LIST[current_masa_index]

            # Recurrence Filtering
            is_match = False
            
            if recurrence_type == "yearly":
                # Strict match on Masa
                if current_masa_name == masa:
                    # Skip Adhika for yearly unless explicit (not supported yet)
                    if not is_adhika:
                        is_match = True
            
            elif recurrence_type == "monthly":
                # Every month matches (skip Adhika for simplicity or include it? Let's include all non-adhika for now)
                if not is_adhika:
                    is_match = True
            
            elif recurrence_type == "paksha":
                if not is_adhika:
                    is_match = True

            if not is_match:
                continue
                
            # If match, check dates
            # Determine Target Paksha/Tithi
            # For 'paksha' recurrence, we check BOTH Shukla and Krishna in this month.
            
            pakshas_to_check = [paksha] if recurrence_type in ["yearly", "monthly"] else ["Shukla", "Krishna"]
            
            for p_check in pakshas_to_check:
                target_tithi_count = tithi if p_check == "Shukla" else 15 + tithi
                days_to_add = target_tithi_count - 1
                approx_date_time = nm_start + datetime.timedelta(days=days_to_add)
                
                # Refine with Sunrise Rule
                base_date = approx_date_time.utc_datetime().date()
                
                found_date = None
                for offset in range(-2, 4):
                    check_date = base_date + datetime.timedelta(days=offset)
                    
                    t_start = self.ts.utc(check_date.year, check_date.month, check_date.day, 0)
                    t_end = self.ts.utc(check_date.year, check_date.month, check_date.day, 23, 59)
                    
                    t_almanac, y_almanac = find_discrete(t_start, t_end, sunrise_sunset(self.eph, topos_location))
                    
                    sunrise_moment = None
                    for t_event, type_event in zip(t_almanac, y_almanac):
                        if type_event == 1: # Sunrise
                            sunrise_moment = t_event
                            break
                    
                    if sunrise_moment is None:
                        continue

                    current_tithi = self.get_tithi(sunrise_moment)
                    
                    calculated_paksha = "Shukla" if current_tithi <= 15 else "Krishna"
                    calculated_tithi = current_tithi if current_tithi <= 15 else current_tithi - 15
                    
                    if calculated_paksha == p_check and calculated_tithi == tithi:
                        found_date = check_date
                        break
                
                if found_date:
                    candidates.append(found_date)

        # Post-Processing candidates
        
        candidates.sort()
        
        if return_all:
            return candidates
            
        # Default behavior: next upcoming
        today = datetime.date.today()
        for d in candidates:
            if d >= today:
                return d
                
    def get_panchang_from_date(self, date_obj, latitude, longitude):
        """
        Calculate Tithi, Masa, Paksha for a given Gregorian Date.
        Calculations are based on Sunrise at the given location.
        """
        topos_location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        
        # Calculate Sunrise for the given date
        t_start = self.ts.utc(date_obj.year, date_obj.month, date_obj.day, 0)
        t_end = self.ts.utc(date_obj.year, date_obj.month, date_obj.day, 23, 59)
        
        t_almanac, y_almanac = find_discrete(t_start, t_end, sunrise_sunset(self.eph, topos_location))
        
        sunrise_moment = None
        for t_event, type_event in zip(t_almanac, y_almanac):
            if type_event == 1: # Sunrise
                sunrise_moment = t_event
                break
        
        if sunrise_moment is None:
            # Fallback to noon if sunrise calculation fails (e.g. extreme latitudes)
            sunrise_moment = self.ts.utc(date_obj.year, date_obj.month, date_obj.day, 12, 0)

        # 1. Calculate Tithi at Sunrise
        tithi_index = self.get_tithi(sunrise_moment)
        
        paksha = "Shukla" if tithi_index <= 15 else "Krishna"
        tithi = tithi_index if tithi_index <= 15 else tithi_index - 15

        # 2. Calculate Masa
        # Correct Logic (Amanta): 
        # The Lunar Month starts at the New Moon.
        # The name of the month is determined by the Solar Rashi at that New Moon (or strictly speaking, the Rashi of the *next* New Moon determines the name, but usually mapped as: 
        # New Moon in Aries -> Starts Vaishakha
        # New Moon in Taurus -> Starts Jyeshtha
        # New Moon in Gemini -> Starts Ashadha 
        # New Moon in Cancer -> Starts Shravana
        
        # So we need to find the *previous* New Moon relative to sunrise_moment
        
        # Search backwards up to 40 days
        t_search_end = sunrise_moment
        t_search_start = self.ts.utc(date_obj.year, date_obj.month, date_obj.day - 40)
        
        t_phases, phases = find_discrete(t_search_start, t_search_end, moon_phases(self.eph))
        
        # Get the last New Moon (phase 0) in this list
        last_new_moon = None
        for t, p in zip(reversed(t_phases), reversed(phases)):
            if p == 0:
                last_new_moon = t
                break
        
        if last_new_moon is not None:
            solar_rashi = self.get_solar_rashi(last_new_moon)
            # New Moon in Gemini (2) -> Ashadha (3)
            # New Moon in Cancer (3) -> Shravana (4)
            # So Masa Index = (Solar Rashi + 1) % 12
            masa_index = (solar_rashi + 1) % 12
        else:
            # Fallback if search fails (should generally not happen with -40 days)
            solar_rashi = self.get_solar_rashi(sunrise_moment)
            masa_index = (solar_rashi + 1) % 12

        masa = MASA_LIST[masa_index]
        
        return {
            "masa": masa,
            "paksha": paksha,
            "tithi": tithi
        }

engine_instance = SmaranEngine()
