from setuptools import setup, Extension

setup(ext_modules=[
    Extension(
        '_foo',
        ['_foo.c'],
        py_limited_api = True,
    )
])
