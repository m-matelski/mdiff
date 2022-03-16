import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


VERSION = '0.1.3'

setuptools.setup(
    name='mdiff',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    license='MIT',
    description='Sequence matcher with displacement detection.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Mateusz Matelski',
    author_email='m.z.matelski@gmail.com',
    url='https://github.com/m-matelski/mdiff',
    keywords=['sequence', 'diff', 'heckel', 'text'],
    entry_points={
        'console_scripts': [
            'mdiff=mdiff.cli:main',
            'mdiff-gui=mdiff.visualisation.gui_tkinter.main:start_app'
        ]
    },
    extras_require={
        'cli': ['colorama==0.4.*', 'typer==0.4.*']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
)
