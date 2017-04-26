"""setuptools configuration for valet_crud_api."""

__version__='1.0.0'
__name__='issue_to_story_sync'

from setuptools import setup, find_packages

setup(
    name=__name__,
    version=__version__,
    url='https://github.homedepot.com/CloudEngineering/issue-to-story-sync',
    description="App to Sync Github Issues to Pivotal Tracker Stories",
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs', 'k8s']),
    install_requires=[
        'APScheduler==3.3.1',
        'click==6.6',
        'enum34==1.1.6',
        'Flask==0.12',
        'funcsigs==1.0.2',
        'future==0.16.0',
        'futures==3.0.5',
        'httplib2==0.9.2',
        'issue-to-story-sync==1.0.0',
        'itsdangerous==0.24',
        'Jinja2==2.8.1',
        'MarkupSafe==0.23',
        'oauth2client==4.0.0',
        'ply==3.8',
        'protobuf==3.2.0rc1.post1',
        'pyasn1==0.1.9',
        'pyasn1-modules==0.0.8',
        'pytz==2016.10',
        'requests==2.12.4',
        'rsa==3.4.2',
        'six==1.10.0',
        'tzlocal==1.3',
        'Werkzeug==0.11.15',
        'gunicorn'

    ],
    entry_points={
        'console_scripts': [
            '{} = {}:application.run'.format(__name__, __name__),
        ]
    },
    zip_safe=False,
)
