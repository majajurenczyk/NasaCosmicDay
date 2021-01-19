from Models import EarthModel
from Views import EarthView
from pubsub import pub
import urllib.request
import webbrowser


class EarthController:
    def __init__(self, parent):
        self.__parent = parent
        self.__model = EarthModel.EarthModel()
        self.__view = EarthView.EarthView(parent)
        self.__view.setup()

        # WIADOMOŚCI Z MODELU
        pub.subscribe(self.model_earth_coordinates_changed, "update_earth_coordinates")
        pub.subscribe(self.model_earth_picture_changed, "update_pic_url")

        # WIADOMOŚCI Z WIDOKU
        pub.subscribe(self.upload_earth_data_pressed, "upload_earth_data")
        pub.subscribe(self.open_in_browser_pressed, "open_earth_in_browser_pressed")
        pub.subscribe(self.save_image_pressed, "save_earth_image")

    # WIADOMOŚCI Z WIDOKU
    def upload_earth_data_pressed(self, data):
        """
        Metoda wykonywana jest w przypadku otrzymania z widoku wiadomości o potrzebie zaktualizowania danych APOD.
        Wywołuje metodę modelu, pobierającą dane.
        :param data: Krotka (wybrana data, wybrane państwo)
        """
        self.__model.get_earth_data_with_request(data)

    def save_image_pressed(self, data):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie zapisania zdjęcia do pliku.
        Aktualny adres URL pobierany jest z danych w modelu i z niego pobierane jest zdjęcie. W przypadku niepowodzenia
        widok wyśwetla komunikat.
        :param data: Nazwa pliku, do jakiego ma zostać zapisane zdjęcie w formacie .jpg
        """
        try:
            urllib.request.urlretrieve(self.__model.get_data_url, data + ".jpg")
            pub.sendMessage("status_changed", data="Earth image saved...")
        except Exception:
            self.__view.show_saving_error()

    def open_in_browser_pressed(self):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie otworzenia zdjęcia w przeglądarce
        CHROME. Aktualny adres URL jest pobierany z modelu i otwierany w przeglądarce. W przypadku niepowodzenia widok
        wyświetla komunikat.
        """
        try:
            webbrowser.register('chrome', None,
                                webbrowser.BackgroundBrowser(
                                    "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
            webbrowser.get('chrome').open(self.__model.get_data_url)
            pub.sendMessage("status_changed", data="Earth image opened in browser.")
        except Exception:
            self.__view.show_opening_in_browser_error()

    # WIADOMOŚCI Z MODELU
    def model_earth_coordinates_changed(self, data):
        """
        Metoda jest wykonywana w momencie kiedy aktualne dane opisu zdjęcia Earth zostaną zaktualizowane i potrzebna
        jest także aktualizacja widoku.
        :param data: Zaktualizowany dane dotyczące współrzędnych geograficznych, krotka (latitude, longitude)
        """
        self.__view.update_coordinates(data)

    def model_earth_picture_changed(self, data):
        """
        Metoda jest wykonywana w momencie kiedy aktualne dane adresu URL zdjęcia Earth w pliku modelu zostaną
        zaktualizowane i potrzebna jest także aktualizacja widoku.
        :param data: Zaktualizowany adres url zdjęcia satelitarnego Earth.
        """
        self.__view.update_earth_pic(data)
