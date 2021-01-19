from Views import HeaderView
from pubsub import pub


class HeaderController:
    def __init__(self, parent):
        self.__parent = parent
        self.__view = HeaderView.HeaderView(parent)
        self.__view.setup()

        # WIADOMOŚCI Z WIDOKU
        pub.subscribe(self.picked_date, "picked_date")

        # PRZY STARCIE APLIKACJI WYBIERANA JEST DATA AKTUALNA
        self.picked_date(self.__view.actual_date)

    def picked_date(self, data):
        """
        Metoda jest wywoływana kiedy w widoku nagłówka wybierana jest data. Wysyła wiadomość do widoków o potrzebie
        zaktualizowania informacji.

        :param data: Wybrana data.
        """
        pub.sendMessage("date_in_header_changed", data=data)
