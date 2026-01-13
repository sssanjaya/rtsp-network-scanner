"""Setup configuration for RTSP Scanner"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='rtsp-network-scanner',
    version='2.5.1',
    author='Sanjay H',
    author_email='contact@sanjayhona.com.np',
    description='Scan networks for RTSP cameras, test streams, discover channels',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sssanjaya/rtsp-network-scanner',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Multimedia :: Video',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Environment :: Console',
        'Natural Language :: English',
    ],
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses Python standard library only
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'twine>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'rtsp-network-scanner=rtsp_scanner.cli:main',
        ],
    },
    keywords='rtsp scanner network camera security debug stream video surveillance ipcam monitoring',
    project_urls={
        'Bug Reports': 'https://github.com/sssanjaya/rtsp-network-scanner/issues',
        'Source': 'https://github.com/sssanjaya/rtsp-network-scanner',
        'Documentation': 'https://github.com/sssanjaya/rtsp-network-scanner#readme',
    },
    include_package_data=True,
    zip_safe=False,
)
