from setuptools import setup, find_packages

setup(
    name='app',
    version='0.1.0',
    description='Kivy-плагин для отправки уведомлений на основе GPS',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Egor',
    url='https://github.com/AmsterdaM1505/hackathon.git',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kivy',
        'plyer',
        'requests',
        'flask'
    ],
    entry_points={
        'console_scripts': [
            'app=app:GeoApp.run'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
