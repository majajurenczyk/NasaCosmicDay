from Models import ApodModel
from Views import ApodView
from pubsub import pub
import webbrowser
import urllib.request


class ApodController:
    def __init__(self, parent):
        self.__parent = parent
        self.__model = ApodModel.ApodModel()
        self.__view = ApodView.ApodView(parent)
        self.__view.setup()

        # WIADOMOŚCI Z WIDOKU
        pub.subscribe(self.upload_apod_pressed, "upload_apod")
        pub.subscribe(self.open_in_browser_pressed, "open_apod_in_browser_pressed")
        pub.subscribe(self.save_image_pressed, "save_apod_image")

        # WIADOMOŚCI Z MODELU
        pub.subscribe(self.model_url_apod_changed, "update_url_apod")
        pub.subscribe(self.model_desc_apod_changed, "update_desc_apod")
        pub.subscribe(self.model_title_apod_changed, "update_title_apod")

    # WIADOMOŚCI Z WIDOKU
    def upload_apod_pressed(self, data):
        """
        Metoda wykonywana jest w przypadku otrzymania z widoku wiadomości o potrzebie zaktualizowania danych APOD.
        Wywołuje metodę modelu, pobierającą dane.
        :param data: Data, która została zaktualizowana w widoku.
        """
        self.__model.get_apod_data_with_request(data)

    def save_image_pressed(self, data):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie zapisania zdjęcia do pliku.
        Aktualny adres URL pobierany jest z danych w modelu i z niego pobierane jest zdjęcie. W przypadku niepowodzenia
        widok wyśwetla komunikat.
        :param data: Nazwa pliku, do jakiego ma zostać zapisane zdjęcie w formacie .jpg
        """
        try:
            urllib.request.urlretrieve(self.__model.get_data_url, data + ".jpg")
            pub.sendMessage("status_changed", data="APOD image saved")
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
            pub.sendMessage("status_changed", data="APOD image opened in browser")
        except Exception:
            self.__view.show_opening_in_browser_error()

    # WIADOMOŚCI Z MODELU
    def model_url_apod_changed(self, data):
        """
        Metoda jest wykonywana w momencie kiedy aktualne dane adresu URL w pliku modelu zostaną zaktualizowane
        i potrzebna jest także aktualizacja widoku.
        :param data: Zaktualizowany adres url zdjęcia APOD.
        """
        self.__view.update_url(data)

    def model_desc_apod_changed(self, data):
        """
        Metoda jest wykonywana w momencie kiedy aktualne dane opisu zdjęcia APOd zostaną zaktualizowane i potrzebna jest
        także aktualizacja widoku.
        :param data: Zaktualizowany opis zdjęcia APOD
        :return:
        """
        self.__view.update_desc(data)

    def model_title_apod_changed(self, data):
        """
        Metoda jest wykonywana w momencie kiedy aktualne dane tytułu zdjęcia APOd zostaną zaktualizowane i potrzebna jest
        także aktualizacja widoku.
        :param data: Zaktualizowany tytuł zdjęcia APOD
        :return:
        """
        self.__view.update_title(data)
