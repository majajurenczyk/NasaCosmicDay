from Controllers import AsteroidsController, HeaderController, ApodController, EarthController
import tkinter as tk
from pubsub import pub
from Setup import Layout_colors as colors


class MainView:
    def __init__(self):
        self.__main_win = tk.Tk()
        self.__main_win.config(background='grey21')
        self.__height = self.__main_win.winfo_screenwidth()
        self.__width = self.__main_win.winfo_screenheight()

        # INFORMACJE O ZMIANIE STATUSÓW
        pub.subscribe(self.status_changed, "status_changed")

    def create_widgets(self):
        """
        Metoda zawiera inicjalizację komponentów widoku.
        """
        self.__header_frame = tk.Frame(self.__main_win, bg=colors.main_background_color)
        self.__sections_frame = tk.Frame(self.__main_win, bg=colors.main_background_color)
        self.__statusbar = tk.Label(self.__main_win, text="Opening app..", anchor=tk.NW,
                                    width=self.__width, justify=tk.LEFT, background=colors.preview_backgorund_color,
                                    foreground=colors.main_font_color)

        # MENU CREATE
        self.__menubar = tk.Menu(self.__main_win)
        self.__main_win["menu"] = self.__menubar
        self.__help_menu = tk.Menu(self.__menubar)
        self.__help_menu.add_command(label="Astronomy picture of the day", underline=0, command=self.apod_help)
        self.__help_menu.add_command(label="Glimpse on Earth", underline=0, command=self.earth_help)
        self.__help_menu.add_command(label="Near Earth objects", underline=0, command=self.asteroids_help)
        self.__menubar.add_cascade(label="Help", menu=self.__help_menu, underline=0)

    def status_changed(self, data):
        """
        Metoda wywoływana jest w przypadku otrzymania informacji  zmianie statusu paska statusu
        :param data: Status
        """
        self.__statusbar.config(text=data)

    def setup_layout(self):
        """
        Metoda rozmieszcza komponenty widoku.
        """
        self.__header_frame.pack(side=tk.TOP)
        self.__sections_frame.pack(side=tk.TOP)

    def apod_help(self):
        """
        Metoda wykonywana jest w przypadku wybrania opcji Help oraz APOD w menu aplikacji, wywołuje metodę
        wyświetlającą pomoc dla tej części aplikacji.
        """
        self.show_help_window("Each day a different image or photograph of our fascinating universe is featured,\n"
                              "along with a brief explanation written by a professional astronomer.\n\n\n"
                              "Open in browser - opens image in your chrome browser\n"
                              "Show image - shows image in new window\n"
                              "Save image - saves image on your computer with given name."
                              )

    def earth_help(self):
        """
        Metoda wykonywana jest w przypadku wybrania opcji Help oraz Earth w menu aplikacji, wywołuje metodę
        wyświetlającą pomoc dla tej części aplikacji.
        """
        self.show_help_window("Each day a different image or photograph of our Earth is featured.\n"
                              "You can choose country that you want to see on satellite imageand photo\n"
                              "from focal point of the country, its latitude and logitude will be provided\n\n\n"
                              "Open in browser - opens satellite image in your chrome browser\n"
                              "Show image - shows satellite image in new window\n"
                              "Save image - saves satellite image on your computer with given name."
                              )

    def asteroids_help(self):
        """
        Metoda wykonywana jest w przypadku wybrania opcji Help oraz Asteroids w menu aplikacji, wywołuje metodę
        wyświetlającą pomoc dla tej części aplikacji.
        """
        self.show_help_window("Here you can see Asteroids that had their closest approach to Earth on picked day.\n"
                              "You can sort this asteroids by velocity, miss distance, choose number of results that\n"
                              "you want to see and choose to show only potentially dangerous for Earth asteroids.\n\n\n"
                              "Save to .txt - saves asteroid data to .txt file\n"
                              "Save to .json - saves asterois data to .json file\n"
                              "Visualize - visualize asteroids on chart showing their size and time of approach"
                              )

    def show_help_window(self, help_text):
        """
        Metoda jest wywoływana po wybraniu opcji help w menu. W zależności od wybranej podopcji wyświetla pomoc dla
        danej części aplikacji.
        :param help_text: Tekst pomocy dla danej części aplikacji
        :return:
        """
        help_window = tk.Toplevel(self.__main_win, background=colors.main_background_color)
        help_window.title("Help")
        tk.Label(help_window, text=help_text, justify=tk.LEFT, foreground=colors.main_font_color,
                 background=colors.main_background_color).pack()

    def setup_statusbar(self):
        """
        Metoda jest wywołana w celu umieszczenia paska statusu w aplikacji.
        """
        self.__statusbar.pack(side=tk.BOTTOM, anchor=tk.NW)

    def start_view(self):
        """
        Metoda ta wywoływana jest podczas startu aplikacji. Tworzy główne okno aplikacji, umieszcza w nim resztę
        widoków oraz uruchamia pętlę programu.
        """

        self.__main_win.geometry("%sx%s" % (self.__height,
                                            self.__width))
        self.__main_win.title("Cosmic day with NASA")
        self.create_widgets()
        self.setup_layout()

        apod_app = ApodController.ApodController(self.__sections_frame)
        earth_app = EarthController.EarthController(self.__sections_frame)
        asteroids_app = AsteroidsController.AsteroidsController(self.__sections_frame)
        header_app = HeaderController.HeaderController(self.__header_frame)

        self.setup_statusbar()
        self.__main_win.mainloop()
