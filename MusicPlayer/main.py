import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.core.audio import SoundLoader
from kivy.utils import platform

# Если запускаем на Android, запрашиваем доступ к памяти
if platform == 'android':
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


class MusicPlayer(App):
    def build(self):
        self.playlist = []
        self.index = -1
        self.sound = None

        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Начальный путь для Android — корень памяти, для ПК — текущая папка
        init_path = "/sdcard" if platform == 'android' else os.getcwd()

        self.chooser = FileChooserListView(path=init_path, filters=['*.mp3', '*.wav'])
        self.root.add_widget(self.chooser)

        self.info = Label(text="Выбери папку и нажми Load", size_hint_y=None, height=50)
        self.root.add_widget(self.info)

        ctrl = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_prev = Button(text="<<", on_release=self.prev)
        self.btn_play = Button(text="Play", on_release=self.toggle)
        btn_next = Button(text=">>", on_release=self.next)
        btn_load = Button(text="Load", on_release=self.load)

        for b in [btn_prev, self.btn_play, btn_next, btn_load]:
            ctrl.add_widget(b)

        self.root.add_widget(ctrl)
        return self.root

    def load(self, *args):
        path = self.chooser.path
        self.playlist = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav'))]
        if self.playlist:
            self.index = 0
            self.info.text = f"Треков в списке: {len(self.playlist)}"
        else:
            self.info.text = "Музыка не найдена в этой папке"

    def play_track(self):
        if self.sound:
            self.sound.stop()
            self.sound.unload()

        if 0 <= self.index < len(self.playlist):
            track = self.playlist[self.index]
            self.sound = SoundLoader.load(track)
            if self.sound:
                self.sound.play()
                self.btn_play.text = "Pause"
                self.info.text = os.path.basename(track)
                self.sound.bind(on_stop=self.auto_next)

    def auto_next(self, instance):
        # Если трек доиграл до конца (а не был остановлен кнопкой)
        if self.sound and self.sound.get_pos() >= self.sound.length - 1:
            self.next()

    def toggle(self, *args):
        if not self.sound and self.playlist:
            self.play_track()
        elif self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.btn_play.text = "Play"
            else:
                self.sound.play()
                self.btn_play.text = "Pause"

    def next(self, *args):
        if self.playlist:
            self.index = (self.index + 1) % len(self.playlist)
            self.play_track()

    def prev(self, *args):
        if self.playlist:
            self.index = (self.index - 1) % len(self.playlist)
            self.play_track()


if __name__ == '__main__':
    MusicPlayer().run()