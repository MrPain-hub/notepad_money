from kivy.app import App
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from datetime import datetime
from calendar import monthrange


store = JsonStore("notepad_store.json")     # хранилище данных
number_day = 0


class CalendarScreen(Screen):
    """
    Основное меню с календарем
    """
    def on_enter(self):
        self.box_main = BoxLayout(orientation="vertical")
        self.add_widget(self.box_main)

        self.calendar_layout = GridLayout(cols=7)
        self.box_main.add_widget(self.calendar_layout)

        first_day_week = int(datetime(# определить первый день недели
            month=datetime.today().month,
            year=datetime.today().year,
            day=1
        ).strftime("%w"))

        """
        Создание надписи дня недели
        """
        for i in range(7):
            now_day_week = datetime(month=datetime.today().month,
                                    year=datetime.today().year,
                                    day=(8 - first_day_week) + i
                                    ).strftime("%a")
            txt = Label(text=now_day_week)
            self.calendar_layout.add_widget(txt)

        """
        Создание дней
        """
        days = monthrange(datetime.today().year,    # сколько дней в месяце
                      datetime.today().month
                      )[1]
        for i in range(days + first_day_week):
            day = i - first_day_week + 1
            box_day = BoxLayout()
            self.calendar_layout.add_widget(box_day)
            if day > 0:    # с какой итерации добавление кнопки дня
                date_key = f"{day}.{datetime.today().strftime('%d.%y')}"
                if date_key in store.store_keys():
                    day_txt = f"{day}\n({store.get(date_key)['money']})"
                else:
                    day_txt = str(day)
                button = Button(text=day_txt,
                                on_press=lambda x=day:
                                set_screen("day", int(x.text.split("\n")[0]))
                                )
                box_day.add_widget(button)

                if day == datetime.today().day:  # день сейчас
                    button.background_color = [0, 1, 0, 1]
    """
    def on_leave(self):  # Будет вызвана в момент закрытия экрана
        self.box_main.clear_widgets()  # очищаем список
    """


class DayScreen(Screen):

    def on_enter(self):
        root = RecycleView(size_hint=(1, None), size=(Window.width,
                                                      Window.height))
        self.add_widget(root)

        self.layout_day = GridLayout(cols=1, spacing=10, size_hint_y=None)
        root.add_widget(self.layout_day)

        date_now = f"{number_day} {datetime.today().strftime('%B %Y')}"
        self.date_key = f"{number_day}.{datetime.today().strftime('%d.%y')}"

        text_info = Label(text=date_now, size_hint_y=None, height=dp(40))
        self.layout_day.add_widget(text_info)

        """
        Чтение данных из хранилища
        """
        if self.date_key in store.store_keys():
            money_for_the_day = store.get(self.date_key)["money"]
            text_for_the_day = store.get(self.date_key)["text"]
        else:
            money_for_the_day = 0
            text_for_the_day = ""

        self.layout_day.add_widget(
            Label(text=f"потрачено: {money_for_the_day}")
        )

        self.text_input_day = TextInput(text=text_for_the_day,
                                        multiline=True,
                                        height=dp(500),
                                        size_hint_y=None,
                                        hint_text=f"Введите сумму"
                                        )
        self.layout_day.add_widget(self.text_input_day)

        btn_calendar = Button(text="назад",
                              size_hint_y=None,
                              height=dp(40),
                              on_press=lambda x: self.save_and_back("calendar")
                              )
        self.layout_day.add_widget(btn_calendar)

    def on_leave(self):  # Будет вызвана в момент закрытия экрана
        self.layout_day.clear_widgets()  # очищаем список

    def save_and_back(self, screen):
        """
        Сохранение в хранилище и выход
        """
        if self.text_input_day.text:
            all_sum = sum(self.filter_txt(self.text_input_day.text))
            store.put(self.date_key,
                      text=self.text_input_day.text,
                      money=all_sum
                      )
        elif self.date_key in store.store_keys():
            store.delete(self.date_key)
        SM.current = screen

    def filter_txt(self, txt):
        """
        Извлечь из текста цифры
            :param txt: на вход подается строка
            :return: массив состоящий из целых чисел list <int>
        """
        lst = txt.split()
        del_lst = set()
        for i in range(len(lst)):
            try:
                lst[i] = int(lst[i])
            except:
                del_lst.add(i)
        out = []
        for i in range(len(lst)):
            if i not in del_lst:
                out.append(lst[i])
        return out


class RunApp(App):
    def build(self):
        return SM


def set_screen(screen, n=0):
    """
    Переход на слайд и присваивание номера дня
    """
    global number_day
    number_day = n
    SM.current = screen


SM = ScreenManager()
SM.add_widget(CalendarScreen(name="calendar"))
SM.add_widget(DayScreen(name="day"))


if __name__ == "__main__":
    RunApp().run()
