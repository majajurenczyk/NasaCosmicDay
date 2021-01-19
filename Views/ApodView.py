import tkinter as tk
from pubsub import pub
from PIL import ImageTk, Image
import urllib.request as ul
import io
from tkinter import messagebox
import tkinter.scrolledtext as st
from Setup import Layout_colors as colors


class ApodView:
    def __init__(self, parent):
        self.__container = parent
        self.__width = int((parent.winfo_screenwidth() - 12) / 3)
        self.__height = int((parent.winfo_screenheight() / 7) * 5)

        # WIADOMOŚĆ Z NAGŁÓWKA APLIKACJI Z INFORMACJĄ O ZMIANIE DATY
        pub.subscribe(self.upload_apod, "date_in_header_changed")

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
        self.__main_frame = tk.LabelFrame(self.__container, text="Astronomy picture of the day", width=self.width,
                                          height=self.height, bg=colors.main_background_color,
                                          fg=colors.main_font_color, font=("Courier", 10))
        self.__top_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                    height=self.height / 10, bg=colors.main_background_color)
        self.__picture_frame = tk.LabelFrame(self.__main_frame, text="Photo preview", width=self.width,
                                             height=((self.__height / 10) * 4), bg=colors.preview_backgorund_color,
                                             fg=colors.main_font_color, font=("Courier", 10))
        self.__data_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                     height=((self.__height / 10) * 4), bg=colors.main_background_color)
        self.__bottom_frame = tk.Frame(self.__main_frame, highlightbackground="Black", width=self.__width,
                                       height=self.height / 12, bg=colors.main_background_color)

        # LABELS
        self.__label_title = tk.Label(self.__top_frame, text="Label", font=("Courier", 12),
                                      background=colors.main_background_color, foreground=colors.main_font_color)

        # BUTTONS
        self.__open_in_browser_button = tk.Button(self.__bottom_frame, width=23, text="Open in browser",
                                                  command=self.open_in_browser, bg=colors.button_color,
                                                  fg=colors.button_font_color)
        self.__upload_img_button = tk.Button(self.__bottom_frame, width=23, text="Show image",
                                             command=self.show_apod_image, bg=colors.button_color,
                                             fg=colors.button_font_color)
        self.___save_img_button = tk.Button(self.__bottom_frame, width=23, text="Save image",
                                            command=self.save_image_window_create, bg=colors.button_color,
                                            fg=colors.button_font_color)

        # IMAGE
        self.__img_mini_apod_label = tk.Label(self.__picture_frame, width=self.width,
                                              height=(int((self.__height / 10) * 3)),
                                              background=colors.main_background_color)

        # SCROLLED TEXT
        self.__pic_desc_scroller_text = st.ScrolledText(self.__data_frame, background=colors.preview_backgorund_color,
                                                        foreground=colors.main_font_color)
        self.__pic_desc_scroller_text.config(state=tk.DISABLED)

    def setup_layout(self):
        """
        Metoda rozmieszcza komponenty widoku.
        """
        # FRAMES
        self.__main_frame.pack(side=tk.LEFT, padx=1, pady=1, ipadx=1, ipady=3)
        self.__main_frame.pack_propagate(0)

        self.__top_frame.pack(side=tk.TOP)
        self.__top_frame.pack_propagate(0)

        self.__picture_frame.pack(side=tk.TOP)
        self.__picture_frame.pack_propagate(0)

        self.__data_frame.pack(side=tk.TOP)
        self.__data_frame.pack_propagate(0)

        self.__bottom_frame.pack(side=tk.TOP)
        self.__bottom_frame.pack_propagate(0)

        # LABELS
        self.__label_title.pack(side=tk.LEFT)

        # SCROLLED TEXT
        self.__pic_desc_scroller_text.pack(side=tk.TOP)

        # IMAGE
        self.__img_mini_apod_label.pack(fill="none", expand=True)

        # BUTTONS
        self.__open_in_browser_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.__upload_img_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.___save_img_button.pack(side=tk.LEFT, padx=1, pady=1)

    # KOMUNIKACJA Z WIDOK -> KONTROLER ( -> MODEL )

    def upload_apod(self, data):
        """
        Metoda jest wykonywana w przypadku zmiany aktualnej daty w nagłówku aplikacji, przy starcie programu wybraną
        datą jest aktualna. wysyła do kontrolera wiadomość o potrzebie pobrania danych dotycząych APOD.
        """
        pub.sendMessage("upload_apod", data=data)

    def open_in_browser(self):
        """
        Metoda jest wykonywana, gdy zostanie użyty przycisk "Open in browser".Wysyła do kontrolera wiadomość o potrzebie
        otworzenia zdjęcia APOD w oknie przeglądarki.
        """
        pub.sendMessage("open_apod_in_browser_pressed")

    def save_image(self):
        """
        Metoda jest wykonywana gdy zostanie użyty przycisk "Save" w oknie zapisywania zdjęcia po użyciu "Save image".
        Metoda wysyła do kontrolera wiadomość o potrzebie zapisania zdjęcia APOD, jeśli nie została podana nazwa dla
        zdjęcia, to zostaje wyświetlany komunikat niepowodzenia.
        """
        name = self.__file_name_entry.get()
        if name == "":
            messagebox.showerror("ERROR", "Give file name")
            pub.sendMessage("status_changed", data="Saving APOD image ERROR.")
        else:
            pub.sendMessage("save_apod_image", data=name)
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

    # AKTUALIZACJA WIDOKU
    def update_url(self, apod_data):
        """
        Metoda jest wywoływana kiedy informacje w modelu zostaną zaktualizowane i potrzebna jest również aktualizacja
        widoku. Zapisywany jest aktualny adres url obrazka na podstawie którego aktualizowana jest miniaturka obrazka.
        Jeśli dane nie zostaną dostarczone adres URL staje się pusty.

        :param apod_data: zawiera informację o aktualnym adresie URL zdjęcia z modelu.
        """
        if apod_data is not None:
            self.enable_buttons()
            self.__img_url = apod_data
            self.update_mini_picture()
            pub.sendMessage("status_changed", data="Updated APOD")
        else:
            self.__img_url = ""
            self.__img_mini_apod_label.image = None
            self.__img_mini_apod_label.config(image=None)
            self.disable_buttons()
            pub.sendMessage("status_changed", data="No APOD data")

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

    def update_desc(self, apod_data):
        """
        Metoda jest wywoływana kiedy informacje w modelu zostaną zaktualizowane i potrzebna jest również aktualizacja
        widoku. W widoku aktualizowany jest komponent wyświetlający opis zdjęcia. Jeśli dane nie zostały dostarczone,
        to opis jest pusty.
        :param apod_data: zawiera informację o aktualnym opisie zdjęcia z modelu.
        """
        self.__pic_desc_scroller_text.config(state=tk.NORMAL)
        self.__pic_desc_scroller_text.delete(1.0, tk.END)
        if apod_data is not None:
            self.__pic_desc_scroller_text.insert(tk.END, apod_data)
            self.__pic_desc_scroller_text.config(state=tk.DISABLED)
            pub.sendMessage("status_changed", data="Updated APOD")
        else:
            pub.sendMessage("status_changed", data="No APOD data")

    def update_title(self, apod_data):
        """
        Metoda jest wywoływana kiedy informacje w modelu zostaną zaktualizowane i potrzebna jest również aktualizacja
        widoku. W widoku aktualizowany jest komponent wyświetlający zapisywany tytuł zdjęcia. Jeśli dane nie zostały
        dostarczone to wyświetlane jest "No data received"
        :param apod_data: zawiera informację o aktualnym opisie zdjęcia z modelu.
        """
        if apod_data is not None:
            self.__img_title = apod_data
            pub.sendMessage("status_changed", data="Updated APOD.")
        else:
            self.__img_title = "No data received"
            pub.sendMessage("status_changed", data="No APOD data")
        self.__label_title.config(text=self.__img_title)


    def update_mini_picture(self):
        """
        Metoda jest wywoływana w momencie aktualizowania widoku w przypadku zmiany adresu URL zdjęcia. Zdjęcie jest
        skalowane do odpowiednich rozmiarów, a następnie aktualizowane.
        """
        raw_data = ul.urlopen(self.__img_url).read()
        img = Image.open(io.BytesIO(raw_data))

        width, height = img.size  # SKALOWANIE

        expected_size = ((self.__height / 10) * 4)

        scale_height = height / expected_size
        scale_width = width / expected_size

        if scale_height > scale_width:
            scale = scale_height
        else:
            scale = scale_width

        img_resized = img.resize((int(width / scale), int(height / scale)), Image.ANTIALIAS)

        img_tk = ImageTk.PhotoImage(img_resized)
        self.__img_mini_apod_label.image = img_tk
        self.__img_mini_apod_label.config(image=img_tk, width=int(width / scale), height=int(height / scale))

    def show_saving_error(self):
        """
        Metoda wywoływana jest jeśli zapisywanie zdjęcia w kontrolerze nie powiedzie się. Wyświetla komunikat o
        niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="APOD image saving ERROR")
        messagebox.showerror("ERROR", "Saving APOD image ERROR")

    def show_opening_in_browser_error(self):
        """
        Metoda wywoływana jest jeśli otwieranie zdjęcia w przeglądarce nie powiedzie się. Wyświetla komunikat o
        niepowodzeniu.
        """
        pub.sendMessage("status_changed", data="APOD image opening in browser ERROR.")
        messagebox.showerror("ERROR", "Opening APOD image in browser ERROR")

    # POKAZYWANI ZDJĘCIA W NOWYM OKNIE
    def show_apod_image(self):
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

            scale_height = height / (self.height * 7 / 5)  # SKALOWANIE
            scale_width = width / (self.width * 3)

            if scale_height > scale_width:
                scale = scale_height
            else:
                scale = scale_width

            img_resized = img.resize((int(width / scale), int(height / scale)), Image.ANTIALIAS)

            self.__img_window.title(self.__img_title)
            self.__img_apod_label.pack()
            img_tk = ImageTk.PhotoImage(img_resized)
            self.__img_apod_label.image = img_tk
            self.__img_apod_label.config(image=img_tk)
            pub.sendMessage("status_changed", data="APOD image opened in new window.")
        except Exception:
            pub.sendMessage("status_changed", data="Opening APOD image in new window ERROR")
            messagebox.showerror("ERROR", "Uploading APOD image in new window ERROR")
