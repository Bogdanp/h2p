import ctypes
import os

from ctypes.util import find_library

LIBRARY_PATH = os.getenv("WKHTMLTOPDF_LIBRARY_PATH")
if LIBRARY_PATH:
    _library_path = LIBRARY_PATH
else:
    _library_path = find_library("libwkhtmltox.0.12")

if not _library_path:  # pragma: no cover
    raise ImportError("Could not find 'libwkhtmltox' version 0.12 on your load path.")

_wkhtmltox = ctypes.cdll.LoadLibrary(_library_path)


class _GlobalSettings(ctypes.Structure):
    pass


class _ObjectSettings(ctypes.Structure):
    pass


class _Converter(ctypes.Structure):
    pass


_global_settings_p = ctypes.POINTER(_GlobalSettings)
_object_settings_p = ctypes.POINTER(_ObjectSettings)
_converter_p = ctypes.POINTER(_Converter)

init = _wkhtmltox.wkhtmltopdf_init
init.argtypes = [ctypes.c_int]
init.restype = ctypes.c_int

deinit = _wkhtmltox.wkhtmltopdf_deinit
deinit.restype = ctypes.c_int

version = _wkhtmltox.wkhtmltopdf_version
version.restype = ctypes.c_char_p

_create_global_settings = _wkhtmltox.wkhtmltopdf_create_global_settings
_create_global_settings.restype = _global_settings_p

_create_object_settings = _wkhtmltox.wkhtmltopdf_create_object_settings
_create_object_settings.restype = _object_settings_p

_destroy_global_settings = _wkhtmltox.wkhtmltopdf_destroy_global_settings
_destroy_global_settings.argtypes = [_global_settings_p]

_destroy_object_settings = _wkhtmltox.wkhtmltopdf_destroy_object_settings
_destroy_object_settings.argtypes = [_object_settings_p]

_set_global_setting = _wkhtmltox.wkhtmltopdf_set_global_setting
_set_global_setting.argtypes = [_global_settings_p, ctypes.c_char_p, ctypes.c_char_p]
_set_global_setting.restype = ctypes.c_int

_set_object_setting = _wkhtmltox.wkhtmltopdf_set_object_setting
_set_object_setting.argtypes = [_object_settings_p, ctypes.c_char_p, ctypes.c_char_p]
_set_object_setting.restype = ctypes.c_int

_create_converter = _wkhtmltox.wkhtmltopdf_create_converter
_create_converter.restype = _converter_p

_destroy_converter = _wkhtmltox.wkhtmltopdf_destroy_converter
_destroy_converter.argtypes = [_converter_p]

_convert = _wkhtmltox.wkhtmltopdf_convert
_convert.argtypes = [_converter_p]
_convert.restype = ctypes.c_int

_add_object = _wkhtmltox.wkhtmltopdf_add_object
_add_object.argtypes = [_converter_p, _object_settings_p, ctypes.c_char_p]


def convert(gs, os, source=None):
    source = source and ctypes.c_char_p(source.encode("utf-8"))
    global_settings = _create_global_settings()
    for setting, value in gs.items():
        _set_global_setting(
            global_settings,
            ctypes.c_char_p(setting.encode("utf-8")),
            ctypes.c_char_p(value.encode("utf-8")),
        )

    object_settings = _create_object_settings()
    for setting, value in os.items():
        _set_object_setting(
            object_settings,
            ctypes.c_char_p(setting.encode("utf-8")),
            ctypes.c_char_p(value.encode("utf-8")),
        )

    converter = _create_converter(global_settings)
    try:
        _add_object(converter, object_settings, source)
        if _convert(converter) == 0:
            return False
        return True
    finally:
        _destroy_converter(converter)
