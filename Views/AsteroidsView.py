import tkinter as tk
from pubsub import pub
from tkinter import messagebox
from tkinter import ttk
from Setup import Layout_colors as colors


class AsteroidsView:
    def __init__(self, parent):
        self.__container = parent
        self.__width = int((parent.winfo_screenwidth() - 12) / 3)
        self.__height = int((parent.winfo_screenheight() / 7) * 5)

        # WIADOMOŚC Z NAGŁÓKA APLIKACJI Z INFORMACJĄ O ZMIANIE DATY
        pub.subscribe(self.upload_asteroids, "date_in_header_changed")

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def setup(self):
        """
        Metoda tworząca widok.
        """
        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        """
        Metoda zawiera inicjalizację komponentów widoku.
        """
        # FRAMES
        self.__main_frame = tk.LabelFrame(self.__container, text="Near Earth Objects", width=self.width,
                                          height=self.height, bg=colors.main_background_color,
                                          fg=colors.main_font_color, font=("Courier", 10))
        self.__top_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                    height=self.height / 10, bg=colors.main_background_color)
        self.__data_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                     height=(self.__height / 10) * 8, bg=colors.main_background_color)
        self.__bottom_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                       height=(self.__height / 12), bg=colors.main_background_color)

        # SCROLLABLE FRAME
        self.create_scrollable_frame_widgets()

        # LIST OF FRAMES TO DISPLAY
        self.__asteroids_frames = []

        # FILTER WIDGETS

        self.__sort_frame = tk.LabelFrame(self.__top_frame, text="Sort", bg=colors.main_background_color,
                                          fg=colors.main_font_color, font=("Courier", 10))
        self.__chosen_sort_option = tk.StringVar()
        self.__chosen_sort_option.set(3)
        self.__sort_options_radio_miss = tk.Radiobutton(self.__sort_frame, text="Miss dist.",
                                                        variable=self.__chosen_sort_option,
                                                        value=1, bg=colors.main_background_color,
                                                        fg=colors.button_color)
        self.__sort_options_radio_vel = tk.Radiobutton(self.__sort_frame, text="Velocity",
                                                       variable=self.__chosen_sort_option,
                                                       value=2, bg=colors.main_background_color,
                                                       fg=colors.button_color)
        self.__sort_options_radio_none = tk.Radiobutton(self.__sort_frame, text="None",
                                                        variable=self.__chosen_sort_option,
                                                        value=3, bg=colors.main_background_color,
                                                        fg=colors.button_color)
        self.__results_number_value = tk.StringVar()
        self.__results_number_picker = tk.Spinbox(self.__top_frame, from_=0, to=0, width=5,
                                                  textvariable=self.__results_number_value,
                                                  bg=colors.main_background_color,
                                                  fg=colors.button_color)

        self.__hazardous_checkbox_value = tk.IntVar()
        self.__hazardous_checkbox = tk.Checkbutton(self.__top_frame, text='hazardous',
                                                   variable=self.__hazardous_checkbox_value,
                                                   onvalue=1,
                                                   offvalue=0,
                                                   bg=colors.main_background_color,
                                                   fg=colors.button_color)

        # BUTTONS

        self.__save_txt_button = tk.Button(self.__bottom_frame, width=23, text="Save to .txt",
                                           command=lambda e='.txt': self.save_info_window_create(e),
                                           bg=colors.button_color, fg=colors.button_font_color)
        self.__save_json_button = tk.Button(self.__bottom_frame, width=23, text="Save to .json",
                                            command=lambda e='.json': self.save_info_window_create(e),
                                            bg=colors.button_color, fg=colors.button_font_color)
        self.__visualize_button = tk.Button(self.__bottom_frame, width=23, text="Visualize",
                                            command=self.visualize_asteroids, bg=colors.button_color,
                                            fg=colors.button_font_color)
        self.__apply_filters_button = tk.Button(self.__top_frame, text="Apply", width=23,
                                                command=self.asteroid_filters_changed, bg=colors.button_color,
                                                fg=colors.button_font_color)

    def setup_layout(self):
        """
        Metoda rozmieszcza komponenty widoku.
        """
        self.__main_frame.pack(side=tk.LEFT, anchor=tk.SW, padx=1, pady=1, ipadx=1, ipady=3)

        self.__main_frame.pack_propagate(0)

        self.__top_frame.pack(side=tk.TOP)
        self.__top_frame.pack_propagate(0)

        self.__sort_frame.pack(side=tk.LEFT)

        self.__sort_options_radio_miss.pack(side=tk.LEFT)
        self.__sort_options_radio_vel.pack(side=tk.LEFT)
        self.__sort_options_radio_none.pack(side=tk.LEFT)

        self.__results_number_picker.pack(side=tk.LEFT, padx=3, ipadx=3)
        self.__hazardous_checkbox.pack(side=tk.LEFT)

        self.__apply_filters_button.pack(side=tk.RIGHT)

        self.__data_frame.pack(side=tk.TOP)
        self.__data_frame.pack_propagate(0)

        self.__bottom_frame.pack(side=tk.TOP)
        self.__bottom_frame.pack_propagate(0)

        self.__save_txt_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.__save_json_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.__visualize_button.pack(side=tk.LEFT, padx=1, pady=1)

        self.setup_scrolled_frame()

    def create_scrollable_frame_widgets(self):
        """
        Metoda jest wywoływana w metodzie create_widgets. Inicjalizuje ona komponenty widoku przewijanej listy asteroid.
        """
        self.__sc_frame_w1 = tk.Frame(self.__data_frame, bg=colors.preview_backgorund_color)
        self.__sc_canvas = tk.Canvas(self.__sc_frame_w1, bg=colors.preview_backgorund_color)
        self.__yscrollbar = ttk.Scrollbar(self.__sc_frame_w1, orient='vertical', command=self.__sc_canvas.yview)
        self.__sc_frame = tk.Frame(self.__sc_canvas, bg=colors.preview_backgorund_color)

    def setup_scrolled_frame(self):
        """
        Metoda jest wywoływana w metodzie setup_layout. Umieszcza komponenty przewijanej listy asteroid w widoku.
        """
        self.__sc_canvas.pack(side=tk.LEFT, fill="both", expand="yes")
        self.__yscrollbar.pack(side=tk.RIGHT, fill="y")
        self.__sc_canvas.config(yscrollcommand=self.__yscrollbar.set)
        self.__sc_canvas.bind('<Configure>',
                              lambda e: self.__sc_canvas.config(scrollregion=self.__sc_canvas.bbox('all')))
        self.__sc_canvas.create_window((0, 0), window=self.__sc_frame, anchor="nw")
        self.__sc_frame_w1.pack(side=tk.TOP, fill="both", expand="yes")

    def visualize_asteroids(self):
        """
        Metoda jest wykonywana, kiedy zostanie użyty przycisk Visualize. Wysyła do kontrolera informację o potrzebie
        wizualizacji asteroid.
        """
        pub.sendMessage("visualize_asteroids")

    # KOMUNIKACJA Z WIDOK -> KONTROLER ( -> MODEL )
    def upload_asteroids(self, data):
        """
        Metoda jest wykonywana w przypadku zmiany aktualnej daty w nagłówku aplikacji, przy starcie programu wybraną
        datą jest aktualna. wysyła do kontrolera wiadomość o potrzebie pobrania danych dotycząych asteroid.
        """
        pub.sendMessage("upload_asteroids_list", data=data)

    def asteroid_filters_changed(self):
        """
        Metoda ta jest wykonywana w przypadku użycia przycisku Apply. Wysyła do kontrolera informację o zmianie filtrów
        wyświetlania asteroid w celu zaktualizowania aktualnie wyświetlanej listy. Wysyłaną informacją o filtrach jest
        krotka (wartość z checkboxa hazardous, wybrana opcja sortowania, liczba wyników do wyświetlenia)
        """
        pub.sendMessage("asteroids_filters_changed", data=(self.__hazardous_checkbox_value.get(),
                                                           int(self.__chosen_sort_option.get()),
                                                           int(self.__results_number_value.get())))

    # SAVING INFO
    def save_info(self, ext):
        """
        Metoda jest wykonywana gdy zostanie użyty przycisk "Save" w oknie zapisywania informacji po użyciu któregość
        z przycisków z grupy Save. Metoda wysyła do kontrolera wiadomość o potrzebie zapisania odpowiedniego pliku
        w zależności od rozszerzenia, jeśli nie została podana nazwa dla pliku, to zostaje wyświetlany komunikat
        niepowodzenia.
        """
        name = self.__file_name_entry.get()
        if name == "":
            messagebox.showerror("ERROR", "Give file name")
            pub.sendMessage("status_changed", data="Saving info ERROR.")
        else:
            if ext == ".txt":
                pub.sendMessage("save_asteroids_info_txt", data=name)
            elif ext == ".json":
                pub.sendMessage("save_asteroids_info_json", data=name)
        self.__file_name_entry_window.destroy()

    def save_info_window_create(self, ext):
        """
        Metoda tworzy okno zapisywania danych asteroid z wejściem, do którego należy wpisać nazwę pliku. W przypadku
        wciśnięcia przycisku "Save" zostaje wywołana metoda save_info z informacją  rozszerzeniu pliku,
        która wysyła odpowiednie informacje do kontrolera.
        :param ext Rozszerzenie zapisywanego pliku .json lub .txt
        """
        pub.sendMessage("status_changed", data="Saving asteroids info")
        self.__file_name_entry_window = tk.Toplevel(background=colors.main_background_color)
        self.__file_name_entry_window.title("Saving")
        self.__file_name_entry_window.wm_geometry("300x100")
        self.__entry_frame = tk.Frame(self.__file_name_entry_window, bg=colors.main_background_color)
        self.__file_name_entry = tk.Entry(self.__entry_frame)
        self.__entry_frame.pack(fill="none", expand=True)
        self.__file_name_entry.pack(side=tk.LEFT, fill="none", expand=True)
        tk.Button(self.__entry_frame, text="Save", command=lambda e=ext: self.save_info(e),
                  bg=colors.button_color, fg=colors.button_font_color).pack(side=tk.RIGHT, padx=5, pady=5)

    # KOMUNIKACJA Z ( MODEL -> ) KONTROLER -> WIDOK

    # UPDATE VIEW
    def destroy_asteroids_frames(self):
        """
        Metoda jest wywoływana w przypadku aktualizowania listy wyświetlanych asteroid. Niszczy aktualnie wyświetlane
        ramki z informacjami.
        """
        if len(self.__asteroids_frames) > 0:
            for frame in self.__asteroids_frames:
                frame.destroy()
        self.__asteroids_frames.clear()

    def update_asteroids_list(self, display_asteroids_data, from_model):
        """
        Metoda jest wywoływana w przypadku potrzeby aktualizacji listy wyświetlanych asteroid - w przypadku zmiany
        filtrów, lub daty w nagłówku. Konfiguruje ustawienia pickera liczby wyników w przypadku, jeśli
        dane sa aktualizowane z modelu, przy zmianie daty, niszczy aktualnie wyświetlane
        przez aplikację ramki a następnie dla każdej z asteroid w liście do wyświetlenia określa kolor wyświetlania
        na podstawie unformacji o poziomie ryzyka asteroidy i tworzy dla każdej asteroidy ramkę z pozyskanymi
        informacjami.
        :param display_asteroids_data: Lista asteroid do wyświetlenia w ramce.
        :param from_model: Wartość logiczna określająca, czy dane zostały zaktulizowane w modelu.
        """
        if from_model:
            self.__results_number_picker.config(to=len(display_asteroids_data))
            self.__results_number_value.set(str(len(display_asteroids_data)))
            self.__hazardous_checkbox_value.set(0)
            self.__chosen_sort_option.set(3)
        self.destroy_asteroids_frames()
        if display_asteroids_data:  # jeśli lista nie jest pusta
            for asteroid in display_asteroids_data:

                if asteroid.is_hazardous_asteroid:
                    act_text_color = colors.hazardous_asteroid_color
                else:
                    act_text_color = colors.main_font_color

                ast_fr = tk.LabelFrame(self.__sc_frame, text=asteroid.asteroid_name, bg=colors.main_background_color,
                                       fg=act_text_color, font=("Courier", 10))
                ast_fr.pack(side=tk.TOP, ipadx=3, ipady=3, padx=3, pady=3)
                label_hour = tk.Label(ast_fr, anchor=tk.W, text="Full date: " + asteroid.asteroid_approach_full_date,
                                      width=65, background=colors.main_background_color, foreground=act_text_color)
                label_velocity = tk.Label(ast_fr, anchor=tk.W, text="Velocity: " + asteroid.asteroid_velocity + " km/s",
                                          width=65, background=colors.main_background_color, foreground=act_text_color)
                label_miss_distance = tk.Label(ast_fr, anchor=tk.W, text="Miss distance: " +
                                                                         asteroid.asteroid_miss_distance_km +
                                                                         " km | "
                                                                         + asteroid.asteroid_miss_distance_au + " AU",
                                               width=65, background=colors.main_background_color,
                                               foreground=act_text_color)
                button_more_info = tk.Button(ast_fr, text="More info", bg=colors.button_color,
                                             fg=colors.button_font_color, command=lambda url=asteroid.asteroid_data_url:
                                             self.open_more_info_url(url))
                label_hour.pack(side=tk.TOP, ipadx=3, ipady=3, padx=3, pady=3)
                label_velocity.pack(side=tk.TOP, ipadx=3, ipady=3, padx=3, pady=3)
                label_miss_distance.pack(side=tk.TOP, ipadx=3, ipady=3, padx=3, pady=3)
                button_more_info.pack(side=tk.RIGHT, ipadx=3, ipady=3, padx=3, pady=3)

                self.__asteroids_frames.append(ast_fr)
            self.__sc_frame_w1.update()
            self.__sc_canvas.configure(scrollregion=self.__sc_canvas.bbox("all"))
            pub.sendMessage("status_changed", data="Updated Asteroids")
        else:
            pub.sendMessage("status_changed", data="No Asteroids data")

    def open_more_info_url(self, url):
        """
        Metoda zostaje wykonana, kiedy zostanie użyty przycisk "More info" przy którejś z asteroid. Wyśle do kontrolera
        informację o potrzebie otworzenia w oknie przeglądarki danego adresu URL asteroidy.
        :param url: Adres url do otworzenia w przeglądarce z większą ilością informacji o konkretnej asteroidzie.
        """
        pub.sendMessage("open_asteroid_more_info_url", data=url)

    def show_saving_error(self):
        """
        Metoda wywoływana jest jeśli zapisywanie pliku w kontrolerze nie powiedzie się. Wyświetla komunikat o
        niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="Asteroids info saving ERROR")
        messagebox.showerror("ERROR", "Saving APOD image ERROR")

    def show_opening_in_browser_error(self):
        """
        Metoda wywoływana jest jeśli otwieranie informacji o asteroidach w przeglądarce nie powiedzie się.
        Wyświetla komunikat o niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="Asteroid info opening in browser ERROR.")
        messagebox.showerror("ERROR", "Asteroid info image in browser ERROR")
