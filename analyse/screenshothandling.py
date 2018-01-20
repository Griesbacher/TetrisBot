import pyautogui

from areas import Areas


class ScreenshotHandler:
    def __init__(self):
        self._regions = dict()

    def register_region(self, area, region):
        # type: (Areas, tuple) -> None
        if len(region) != 4:
            raise ValueError("Region size is not 4, instead: %d" % len(region))
        self._regions[area] = region

    def take_screenshot(self, area):
        # type: (Areas) -> PIL.Image.Image
        return pyautogui.screenshot(region=self._regions[area])
