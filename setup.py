from setuptools import setup, find_packages

with open('README.rst') as rf, open('HISTORY.rst') as hf:
    long_description = rf.read() + hf.read()

setup(
    name='django-commentary',
    version='2.0.0.dev1',
    url='https://github.com/mangadventure/django-commentary',
    description='Yet another Django comment framework.',
    long_description_content_type='text/x-rst',
    long_description=long_description,
    author='Django Software Foundation',
    author_email='jacob@jacobian.org',
    maintainer='MangAdventure',
    maintainer_email='chronobserver@disroot.org',
    license='BSD',
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    test_suite='tests.runtests.main',
    install_requires=['Django>=3.0']
)
