from pubsub import pub
import nasapy as nasa
from Setup import ApiData
from threading import Thread


class ApodData:
    """
    Jest klasą która modeluje dane APOD uzyskane dzięku połączeniu z API NASA
    """

    def __init__(self, apod_url=None, apod_desc=None,
                 apod_title=None, apod_date=None):
        self.__apod_url = apod_url
        self.__apod_desc = apod_desc
        self.__apod_title = apod_title
        self.__apod_date = apod_date

    @property
    def url(self):
        return self.__apod_url

    @property
    def desc(self):
        return self.__apod_desc

    @property
    def title(self):
        return self.__apod_title

    @property
    def date(self):
        return self.__apod_date


class ApodModel:
    """
    Jest klasą dzięki której dane z API są pobierane i przechowywane.
    """

    def __init__(self):
        self.__model_data = ApodData()  # OBIEKT APOD DATA ZAWIERAJĄCY AKTUALNE INFORMACJE

    def get_apod_data_with_request(self, data):
        """
        Metoda wykonywana jest z przypadku potrzeby zaktualizowania danych aplikacji, przy wybraniu daty. Tworzy nowy
        wątek w którym wysyłane jest żądanie HTTP w celu otrzymania potrzebnych informacji. Następnie sygnalizuje
        potrzebę zaktualizowania widoku.
        :param data: Dane dotyczące wybranej daty.
        """
        thread = Thread(target=self.get_apod_data_with_request_in_thread, args=(data,))
        thread.start()
        thread.join()
        self.update_view()

    def get_apod_data_with_request_in_thread(self, data):
        """
        Metoda wykonywana jest w przypadku potrzeby zaktualizowania danych aplikacji. Tworzy połączenie z API NASA oraz
        wysyła żądanie HTTP w celu otrzymania aktualnych informacji i aktualizuje te dane. Jeżeli uzyskanie informacji
        się nie powiedzie, zostają one ustawione jako None.
        :param data: Dane dotyczące wybranej daty.
        """
        try:
            nasa_access = nasa.Nasa(key=ApiData.NASA_API_KEY)
            pic_data_dict = nasa_access.picture_of_the_day(data, hd=True)
            self.__model_data = ApodData(pic_data_dict['hdurl'], pic_data_dict['explanation'],
                                         pic_data_dict['title'], pic_data_dict['date'])
        except Exception:
            self.__model_data = ApodData()

    def update_view(self):
        """
        Metoda zostaje wywołana w przypadku zaktualizowania informacji. Wywołuje metody aktualizacji komponentów widoku.
        """
        self.update_url_apod()
        self.update_description_apod()
        self.update_title_apod()

    def update_url_apod(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o adresie URL zdjęcia APOD w widoku
        """
        pub.sendMessage("update_url_apod", data=self.__model_data.url)

    def update_description_apod(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o opisie zdjęcia APOD w widoku
        """
        pub.sendMessage("update_desc_apod", data=self.__model_data.desc)

    def update_title_apod(self):
        """
        Metoda zostaje wykonana w metodzie update_view. Wysyła komunikat do kontrolera o potrzebie zaktualizowania
        informacji o tytule zdjęcia APOD w widoku
        """
        pub.sendMessage("update_title_apod", data=self.__model_data.title)

    @property
    def get_data_url(self):
        return self.__model_data.url
