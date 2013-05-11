import sys

import curses
import colors

import gevent
import gevent.monkey

from image import CurseImage
import instagram
import process

gevent.monkey.patch_all(thread=False)

def main():
    Application().run()

class Application(object):
    def run(self):
        try:
            # TODO: Provide better logging mechanism
            sys.stdout = open('log.txt', 'a', 0)
            curses.wrapper(self._run)
        finally:
            sys.stdout = sys.__stdout__

    def _run(self, screen):
        curses.curs_set(0)
        curses.mousemask(1)

        screen.nodelay(1)

        colors.init(screen)

        page = WelcomePage()

        self._main_loop(screen, page)

    def _main_loop(self, screen, page):
        while page:
            screen.clear()
            screen.refresh()
            page = page.run(screen)

class Page(object):
    pass

class WelcomePage(Page):
    def run(self, screen):
        logo = CurseImage.from_file('extras/logo.txt')

        self.animate_logo(screen, logo)

        _getch(screen)

        return PopularPage()

    def animate_logo(self, screen, logo):
        height, width = screen.getmaxyx()

        x = width / 2 - logo.width / 2
        y_center =  height / 2 - logo.height / 2 - 1
        y_start = 0

        while y_start < y_center:
            screen.clear()

            logo.draw(screen, y_start, x)

            y_start += 1
            screen.refresh()
            gevent.sleep(seconds=0.05)

        addstr_centered(screen, y_center + logo.height + 1, "PRESS ANY KEY")

        screen.refresh()


class PopularPage(Page):
    def run(self, screen):
        gevent.spawn(self._fetch_images).join()

        height, width = screen.getmaxyx()
        image = process.get_image(self.images[0].low_res['url'], width, height)
        image.draw(screen, 0, 0)
        screen.refresh()

        while True:
            c = _getch(screen)

    def _fetch_images(self):
        self.images = instagram.popular()


def addstr_centered(screen, y, text):
    height, width = screen.getmaxyx()
    x = width / 2 - len(text) / 2
    screen.addstr(y, x, text)

def _getch(screen):
    gevent.socket.wait_read(sys.stdin.fileno())
    return screen.getch()

if __name__ == '__main__':
    main()
