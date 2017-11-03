import atexit
import enum
import logging

from queue import Empty, Queue
from threading import Condition, Thread

from . import _wkhtmltopdf

#: Represents a missing value on a field.
Missing = object()


class ConversionError(Exception):
    """Raised on conversion failure.
    """


class ColorMode(enum.Enum):
    """The supported color modes.
    """

    COLOR = "Color"
    GRAYSCALE = "Grayscale"


class Orientation(enum.Enum):
    """The supported orientations.
    """

    LANDSCAPE = "Landscape"
    PORTRAIT = "Portrait"


class PageSize(enum.Enum):
    """The supported page sizes.
    """

    A3 = "A3"
    A4 = "A4"
    A5 = "A5"


def generate_pdf(
        output_filename,
        source_uri=None,
        source_html=None,
        page_size=PageSize.A4,
        orientation=Orientation.PORTRAIT,
        color_mode=ColorMode.COLOR,
        width=None,
        height=None,
        margin_top=None,
        margin_right=None,
        margin_bottom=None,
        margin_left=None,
        image_dpi=600,
        image_quality=94,
        zoom=1,
):
    """Generate a PDF file from an HTML string or a URI.

    Parameters:
      output_filename(str): The path where the PDF should be saved.
      source_uri(str): The URI to generate the PDF from.
      source_html(str): A blob of HTML to generate the PDF from.
      page_size(PageSize): The size of the generated page.
      orientation(Orientation): The PDF's orientation.
      color_mode(ColorMode): The PDF's color mode.
      width(str): The width of the document. e.g. "4cm".
      height(str): The height of the document. e.g. "12in".
      margin_top(str): The size of the top margin.
      margin_right(str): The size of the right margin.
      margin_bottom(str): The size of the bottom margin.
      margin_left(str): The size of the left margin.
      image_dpi(int): Defaults to 600.
      image_quality(int): Defaults to 94.
      zoom(float): Defaults to 1.

    Returns:
      Task: A value representing the async conversion process.
    """
    assert source_uri or source_html, \
        "You must provide either a source_uri or a source_html."

    global_settings = {
        "size.pageSize": page_size.value,
        "size.width": width,
        "size.height": height,
        "orientation": orientation.value,
        "colorMode": color_mode.value,
        "dpi": image_dpi,
        "imageQuality": image_quality,
        "margin.top": margin_top,
        "margin.right": margin_right,
        "margin.bottom": margin_bottom,
        "margin.left": margin_left,
        "out": output_filename,
    }

    object_settings = {
        "load.zoomFactor": zoom,
        "page": source_uri,
    }

    return _convert(
        _convert_args(global_settings),
        _convert_args(object_settings),
        source_html,
    )


class _Task(object):
    """Represents an HTML -> PDF conversion task.

    Parameters:
      global_settings(dict[str, str])
      object_settings(dict[str, str])
      source(str)
    """

    def __init__(self, global_settings, object_settings, source):
        self.global_settings = global_settings
        self.object_settings = object_settings
        self.source = source

        self._condition = Condition()
        self._exception = Missing
        self._result = Missing

    def result(self, timeout=None):
        if self._exception is not Missing:
            raise self._exception

        if self._result is not Missing:
            return self._result

        with self._condition:
            self._condition.wait(timeout=timeout)
            if self._exception is not Missing:
                raise self._exception
            return self._result

    def set_exception(self, exception):
        with self._condition:
            self._exception = exception
            self._condition.notify_all()

    def set_result(self, result):
        with self._condition:
            self._result = result
            self._condition.notify_all()

    def __repr__(self):
        return f"Task({self.global_settings!r}, {self.object_settings!r})"


class _Converter(Thread):
    """Serializes HTML -> PDF conversion tasks onto a single POSIX
    thread.  This is required as wkhtmltopdf isn't thread safe.
    """

    def __init__(self):
        super().__init__(daemon=True)

        self.logger = logging.getLogger("h2p.Converter")
        self.work = Queue()
        self.start()

    def run(self):
        # We have to initialize the Qt main loop in this thread
        # otherwise it'll just spin idly in the main thread.
        self.logger.debug("Booting up converter thread...")
        self.logger.debug("Initializing wkhtmltopdf main loop...")
        _wkhtmltopdf.init(0)

        try:
            self.running = True
            while self.running:
                try:
                    task = self.work.get(timeout=1)

                    try:
                        self.logger.debug("Converting %r...", task)
                        res = _wkhtmltopdf.convert(
                            task.global_settings,
                            task.object_settings,
                            task.source,
                        )

                        self.logger.debug("Finished converting %r.", task)
                        if res:
                            task.set_result(res)
                        else:
                            task.set_exception(ConversionError())
                    except Exception as exc:
                        self.logger.warning("Failed to convert %r.", task, exc_info=True)
                        task.set_exception(exc)
                except Empty:
                    continue
        finally:
            _wkhtmltopdf.deinit()

    def stop(self):
        self.running = False
        self.join()

    def submit(self, task):
        self.work.put(task)


_converter = _Converter()
atexit.register(_converter.stop)


def _convert(global_settings, object_settings, source=None):
    """Convert HTML to PDF.

    Parameters:
      global_settings(dict[str, str])
      object_settings(dict[str, str])
      source(str): If provided, the source will be rendered as HTML
        then converted to a PDF, avoiding the need for a web request.

    Returns:
      Task: A value representing the async conversion process.

    See also:
      https://wkhtmltopdf.org/libwkhtmltox/pagesettings.html
    """
    task = _Task(global_settings, object_settings, source)
    _converter.submit(task)
    return task


def _convert_args(args):
    converted_args = {}
    for name, value in args.items():
        if value is None:
            continue

        if isinstance(value, bool):
            converted_args[name] = str(value).lower()
        else:
            converted_args[name] = str(value)

    return converted_args
