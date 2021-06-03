# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='h5dataviewer',
    version='1.0.0',
    description='`https://github.com/shikishima-TasakiLab/h5dataviewer`',
    long_description='`https://github.com/shikishima-TasakiLab/h5dataviewer`',
    author='Junya Shikishima',
    author_email='160442065@ccalumni.meijo-u.ac.jp',
    url='https://github.com/shikishima-TasakiLab/h5dataviewer',
    license='',
    packages=find_packages(),
    install_requires=[
        "numpy", "h5py==2.10.0", "scipy", "opencv-python-headless", "PySide2", "pyqtgraph", "pyopengl", "pyopengl accelerate"
    ],
    entry_points={
        'console_scripts': [
            'h5dataviewer = h5dataviewer.dataviewer:main',
        ]
    },
    python_requires='>=3.6'
)