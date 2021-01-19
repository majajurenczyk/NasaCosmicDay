import tkinter as tk
from pubsub import pub
from tkinter import messagebox
from tkinter import ttk
import pycountry
import datetime as dt
from PIL import ImageTk, Image
import urllib.request as ul
import io
from Setup import Layout_colors as colors


class EarthView:
    def __init__(self, parent):
        self.__container = parent
        self.__width = int((parent.winfo_screenwidth() - 12) / 3)
        self.__height = int((parent.winfo_screenheight() / 7) * 5)
        self.__countries_names = [country.name for country in pycountry.countries]  # lista państw
        self.__actual_date = dt.datetime.today().strftime("%Y-%m-%d")
        self.__act_country = tk.StringVar()

        # WIADOMOŚĆ Z NAGŁÓWKA APLIKACJI Z INFORMACJĄ O ZMIANIE DATY
        pub.subscribe(self.upload_earth_pic, "date_in_header_changed")

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
        self.__main_frame = tk.LabelFrame(self.__container, text="Glimpse on Earth", width=self.width,
                                          height=self.height, bg=colors.main_background_color,
                                          fg=colors.main_font_color, font=("Courier", 10))
        self.__top_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                    height=self.height / 10, bg=colors.main_background_color)
        self.__picture_frame = tk.LabelFrame(self.__main_frame, text="Photo preview", width=self.width,
                                             height=((self.__height / 10) * 4), bg=colors.preview_backgorund_color,
                                             fg=colors.main_font_color, font=("Courier", 10))
        self.__data_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                     height=((self.__height / 10) * 4), bg=colors.preview_backgorund_color)
        self.__bottom_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                       height=self.height / 12, bg=colors.main_background_color)

        self.__coordinates_frame = tk.Frame(self.__data_frame, bg=colors.preview_backgorund_color)

        # BUTTONS
        self.__upload_earth_pic_button = tk.Button(self.__top_frame, width=20, text="Upload Earth pic",
                                                   command=self.upload_earth_pic_country_changed,
                                                   bg=colors.button_color,
                                                   fg=colors.button_font_color
                                                   )

        self.__open_in_browser_button = tk.Button(self.__bottom_frame, width=23, text="Open in browser",
                                                  command=self.open_in_browser, bg=colors.button_color,
                                                  fg=colors.button_font_color)
        self.__upload_img_button = tk.Button(self.__bottom_frame, width=23, text="Show image",
                                             command=self.show_earth_image, bg=colors.button_color,
                                                  fg=colors.button_font_color)
        self.___save_img_button = tk.Button(self.__bottom_frame, width=23, text="Save image",
                                            command=self.save_image_window_create, bg=colors.button_color,
                                                  fg=colors.button_font_color)

        # IMAGE
        self.__img_mini_earth_label = tk.Label(self.__picture_frame, width=self.width,
                                               height=(int((self.__height / 10) * 3)),
                                               background=colors.main_background_color)

        # TEXT
        self.__latitude = tk.Text(self.__coordinates_frame, height=2, background=colors.preview_backgorund_color,
                                                        foreground=colors.main_font_color)
        self.__longtitude = tk.Text(self.__coordinates_frame, height=2, background=colors.preview_backgorund_color,
                                                        foreground=colors.main_font_color)

        # LABELS
        self.__latitude_label = tk.Label(self.__coordinates_frame, text="Latitude: ", font=("Courier", 12),
                                         background=colors.preview_backgorund_color, foreground=colors.main_font_color)
        self.__longitude_label = tk.Label(self.__coordinates_frame, text="Longitude: ", font=("Courier", 12),
                                          background=colors.preview_backgorund_color, foreground=colors.main_font_color)

        # COUNTRY COMBOBOX
        self.__drop_countries = ttk.Combobox(self.__top_frame, values=self.__countries_names,
                                             textvariable=self.__act_country,)
        self.__act_country.set(self.__countries_names[0])
        self.__drop_countries.current(0)

    def setup_layout(self):
        # FRAMES
        self.__main_frame.pack(side=tk.LEFT, anchor=tk.SW, padx=1, pady=1, ipadx=1, ipady=3)
        self.__main_frame.pack_propagate(0)

        self.__top_frame.pack(side=tk.TOP)
        self.__top_frame.pack_propagate(0)

        self.__picture_frame.pack(side=tk.TOP)
        self.__picture_frame.pack_propagate(0)

        self.__data_frame.pack(side=tk.TOP)
        self.__data_frame.pack_propagate(0)

        self.__coordinates_frame.pack(fill="none", expand=True)

        self.__bottom_frame.pack(side=tk.TOP)
        self.__bottom_frame.pack_propagate(0)

        # BUTTONS
        self.__upload_earth_pic_button.pack(side=tk.RIGHT)

        # COUNTRY COMBOBOX
        self.__drop_countries.pack(side=tk.LEFT)

        # LABELS
        self.__latitude_label.pack(side=tk.TOP)
        self.__latitude.pack(side=tk.TOP)
        self.__latitude.pack_propagate(0)

        self.__longitude_label.pack(side=tk.TOP)
        self.__longtitude.pack(side=tk.TOP)
        self.__longtitude.pack_propagate(0)

        # IMAGE
        self.__img_mini_earth_label.pack(fill="none", expand=True)

        # BUTTONS
        self.__open_in_browser_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.__upload_img_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.___save_img_button.pack(side=tk.LEFT, padx=1, pady=1)

    # KOMUNIKACJA Z WIDOK -> KONTROLER ( -> MODEL )

    def upload_earth_pic(self, data):
        """
        Metoda jest wykonywana w przypadku zmiany aktualnej daty w nagłówku aplikacji, przy starcie programu wybraną
        datą jest aktualna. Wysyła do kontrolera wiadomość o potrzebie pobrania danych dotycząych zdjęć satelitarnych
        ziemi przekazując informację o wybranym państwie oraz wybranej dacie, tymczasowo zachowuje aktualną datę.
        """
        self.enable_buttons()
        self.__actual_date = data
        if self.__act_country.get() is None:
            self.__act_country.set(self.__countries_names[0])
        pub.sendMessage("upload_earth_data", data=[self.__actual_date, self.__act_country.get()])

    def upload_earth_pic_country_changed(self):
        """
        Metoda jest wykonywana w przypadku zmiany aktualnego państwa, z nad którego pochodzą zdjęcia satelitarne, przy
        starcie programu wybranym państwiem jest pierwsze w liście państw. Metoda wysyła do kontrolera wiadomość o
        potrzebie pobrania nowych danych dotycząych zdjęć satelitarnych ziemi przekazując informację o wybranym państwie
        oraz wybranej dacie.
        """
        self.enable_buttons()
        pub.sendMessage("upload_earth_data", data=[self.__actual_date, self.__act_country.get()])

    def open_in_browser(self):
        """
        Metoda jest wykonywana, gdy zostanie użyty przycisk "Open in browser".Wysyła do kontrolera wiadomość o potrzebie
        otworzenia zdjęć satelitarnych w oknie przeglądarki.
        """
        pub.sendMessage("open_earth_in_browser_pressed")

    def save_image(self):
        """
        Metoda jest wykonywana gdy zostanie użyty przycisk "Save" w oknie zapisywania zdjęcia po użyciu "Save image".
        Metoda wysyła do kontrolera wiadomość o potrzebie zapisania zdjęcia satelitarnego, jeśli nie została podana
        nazwa dla zdjęcia, to zostaje wyświetlany komunikat niepowodzenia.
        """
        name = self.__file_name_entry.get()
        if name == "":
            messagebox.showerror("ERROR", "Give file name.")
            pub.sendMessage("status_changed", data="Saving Earth image ERROR.")
        else:
            pub.sendMessage("save_earth_image", data=name)
        self.__file_name_entry_window.destroy()

    def save_image_window_create(self):
        """
        Metoda tworzy okno zapisywania zdjęcia APOD z wejściem, do którego należy wpisać nazwę zdjęcia. W przypadku
        wciśnięcia przycisku "Save" zostaje wywołana metoda save_image, która wysyła odpowiednie informacje do
        kontrolera.
        """
        self.__file_name_entry_window = tk.Toplevel(background=colors.main_background_color)
        self.__file_name_entry_window.title("Saving")
        self.__file_name_entry_window.wm_geometry("300x100")
        self.__entry_frame = tk.Frame(self.__file_name_entry_window, bg=colors.main_background_color)
        self.__file_name_entry = tk.Entry(self.__entry_frame)
        self.__entry_frame.pack(fill="none", expand=True)
        self.__file_name_entry.pack(side=tk.LEFT, fill="none", expand=True)
        tk.Button(self.__entry_frame, text="Save", command=self.save_image, bg=colors.button_color,
                                                  fg=colors.button_font_color).pack(side=tk.RIGHT, padx=5, pady=5)

    # KOMUNIKACJA Z MODEL -> KONTROLER -> WIDOK

    # UPDATE VIEW
    def update_coordinates(self, data):
        """
        Metoda zostanie wykonana kiedy dane w modelu zostaną zaktualizowane i potrzebna jest również aktualizacja widoku
        Aktualizowane są informacje dotyczące współrzędnych geograficznych centralnego punktu wybranego państwa. Jeśli
        dane nie zostały dostarczone, to wyświetlana jest informacja "No data received"
        :param data: Krotka (latitude, longitude)
        """
        self.__latitude.delete(1.0, tk.END)
        self.__longtitude.delete(1.0, tk.END)
        if data[0] is not None:
            self.__latitude.insert(tk.END, data[0])
            self.__longtitude.insert(tk.END, data[1])
            pub.sendMessage("status_changed", data="Updated Earth data")
        else:
            self.__latitude.insert(tk.END, "No data received")
            self.__longtitude.insert(tk.END, "No data received")
            pub.sendMessage("status_changed", data="No Earth data")

    def update_earth_pic(self, data):
        """
        Metoda jest wywoływana kiedy informacje w modelu zostaną zaktualizowane i potrzebna jest również aktualizacja
        widoku. Zapisywany jest aktualny adres url obrazka satelitarnego na podstawie którego aktualizowana jest
        jego miniaturka. Jeśli dane nie zostaną dostarczone adres URL staje się pusty.

        :param data: zawiera informację o aktualnym adresie URL zdjęcia satelitarnego z modelu.
        """
        if data is not None:
            self.__img_url = data
            self.update_mini_picture()
            pub.sendMessage("status_changed", data="Updated Earth data")
        else:
            self.__img_url = ""
            self.__img_mini_earth_label.image = None
            self.__img_mini_earth_label.config(image=None)
            self.disable_buttons()
            pub.sendMessage("status_changed", data="No Earth data")

    def disable_buttons(self):
        """
        Metoda wykonywana jest jeśli nie dostaną dostarczone dane z modelu, wprowadza przyciski w stan nieaktywny.
        """
        if self.___save_img_button["state"] == tk.NORMAL:
            self.___save_img_button.config(state=tk.DISABLED)

        if self.__upload_img_button["state"] == tk.NORMAL:
            self.__upload_img_button.config(state=tk.DISABLED)

        if self.__open_in_browser_button["state"] == tk.NORMAL:
            self.__open_in_browser_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        """
        Metoda jest wykonywana kiedy dostarczone zostaną dane z modelu, wprowadza przyciski w stan aktywny.
        """
        if self.___save_img_button["state"] == tk.DISABLED:
            self.___save_img_button.config(state=tk.NORMAL)

        if self.__upload_img_button["state"] == tk.DISABLED:
            self.__upload_img_button.config(state=tk.NORMAL)

        if self.__open_in_browser_button["state"] == tk.DISABLED:
            self.__open_in_browser_button.config(state=tk.NORMAL)

    def update_mini_picture(self):
        """
        Metoda jest wywoływana w momencie aktualizowania widoku w przypadku zmiany adresu URL zdjęcia. Jeśli otrzymano
        adres url zdjęcie jest skalowane do odpowiednich rozmiarów, a następnie aktualizowane.
        """
        raw_data = ul.urlopen(self.__img_url).read()
        img = Image.open(io.BytesIO(raw_data))

        width, height = img.size

        lab_size = ((self.__height / 10) * 4)

        scale_height = height / lab_size
        scale_width = width / lab_size

        if scale_height > scale_width:
            scale = scale_height
        else:
            scale = scale_width

        img_resized = img.resize((int(width / scale), int(height / scale)), Image.ANTIALIAS)

        img_tk = ImageTk.PhotoImage(img_resized)
        self.__img_mini_earth_label.image = img_tk
        self.__img_mini_earth_label.config(image=img_tk, width=int(width / scale), height=int(height / scale))

    def show_saving_error(self):
        """
        Metoda wywoływana jest jeśli zapisywanie zdjęcia w kontrolerze nie powiedzie się. Wyświetla komunikat o
        niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="Earth image saving ERROR")
        messagebox.showerror("ERROR", "Saving Earth image ERROR")


    def show_opening_in_browser_error(self):
        """
        Metoda wywoływana jest jeśli otwieranie zdjęcia w przeglądarce nie powiedzie się. Wyświetla komunikat o
        niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="Earth image opening in browser ERROR.")
        messagebox.showerror("ERROR", "Opening Earth image in browser ERROR")

    def show_earth_image(self):
        """
        Metoda jest wykonywana w przypadku użycia przycisku "Show image". Tworzy nowe okno aplikacji, w którym zostaje
        umieszczony odpowiednio przeskalowany obrazek. Jeżeli obrazka nie uda się otworzyć pokazywany jest komunikat
        niepowodzenia.
        """
        try:
            self.__img_window = tk.Toplevel(self.__container)
            self.__img_apod_label = tk.Label(self.__img_window)
            raw_data = ul.urlopen(self.__img_url).read()
            img = Image.open(io.BytesIO(raw_data))
            width, height = img.size
            scale_height = height / (self.height * 7 / 5)
            scale_width = width / (self.width * 3)

            if scale_height > scale_width:
                scale = scale_height
            else:
                scale = scale_width

            img_resized = img.resize((int(width / scale), int(height / scale)), Image.ANTIALIAS)
            self.__img_window.title('LANDSAT photo')
            self.__img_apod_label.pack()
            img_tk = ImageTk.PhotoImage(img_resized)
            self.__img_apod_label.image = img_tk
            self.__img_apod_label.config(image=img_tk)
            pub.sendMessage("status_changed", data="Earth image opened in new window.")
        except Exception:
            messagebox.showerror("ERROR", "Uploading image ERROR")
            pub.sendMessage("status_changed", data="Opening Earth image in new window ERROR.")
