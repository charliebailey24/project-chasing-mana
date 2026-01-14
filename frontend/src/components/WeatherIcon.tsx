interface WeatherIconProps {
  icon: string;
  description: string;
  size?: number;
}

// Map OpenWeatherMap icon codes to emoji
const iconMap: Record<string, string> = {
  '01d': '\u2600\ufe0f',     // clear sky day - sun
  '01n': '\ud83c\udf19',     // clear sky night - crescent moon
  '02d': '\u26c5',           // few clouds day - sun behind cloud
  '02n': '\ud83c\udf19',     // few clouds night - crescent moon
  '03d': '\u2601\ufe0f',     // scattered clouds - cloud
  '03n': '\u2601\ufe0f',
  '04d': '\u2601\ufe0f',     // broken clouds - cloud
  '04n': '\u2601\ufe0f',
  '09d': '\ud83c\udf27\ufe0f', // shower rain - cloud with rain
  '09n': '\ud83c\udf27\ufe0f',
  '10d': '\ud83c\udf26\ufe0f', // rain day - sun behind rain cloud
  '10n': '\ud83c\udf27\ufe0f', // rain night - cloud with rain
  '11d': '\u26c8\ufe0f',     // thunderstorm - cloud with lightning and rain
  '11n': '\u26c8\ufe0f',
  '13d': '\u2744\ufe0f',     // snow - snowflake
  '13n': '\u2744\ufe0f',
  '50d': '\ud83c\udf2b\ufe0f', // mist - fog
  '50n': '\ud83c\udf2b\ufe0f',
};

export function WeatherIcon({ icon, description, size = 48 }: WeatherIconProps) {
  const emoji = iconMap[icon] || '\u2753'; // question mark if unknown

  return (
    <span
      role="img"
      aria-label={description}
      style={{ fontSize: size }}
    >
      {emoji}
    </span>
  );
}
