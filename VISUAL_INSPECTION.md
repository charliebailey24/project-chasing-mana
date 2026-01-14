# Visual Inspection Checklist

Manual QA checklist for verifying the weather app renders correctly across varied conditions.

## Test Cities

These 10 cities were selected to cover a wide range of weather conditions, temperatures, and time zones.

| # | City | Why Selected | Expected Conditions |
|---|------|--------------|---------------------|
| 1 | **Phoenix, Arizona, US** | Desert climate | Hot, sunny, clear skies, low humidity |
| 2 | **Seattle, Washington, US** | Pacific Northwest | Overcast, rain, mild temps, high precipitation % |
| 3 | **Reykjavik, Iceland** | Subarctic | Cold, wind, variable conditions, possible snow |
| 4 | **Singapore** | Tropical | Hot, humid, thunderstorms, high precipitation % |
| 5 | **Dubai, UAE** | Arid desert | Extreme heat, clear, possible sandstorm/mist |
| 6 | **London, UK** | Maritime | Overcast, drizzle, mild, fog/mist conditions |
| 7 | **Tokyo, Japan** | Humid subtropical | Varied seasons, rain, typhoon season storms |
| 8 | **Sydney, Australia** | Southern hemisphere | Opposite season, tests date handling |
| 9 | **Anchorage, Alaska, US** | Subarctic | Very cold, snow, extreme temps |
| 10 | **Mumbai, India** | Tropical monsoon | Monsoon rain, extreme humidity, thunderstorms |

## Visual Elements to Verify

For each city, check the following:

### Current Weather Card
- [ ] Location name displays correctly
- [ ] Weather icon matches condition description
- [ ] Temperature displays with °F
- [ ] "Feels like" temperature shows
- [ ] High/Low temperatures display
- [ ] Humidity percentage shows
- [ ] Wind speed shows in mph
- [ ] Pressure displays in hPa
- [ ] Cloud coverage percentage shows
- [ ] Sunrise/Sunset times display correctly

### 5-Day Forecast
- [ ] All 5 days render (or available days)
- [ ] Day labels are correct (Today, Tomorrow, weekday names)
- [ ] Weather icons display for each day
- [ ] High/Low temps show for each day
- [ ] Precipitation % (💧) shows when > 0%
- [ ] Cards are visually aligned

### Weather Icons Coverage
Verify these icon types render correctly:

| Icon | Condition | Test City Likely to Show |
|------|-----------|--------------------------|
| ☀️ | Clear day | Phoenix, Dubai |
| 🌙 | Clear night | Check after sunset |
| ⛅ | Few clouds | Variable |
| ☁️ | Cloudy | Seattle, London |
| 🌧️ | Rain | Seattle, Singapore, Mumbai |
| 🌦️ | Sun + Rain | Singapore, Tokyo |
| ⛈️ | Thunderstorm | Singapore, Mumbai |
| ❄️ | Snow | Reykjavik, Anchorage |
| 🌫️ | Mist/Fog | London, Dubai |

### Edge Cases to Watch
- [ ] Very long city names truncate gracefully
- [ ] Negative temperatures display correctly (Anchorage, Reykjavik)
- [ ] 100% humidity displays correctly
- [ ] 0% precipitation hides the 💧 indicator
- [ ] Night icons show for cities currently in nighttime

## Test Procedure

1. Open the app at `/weather`
2. Search for each city in order
3. Click the first search result
4. Verify all checkboxes above
5. Take screenshot if issues found
6. Note any visual bugs below

## Issues Found

| City | Issue | Screenshot | Status |
|------|-------|------------|--------|
| | | | |

---

*Last updated: 2026-01-14*
