try:
    from setuptools import setup, find_packages
except ImportError as e:
    from distutils.core import setup

__version__ = "1.0.0-beta"

config = {
    'name': 'rpi-disklavier',
    'version': __version__,
    'description': 'A MusicPlayer which can be controlled by different controllers',
    'long_description': open('README.md').read(),
    'author': 'Jordan Jarvis',
    'author_email': 'Not@online.com',
    'classifiers': [
        'Development Status :: 1 - beta',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    'url': 'None',
    'download_url': 'https://github.com/Jordan-Jarvis/RPi-Diskalvier-network-player',
    'install_requires': [
        'mido',
        'python-rtmidi'
    ],
    'packages': find_packages(exclude=['docs', 'tests']),
}

setup(**config)
