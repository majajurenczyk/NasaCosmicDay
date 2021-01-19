import tkinter as tk
import datetime as dt
from tkcalendar import Calendar
from pubsub import pub
from PIL import ImageTk, Image
from Setup import Layout_colors as colors


class HeaderView:
    def __init__(self, parent):
        self.__container = parent
        self.__width = int(parent.winfo_screenwidth())
        self.__height = int((parent.winfo_screenheight() / 6))
        self.__actual_date = dt.datetime.today().strftime("%Y-%m-%d")  # AKTUALNA DATA

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def actual_date(self):
        return self.__actual_date

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
        self.__main_frame = tk.Frame(self.__container, width=self.width,
                                     height=self.height, bg=colors.main_background_color)
        self.__header_label = tk.Label(self.__main_frame, text="YOUR COSMIC DAY: ", font=("Courier", 30),
                                       background=colors.main_background_color, foreground=colors.main_font_color)

        datetime_obj = dt.datetime.strptime(self.__actual_date, "%Y-%m-%d")
        self.__header_date = tk.Label(self.__main_frame, text=datetime_obj.strftime('%a %d. of %B %Y'),
                                      font=("Courier", 30), background=colors.main_background_color,
                                      foreground=colors.main_font_color)
        self.__pick_date_button = tk.Button(self.__main_frame, width=15, height=2, text="PICK DAY",
                                            command=self.change_date_window_open, font=("Courier", 15),
                                            bg=colors.button_color, fg=colors.button_font_color)

        self.__img_logo_nasa = tk.Label(self.__main_frame, background=colors.main_background_color)

    def setup_layout(self):
        """
        Metoda rozmieszcza komponenty widoku.
        """
        self.load_nasa_logo()
        self.__main_frame.pack(side=tk.LEFT)
        self.__main_frame.pack_propagate(0)
        self.__header_label.pack(side=tk.LEFT)
        self.__header_label.pack_propagate(0)
        self.__header_date.pack(side=tk.LEFT)
        self.__header_date.pack_propagate(0)
        self.__pick_date_button.pack(side=tk.RIGHT, padx=10, pady=10, ipadx=10, ipady=10)

    def change_date_window_open(self):
        """
        Metoda tworzy i otwiera okno wybierania daty z kalendarzem. Wykonywana jest w momencie użycia przycisku
        pick date w nagłówku.
        """
        today = dt.date.today()
        self.__pick_date_window = tk.Toplevel(background=colors.main_background_color)
        self.__calendar = Calendar(self.__pick_date_window, font="Arial 14", maxdate=today, selectmode='day',
                                   cursor="hand1", year=int(today.year), month=int(today.month), day=int(today.day))
        accept_date = tk.Button(self.__pick_date_window, text="Accept", command=self.accept_changed_date,
                                bg=colors.button_color, fg=colors.button_font_color, width=30)
        self.__calendar.pack(fill="both", expand=True)
        accept_date.pack()

    def accept_changed_date(self):
        """
        Metoda jest wywoływana w przypadku użycia przycisku Accept w oknie wyboru daty. Zmienia aktualną datę w widoku
        oraz wysyła do kontrolera informację o zmianie daty.
        """
        self.__actual_date = str(self.__calendar.selection_get())
        datetime_obj = dt.datetime.strptime(self.__actual_date, "%Y-%m-%d")
        self.__header_date.config(text=datetime_obj.strftime('%a %d. of %B %Y'))
        self.__pick_date_window.destroy()
        pub.sendMessage("picked_date", data=self.__actual_date)

    def load_nasa_logo(self):
        """
        Metoda wczytuje zdjęcie logo nasa z pliku, i umieszcza go w nagłówku.
        """
        self.__img_logo_nasa.pack(side=tk.LEFT, padx=1, pady=1, ipady=1, ipadx=3)
        img = Image.open('nasa_logo.png')
        resized_img = img.resize((140, 125), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(resized_img)
        self.__img_logo_nasa.image = img_tk
        self.__img_logo_nasa.config(image=img_tk, width=140, height=125)
