from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.utils import timezone
from . import models
import requests
from datetime import timedelta


class Weather(View):

    @staticmethod
    def _get_yandex_weather(lat, lon):
        url = "https://api.weather.yandex.ru/v2/forecast"
        params = {
            "lat": lat,
            "lon": lon,
        }
        headers = {
            "X-Yandex-API-Key": settings.YANDEX_API_KEY
        }
        try:
            response = requests.get(url=url, params=params, headers=headers)
            result = {
                "temp": response.json()["fact"]["temp"],
                "pressure_mm": response.json()["fact"]["pressure_mm"],
                "wind_speed": response.json()["fact"]["wind_speed"],
            }
            return result
        except Exception as e:
            print(f"Exception while getting Yandex weather: {e.args}")
            return None

    @staticmethod
    def _format_response(result, multiple=False):
        degree_sign = u'\N{DEGREE SIGN}'
        coordinates = ""
        if multiple:
            coordinates = f"({result['latitude']}, {result['longitude']})"

        return (f"Погода в г. {result['name']} {coordinates}:\n"
                f"Температура {result['weather']['temp']}{degree_sign}C\n"
                f"Давление {result['weather']['pressure_mm']} мм рт. ст.\n"
                f"Скорость ветра {result['weather']['wind_speed']} м/с.\n")

    def get(self, request):
        city = request.GET.get("city")
        if not city:
            return HttpResponse(f"Не передан параметр: city")

        city_formatted = city.lower().replace("-", " ").strip()
        city_queryset = models.City.objects.filter(formatted_name=city_formatted)

        results = []
        for city_obj in city_queryset:
            if city_obj.upd_time and timezone.now() - city_obj.upd_time < timedelta(minutes=30):
                print("Getting weather from cache")
                weather = {
                    "temp": city_obj.temp,
                    "pressure_mm": city_obj.pressure_mm,
                    "wind_speed": city_obj.wind_speed,
                }
            else:
                print("Getting weather from yandex")
                weather = self._get_yandex_weather(city_obj.latitude, city_obj.longitude)
                if weather:
                    city_obj.temp = weather["temp"]
                    city_obj.pressure_mm = weather["pressure_mm"]
                    city_obj.wind_speed = weather["wind_speed"]
                    city_obj.upd_time = timezone.now().strftime("%Y-%m-%d %H:%M")
                    city_obj.save()
                    print("Saved result to cache")

            if weather:
                results.append(
                    {
                        "name": city_obj.name,
                        "latitude": city_obj.latitude,
                        "longitude": city_obj.longitude,
                        "weather": weather,
                    }
                )

        if not results:
            return HttpResponse(f"Нет данных для города: {city}")
        if len(results) == 1:
            return HttpResponse(self._format_response(results[0]))

        multiple_cities = "\n".join([self._format_response(result, multiple=True) for result in results])
        return HttpResponse(f"Найдено несколько городов с названием {results[0]['name']}.\n\n{multiple_cities}")
