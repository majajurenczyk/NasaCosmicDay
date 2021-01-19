import nasapy as nasa
from Setup import ApiData
from pubsub import pub
from threading import Thread
import datetime


class Asteroid:
    """
    Jest klasą która modelującą dane jednej asteroidy
    """

    def __init__(self, name=None, url=None, is_hazardous=None, approach_full_date=None, velocity=None,
                 miss_distance_km=None, miss_distance_au=None, diameter=None):
        self.__asteroid_name = name
        self.__asteroid_data_url = url
        self.__is_hazardous_asteroid = is_hazardous
        self.__asteroid_approach_full_date = approach_full_date
        self.__asteroid_velocity = velocity  # km/s
        self.__asteroid_miss_distance_km = miss_distance_km
        self.__asteroid_miss_distance_au = miss_distance_au
        self.__asteroid_diameter = diameter

    def __str__(self):
        return "{name}\n{url}\n{haz}\n{date}\n" \
               "{vel}\n{miss_km}\n{miss_au}\n{dia}".format(name=self.__asteroid_name,
                                                           url=self.__asteroid_data_url,
                                                           haz=self.__is_hazardous_asteroid,
                                                           date=self.__asteroid_approach_full_date,
                                                           vel=self.__asteroid_velocity,
                                                           miss_km=self.__asteroid_miss_distance_km,
                                                           miss_au=self.asteroid_miss_distance_au,
                                                           dia=self.__asteroid_diameter
                                                           )

    @property
    def asteroid_name(self):
        return self.__asteroid_name

    @property
    def asteroid_data_url(self):
        return self.__asteroid_data_url

    @property
    def is_hazardous_asteroid(self):
        return self.__is_hazardous_asteroid

    @property
    def asteroid_approach_full_date(self):
        return self.__asteroid_approach_full_date

    @property
    def asteroid_velocity(self):
        return self.__asteroid_velocity

    @property
    def asteroid_miss_distance_km(self):
        return self.__asteroid_miss_distance_km

    @property
    def asteroid_miss_distance_au(self):
        return self.__asteroid_miss_distance_au

    @property
    def asteroid_diameter(self):
        return self.__asteroid_diameter


class AsteroidsData:
    """
    Jest klasą która modeluje dane asteroid uzyskane dzięku połączeniu z API NASA
    """

    def __init__(self, data_date=None, all_ast=None):
        self.__data_date = data_date
        if all_ast is None:
            self.__all_asteroids = []
        else:
            self.__all_asteroids = all_ast

    def __str__(self):
        return str(self.__all_asteroids)

    def add_asteroid(self, name, url, is_hazardous, approach_full_date, velocity,
                     miss_distance_km, miss_distance_au, diameter):
        self.__all_asteroids.append(
            Asteroid(name, url, is_hazardous, approach_full_date, velocity, miss_distance_km,
                     miss_distance_au, diameter))

    def add_data_date(self, date):
        self.__data_date = date

    def clear_asteroids(self):
        self.__all_asteroids = []

    @property
    def all_asteroids(self):
        return self.__all_asteroids

    @property
    def data_date(self):
        return self.__data_date


class AsteroidsModel:
    """
    Jest klasą dzięki której dane z API są pobierane i przechowywane.
    """

    def __init__(self):
        self.__model_data = AsteroidsData()
        self.__asteroids_fetched_data = {}

    def get_asteroid_data_with_request(self, data):
        """
        Metoda wykonywana jest z przypadku potrzeby zaktualizowania danych aplikacji, przy wybraniu daty. Tworzy nowy
        wątek w którym wysyłane jest żądanie HTTP w celu otrzymania potrzebnych informacji. Następnie sygnalizuje
        potrzebę zaktualizowania widoku.
        :param data: Dane dotyczące wybranej daty.
        """
        thread = Thread(target=self.get_asteroid_data_with_request_in_thread, args=(data,))
        thread.start()
        thread.join()
        pub.sendMessage("status_changed", data="Asteroids request received.")
        self.update_view()

    def get_asteroid_data_with_request_in_thread(self, asteroids_date):
        """
        Metoda wykonywana jest w przypadku potrzeby zaktualizowania danych aplikacji. Tworzy połączenie z API NASA oraz
        wysyła żądanie HTTP w celu otrzymania aktualnych informacji i aktualizuje te dane. Jeżeli uzyskanie informacji
        się nie powiedzie, zostają one ustawione jako None lub pustą listę w przypadku listy asteroid.
        :param asteroids_date: Dane dotyczące wybranej daty.
        """
        try:
            nasa_access = nasa.Nasa(key=ApiData.NASA_API_KEY)
            asteroids_data = nasa_access.asteroid_feed(start_date=asteroids_date, end_date=asteroids_date)

            self.__asteroids_fetched_data = asteroids_data

            asteroids_dict = asteroids_data["near_earth_objects"]  # tu jest słownik z datami
            asteroids_in_date = asteroids_dict[asteroids_date]  # słownik z asteroidami
            self.__model_data.add_data_date(asteroids_date)
            self.__model_data.clear_asteroids()
            for asteroid in asteroids_in_date:
                name = asteroid["name"]
                url = asteroid["nasa_jpl_url"]
                hazardous = asteroid["is_potentially_hazardous_asteroid"]
                date = asteroid["close_approach_data"][0]["close_approach_date_full"]
                date_datetime = datetime.datetime.strptime(date, '%Y-%b-%d %H:%M')
                date_datetime_str = date_datetime.strftime('%Y-%b-%d %H:%M')

                velocity = asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"]
                miss_au = asteroid["close_approach_data"][0]["miss_distance"]["astronomical"]
                miss_km = asteroid["close_approach_data"][0]["miss_distance"]["kilometers"]
                diameter = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
                self.__model_data.add_asteroid(name, url, hazardous, date_datetime_str, velocity, miss_km,
                                               miss_au, diameter)
        except Exception:
            self.__model_data = AsteroidsData()

    def update_view(self):
        """
        Metoda zostaje wywołana w przypadku zaktualizowania informacji. Wywołuje metody aktualizacji komponentów widoku.
        """
        self.update_asteroids_list()

    def update_asteroids_list(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o liście asteroid wyświetlanej w widoku.
        """
        pub.sendMessage("update_asteroids_list", data=self.__model_data.all_asteroids)

    def get_asteroids(self):
        return self.__model_data.all_asteroids  # lista obiektów astroida

    def get_date(self):
        return self.__model_data.data_date

    def get_fetched_asteroids_data(self):
        return self.__asteroids_fetched_data
