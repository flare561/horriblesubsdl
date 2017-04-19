from npyscreen import Form, TitleText, TitleFilename, TitleMultiSelect,\
                      TitleSelectOne, FixedText, npyssafewrapper, notify 
from npyscreen.wgwidget import EXITED_ESCAPE
from transmissionrpc import Client as tClient
from .external import fetch_episodes, add_torrents


class TorrentFinderForm(Form):
    def __init__(self, download_dir, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.directory_widget.value = download_dir

    def create(self):
        self.name = "HorribleSubs Batch Downloader"
        self.search_widget = self.add(TitleText, name="Search:")
        self.resolution_widget = self.add(
                TitleSelectOne, max_height=4, value=[1],
                name="Resolution:", values=["480", "720", "1080"],
                scroll_exit=True
                )

        self.directory_widget = self.add(
                TitleFilename, name="Download Dir:",
                value=''
                )

        self.episodes_widget = self.add(
                TitleMultiSelect, max_height=-2, value=[],
                name="Episodes:", values=[], scroll_exit=True
                )

        self.add(FixedText, value="Press Ctrl-A to select all, "
                                  "Ctrl-D to select none, "
                                  "or Escape to quit")
        self.how_exited_handers[EXITED_ESCAPE] = self.cancel
        self.add_handlers({
            "^A": self.select_all,
            "^D": self.select_none
        })
        self.search_text = ""
        self.selected_resolution = "720"
        self.available_episodes = {}
        self.cancelled = False

    @property
    def directory(self):
        if self.directory_widget.value:
            return self.directory_widget.value
        else:
            return None

    @property
    def episodes(self):
        return self.available_episodes

    @episodes.setter
    def episodes(self, value):
        self.available_episodes = value
        self.episodes_widget.values = list(value.keys())
        self.episodes_widget.value = []
        self.episodes_widget.update()

    @property
    def search(self):
        return self.search_widget.value

    @property
    def resolution(self):
        return self.resolution_widget.get_selected_objects()[0]

    @property
    def downloads(self):
        try:
            if not self.cancelled:
                return {key: self.available_episodes[key] for key in
                        self.episodes_widget.get_selected_objects()}
        except TypeError:
            pass
        return {}

    def select_all(self, key):
        self.episodes_widget.value = list(range(len(
            self.available_episodes.keys())))
        self.episodes_widget.update()

    def select_none(self, key):
        self.episodes_widget.value = []
        self.episodes_widget.update()

    def cancel(self):
        self.cancelled = True
        self.exit_editing()

    def while_editing(self, current_widget):
        if (self.search_text != self.search or
                self.selected_resolution != self.resolution):
            notify("Getting episodes", title="Busy")
            self.search_text = self.search
            self.selected_resolution = self.resolution
            self.episodes = fetch_episodes(self.search_text, self.resolution)

    def edit(self):
        self.cancelled = False
        super().edit()
        return (self.downloads, self.directory)

def main():
    def runform(*args, **kwargs):
        tclient = tClient('localhost', 9091)
        tform = TorrentFinderForm(tclient.session.download_dir)
        torrents, download_dir = tform.edit()
        add_torrents(tclient, torrents, download_dir)

    npyssafewrapper.wrapper(runform)

if __name__ == "__main__":
    main()
