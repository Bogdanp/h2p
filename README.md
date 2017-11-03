# h2p

This package converts HTML pages to PDFs by leveraging `libwkhtmltox`
via ctypes, avoiding the need to spawn subprocesses on every call.

## Installation

    pipenv install h2p

## Usage

Make sure `libwkhtmltox.0.12` is on your library path.

``` python
from h2p import generate_pdf

# PDFs are built on a background thread so each call to
# generate_pdf is asynchronous.
task = generate_pdf("output.pdf", source_uri="http://example.com")

# result blocks until a task has finished.  If an error occurred
# this will raise a ConversionError.
task.result()
```

See `help(generate_pdf)` for info on the available parameters.

## License

h2p is licensed under Apache 2.0.  Please see [LICENSE][license] for
licensing details.

[license]: https://github.com/Bogdanp/h2p/blob/master/LICENSE
