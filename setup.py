import sys
from setuptools import setup, Extension

# Define the C++ extension
backend_module = Extension(
    'scl_backend',
    sources=['src/scl_backend.cpp'],
    language='c++',
    extra_compile_args=['/std:c++11'] if 'win32' in sys.platform else ['-std=c++11'],
)

setup(
    name='SunsetCodeLang',
    version='1.0.0',
    description='SunsetCodeLang - A console programming language',
    ext_modules=[backend_module],
    py_modules=['scl'],
    packages=['src'],
    package_dir={'src': 'src'},
    entry_points={
        'console_scripts': [
            'scl = scl:main',
        ],
    },
)
