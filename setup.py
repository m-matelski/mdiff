import setuptools

setuptools.setup(
    name='mdiff',
    packages=setuptools.find_packages(),
    version='0.0.1',
    license='MIT',
    description='Compare sequences',
    author='Mateusz Matelski',
    author_email='m.z.matelski@gmail.com',
    url='https://github.com/m-matelski/mdiff',
    download_url = 'https://github.com/m-matelski/mdiff/archive/v0.0.1.tar.gz',
    keywords = ['sql', 'diff', 'postgres', 'teradata'],
    install_requires=[
        'colorama==0.4.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)