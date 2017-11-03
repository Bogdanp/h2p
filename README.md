# h2p

[![Build Status](https://travis-ci.org/Bogdanp/h2p.svg?branch=master)](https://travis-ci.org/Bogdanp/h2p)
[![Test Coverage](https://api.codeclimate.com/v1/badges/d20f010978828b7530dd/test_coverage)](https://codeclimate.com/github/Bogdanp/h2p/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/780d074f7d151fddb1b9/maintainability)](https://codeclimate.com/github/Bogdanp/h2p/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/780d074f7d151fddb1b9/test_coverage)](https://codeclimate.com/github/Bogdanp/h2p/test_coverage)

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
