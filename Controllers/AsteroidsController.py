from bokeh.models import ColumnDataSource, LabelSet, TapTool, OpenURL, Label
from bokeh.plotting import figure, output_file, show
from Models import AsteroidsModel
from Views import AsteroidsView
from pubsub import pub
import webbrowser
import datetime
import json


class AsteroidsController:
    def __init__(self, parent):
        self.__parent = parent
        self.__model = AsteroidsModel.AsteroidsModel()
        self.__view = AsteroidsView.AsteroidsView(parent)
        self.__view.setup()

        # WIADOMOŚCI Z MODELU
        pub.subscribe(self.model_asteroids_list_changed, "update_asteroids_list")

        # WIADOMOŚCI Z WIDOKU
        pub.subscribe(self.upload_asteroids_pressed, "upload_asteroids_list")
        pub.subscribe(self.update_astreoids_with_filters, "asteroids_filters_changed")
        pub.subscribe(self.open_more_info_url, "open_asteroid_more_info_url")
        pub.subscribe(self.visualize_asteroids_pressed, "visualize_asteroids")
        pub.subscribe(self.save_asteroids_data_to_txt, "save_asteroids_info_txt")
        pub.subscribe(self.save_asteroids_data_to_json, "save_asteroids_info_json")

    # WIADOMOŚCI Z WIDOKU

    def upload_asteroids_pressed(self, data):
        """
        Metoda wykonywana jest w przypadku otrzymania z widoku wiadomości o potrzebie zaktualizowania danych asteroid.
        Wywołuje metodę modelu, pobierającą dane.
        :param data: Data, która została zaktualizowana w widoku.
        """
        self.__model.get_asteroid_data_with_request(data)

    def visualize_asteroids_pressed(self):
        """
        Metoda tworzy wizualizację asteroid na podstawie ich rozmiaru, odległości w jakiej minęły Ziemię i godziny
        zbliżenia. Wykres generowany jest z wykorzystaniem biblioteki bokeh do pliku html oraz wyświetlany.
        Metoda jest wykonywana w przypadku użycia przycisku Visualize w widoku.
        """
        # WIZUALIZACJA BOKEH
        asteroids = self.__model.get_asteroids()

        # NAZWY DLA ASTEROID NA WIZUALIZACJI
        asteroids_names = [asteroid.asteroid_name + "{:.2f}".format(asteroid.asteroid_diameter) + "KM WIDE"
                           for asteroid in asteroids]
        asteroids_names.append('Moon')  # DLA PORÓWNANIA

        x_axis = [datetime.datetime.strptime(asteroid.asteroid_approach_full_date, '%Y-%b-%d %H:%M') for
                  asteroid in asteroids]  # NA OSI X CZAS MINIĘCIA ZIEMI PRZEZ ASTEROIDĘ
        act_date = self.__model.get_date()

        # KSIĘŻYC USTAWIANY JEST DOMYŚLNIE NA 5:00
        x_axis.append(datetime.datetime.strptime(act_date + " 5:00", '%Y-%m-%d %H:%M'))

        y_axis = [float(asteroid.asteroid_miss_distance_km) for asteroid in asteroids]  # NA OSI Y ODLEGŁOŚĆ MINIĘCIA
        y_axis.append(384472)  # ODLEGŁOŚC KSIĘŻYCA OD ZIEMI W KILOMETRACH

        asteroid_sizes = [float(asteroid.asteroid_diameter) for asteroid in asteroids]  # ROZMIARY ASTEROID
        size_on_chart = [size * 1e7 for size in asteroid_sizes]  # WZGLĘDNY ROZMIAR ASTEROIDY JEST OKREŚLANY PRZEZ
        # PROMIEŃ JEJ KOŁA
        # ROZMIAR JEST SKALOWANY * MILION, ABY BY ASTEROIDY BYŁY WIDOCZNE NA WYKRESIE MIMO ŻE OŚ Y MA MILIONY KM

        size_on_chart.append(1e6)  # KSIĘŻYC JEST DUŻO WIĘKSZY OD ASTEROID, ROZMIAR NIE MA ZNACZENIA, KSIEZYC
        # POKAZUJE TYLKO ODLEGŁOŚĆ OD ZIEMI

        urls = [asteroid.asteroid_data_url for asteroid in asteroids]  # ADRESY URL ASTEROID (TE CO W MORE INFO )
        urls.append('https://moon.nasa.gov/')  # STRONA KSIĘŻYCA NASA

        colors = []
        min_distance = min(y_axis)
        max_distance = max(y_axis)
        range_distance = max_distance - min_distance
        for (name, distance) in zip(asteroids_names, y_axis):  # ZWRACA KROTKE (NAZWA ODLEGŁOŚĆ) DLA KAZDYCH
            # ODPOWIADAJACYCH SOBIE ELEMENTOW
            if name == 'Moon':
                colors.append('#0000FF')  # KSIĘŻYC JEST NIEBIESKI
            elif distance == min_distance:
                colors.append("#%02x%02x%02x" % (255, 0, 0))  # #RRGGBB Z KROTKI RGB
            elif distance == max_distance:
                colors.append("#%02x%02x%02x" % (0, 255, 0))

            else:
                distance_change = (distance - min_distance) / range_distance
                color_change = int(distance_change * 450)
                if color_change > 255:
                    colors.append("#%02x%02x%02x" % (0, color_change - 255, 0))
                else:
                    colors.append("#%02x%02x%02x" % (255 - color_change, 0, 0))

        # ŹRÓDŁO DANYCH DLA WYKRESU
        data_source = ColumnDataSource(data=dict(hours=x_axis,
                                                 distance=y_axis,
                                                 names=asteroids_names,
                                                 size_on_chart=size_on_chart,
                                                 colors=colors,
                                                 url=urls))

        # KOMPONENT WYKRESU DO WYRENDEROWANIA WIZUALIZACJI W PLIKU HTML
        chart = Label(x=850, y=70, x_units='screen', y_units='screen',
                      text='Data From NASA NeoW API', render_mode='css',
                      border_line_color='black', border_line_alpha=0.7,
                      background_fill_color='white', background_fill_alpha=0.7)

        # NOTATKA KTÓRA POWIE, ILE RAZY WIĘKSZY JEST KSIĘŻYC OD NAJWIĘKSZEJ ASTEROIDY NA WYKRESIE
        max_size = max(asteroid_sizes)
        scale = " {:.2f}".format(3474.2 / max_size)  # 3474.2 TO ROZMIAR KSIĘŻYCA W KILOMETRACH

        # KOMPONENT NOTATKI POROWNUJACEJ WIELKOSC KSIEZYCA
        moon_comparing_note = Label(x=150, y=30, x_units='screen', y_units='screen',
                                    text='Moon is ' + scale + ' x larger than largest asteroid on chart.',
                                    render_mode='css',
                                    border_line_color='black', border_line_alpha=0.7,
                                    background_fill_color='white', background_fill_alpha=0.7, text_font_size="10pt")

        # GENEROWANIE WIZUALIZACJI DO PLIKU HTML
        output_file("asteroids_today.html", title="Asteroids", mode="cdn")  # Bokeh js from cdn

        TOOLS = "pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,tap"
        # UTWORZENIE POLA WYKRESU
        plot = figure(tools=TOOLS, x_axis_type="datetime", plot_width=1400, height=650,
                      x_axis_label="Hours After Midnight",
                      y_axis_label="Miles From Earth", title="Asteroids today")
        plot.circle(x="hours", y="distance", source=data_source, radius="size_on_chart", fill_color="colors",
                    fill_alpha=0.6, line_color='black')

        # ETYKIETY DLA DANYCH
        labels = LabelSet(x='hours', y='distance', text='names', source=data_source, text_font_size='9pt')

        # DODANIE LAYOUTU
        plot.add_layout(labels)
        plot.add_layout(chart)
        plot.add_layout(moon_comparing_note)

        # KIEDY ASTEROIDA ZOSTANIE KLINIETA, W PRZEGLADARCE OTWORZY SIE WIĘCEJ INFORMACJI O NIEJ
        taptool = plot.select(type=TapTool)
        taptool.callback = OpenURL(url="@url")

        # WYŚWIETLENIE WYKRESU
        show(plot)
        pub.sendMessage("status_changed", data="Asteroids info visualized")

    # ZAPISYWANIE DO PLIKU
    def save_asteroids_data_to_txt(self, data):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie zapisania zdjęcia do pliku .txt.
        W przypadku niepowodzenia widok wyśwetla komunikat.
        :param data: Nazwa pliku, do jakiego mają zostać zapisane dane w formacie .txt
        """
        file_name = data + ".txt"
        try:
            with open(file_name, 'w') as out_file:
                out_file.write(str(self.__model.get_fetched_asteroids_data()))
                pub.sendMessage("status_changed", data="Asteroids info saved to .txt")
        except IOError:
            self.__view.show_saving_error()

    def save_asteroids_data_to_json(self, data):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie zapisania zdjęcia do pliku .json.
        W przypadku niepowodzenia widok wyśwetla komunikat.
        :param data: Nazwa pliku, do jakiego mają zostać zapisane dane w formacie .json
        """
        file_name = data + ".json"
        try:
            with open(file_name, 'w') as out_file:
                json.dump(self.__model.get_fetched_asteroids_data(), out_file)
                pub.sendMessage("status_changed", data="Asteroids info saved to .json")
        except IOError:
            self.__view.show_saving_error()

    # SORTOWANIE I FILTROWANIE
    def sort_by_miss_distance_chosen(self, asteroids_list):  # 1
        """
        Metoda jest wykonywana w przypadku wybrania sortowania po Miss distance.
        :param asteroids_list: lista asteroid do posortowania
        :return: lista posortowanych według odległości zbliżenia asteroid
        """
        return sorted(asteroids_list, key=lambda a: a.asteroid_miss_distance_km)

    def sort_by_velocity_chosen(self, asteroids_list):  # 2
        """
        Metoda jest wykonywana w przypadku wybrania sortowania po Velocity.
        :param asteroids_list: lista asteroid do posortowania
        :return: lista posortowanych według prędkości asteroidy przy zbliżeniu
        """
        return sorted(asteroids_list, key=lambda a: a.asteroid_velocity)

    def number_of_results_chosen(self, asteroids_list, number_of_results):
        """
        Metoda jest wykonywana kiedy zmieniają się filtry wyświetlania asteroid, wybiera z listy asteroid tylko
        początkową liczbę elementów, określoną w filtrze.
        :param asteroids_list: lista asteroid do modyfikacji
        :param number_of_results: liczba wyników w liście asteroid
        :return: lista asteroid ze zmodyfikowaną ich liczbą
        """
        return asteroids_list[:number_of_results]

    def only_hazardous_asteroids(self, asteroids_list):
        """
        Metoda jest wykonywana kiedy zmieniają się filtry wyświetlania asteroid, wybiera z listy asteroid tylko
        te, które są potencjalnym zagrożeniem dla Ziemi.
        :param asteroids_list: lista asteroid do modyfikacji
        :return: lista asteroid będących potencjalnym zagrożeniem dla Ziemi
        """
        return [asteroid for asteroid in asteroids_list if asteroid.is_hazardous_asteroid]

    def open_more_info_url(self, data):
        """
        Metoda jest wykonywana w przypadku otrzymania z widoku informacji o potrzebie otworzenia informacji o asteroidzie
        w przeglądarce CHROME. Aktualny adres URL informacji jest pobierany z modelu i otwierany w przeglądarce.
        W przypadku niepowodzenia widok wyświetla komunikat.
        """
        try:
            webbrowser.register('chrome', None,
                                webbrowser.BackgroundBrowser(
                                    "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
            webbrowser.get('chrome').open(data)
            pub.sendMessage("status_changed", data="Asteroids more info opened in browser.")
        except Exception:
            self.__view.show_opening_in_browser_error()

    def update_astreoids_with_filters(self, data):  # data = (hazardous, sort, number)
        """
        Aktualizuje dane dotyczące wyświetlanych asteroid w momencie, kiedy zmienione zostają filtry wyświetlania.
        Stosuje wybrane filtry oraz wysyła przefiltrowaną listę do widoku w celu zaktualizowania widoku.
        :param data: Informacje o filtrach, krotka
        (wartość z checkboxa hazardous, wybrana opcja sortowania, liczba wyników do wyświetlenia)
        """
        print(data)
        filtered_asteroids = self.__model.get_asteroids()
        print(filtered_asteroids)
        if data[0] == 1:
            filtered_asteroids = self.only_hazardous_asteroids(filtered_asteroids)
        if data[1] == 1:
            filtered_asteroids = self.sort_by_miss_distance_chosen(filtered_asteroids)
        if data[1] == 2:
            filtered_asteroids = self.sort_by_velocity_chosen(filtered_asteroids)

        filtered_asteroids = self.number_of_results_chosen(filtered_asteroids, data[2])
        self.__view.update_asteroids_list(filtered_asteroids, False)

    # WIADOMOŚCI Z MODELU
    def model_asteroids_list_changed(self, data):
        """
        Aktualizuje dane dotyczące wyświetlanych asteroid w momencie zmiany danych w modelu.
        :param data: lista asteroid do wyświetlenia
        """
        self.__view.update_asteroids_list(self.__model.get_asteroids(), True)
