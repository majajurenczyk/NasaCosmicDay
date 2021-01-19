from pubsub import pub
from Setup import ApiData
from geopy.geocoders import Nominatim
import requests
import datetime
from threading import Thread


class EarthData:
    """
    Jest klasą która modeluje dane Earth uzyskane dzięku połączeniu z API NASA
    """

    def __init__(self, name=None, lat=None, lon=None, url=None, date=None):
        self.__country_name = name
        self.__latitude = lat
        self.__longitude = lon
        self.__pic_url = url
        self.__pic_date = date

    @property
    def country_name(self):
        return self.__country_name

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    @property
    def pic_url(self):
        return self.__pic_url


class EarthModel:
    """
    Jest klasą dzięki której dane z API są pobierane i przechowywane.
    """

    def __init__(self):
        self.__earth_data = EarthData()  # OBIEKT EARTH DATA ZAWIERAJĄCY AKTUALNE INFORMACJE

    @staticmethod
    def convert_country_to_coordinates(country_name):
        """
        Metoda zamienia nazwę państwa na współrzędne geograficzne jego centralnego punktu.
        :param country_name: Nazwa państwa
        :return: Krotka (latitude, longitude) będąca współrzędnymi geograficznymi centralnego punktu państwa
        """
        geolocator = Nominatim(user_agent="CosmicDay")
        location = geolocator.geocode(country_name)
        return location.latitude, location.longitude

    def get_earth_data_with_request(self, data):
        """
        Metoda wykonywana jest z przypadku potrzeby zaktualizowania danych aplikacji, przy wybraniu daty lub państwa.
        Tworzy nowy wątek w którym wysyłane jest żądanie HTTP w celu otrzymania potrzebnych informacji.
        Następnie sygnalizuje potrzebę zaktualizowania widoku.
        :param data: Krotka z danymi (wybrana data, wybrane państwo)
        """
        thread = Thread(target=self.get_earth_data_with_request_in_thread, args=(data,))
        thread.start()
        thread.join()
        pub.sendMessage("status_changed", data="Earth request received.")
        self.update_view()

    def get_earth_data_with_request_in_thread(self, data):  # data[0] = date, data[1] = country name
        """
        Metoda wykonywana jest w przypadku potrzeby zaktualizowania danych aplikacji. Tworzy połączenie z API NASA oraz
        wysyła żądanie HTTP w celu otrzymania aktualnych informacji i aktualizuje te dane. Ponieważ nie dla każdego dnia
        dostępne są zdjęcia satelitarne, to wysyłane są żądania o informacje dla z poprzedniego miesiąca aż do momentu
        uzyskania najbliższych wymaganym informacji. Jeżeli uzyskanie informacji się nie powiedzie, zostają one
        ustawione jako None.
        :param data: Krotka z danymi (wybrana data, wybrane państwo)
        """
        try:
            location = self.convert_country_to_coordinates(data[1])
            latitude = location[0]
            longitude = location[1]

            lat_round = float(int(location[0] * 10)) / 10
            lon_round = float(int(location[1] * 10)) / 10

            request_params = {'api_key': ApiData.NASA_API_KEY, 'lat': lat_round, 'lon': lon_round, 'dim': 0.2,
                              'date': data[0]}
            request_response = requests.get(ApiData.ENDPOINT_URL, request_params)
            request_data_json = request_response.json()

            datetime_obj = datetime.datetime.strptime(data[0], "%Y-%m-%d")
            counter = 0
            if 'msg' in request_data_json:
                while 'msg' in request_data_json and counter <= 30:
                    datetime_obj = datetime_obj - datetime.timedelta(days=1)
                    request_params = {'api_key': ApiData.NASA_API_KEY, 'lat': latitude, 'lon': longitude,
                                      'date': datetime_obj.strftime("%Y-%m-%d")}
                    request_response = requests.get(ApiData.ENDPOINT_URL, request_params)
                    request_data_json = request_response.json()
                    counter += 1
            if counter != 30:
                requested_url = request_data_json['url']
                self.__earth_data = EarthData(name=data[1], lat=latitude, lon=longitude, date=data[0],
                                              url=requested_url)
            else:
                self.__earth_data = EarthData()

        except Exception:
            self.__earth_data = EarthData()

    def update_view(self):
        """
        Metoda zostaje wywołana w przypadku zaktualizowania informacji. Wywołuje metody aktualizacji komponentów widoku.
        """
        self.update_url()
        self.update_coordinates()

    def update_coordinates(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o aktualnych współrzędnych geograficznych państwa.
        """
        pub.sendMessage("update_earth_coordinates", data=[self.__earth_data.latitude, self.__earth_data.longitude])

    def update_url(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o adresie URL zdjęcia satelitarnego Earth w widoku
        """
        pub.sendMessage("update_pic_url", data=self.__earth_data.pic_url)

    @property
    def get_data_url(self):
        return self.__earth_data.pic_url
