import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                         '..',
                                         '..',))

BEESCAN_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                            '..',))

FRAMEWORK_DIR = os.path.abspath(os.path.join(BASE_DIR,
                                             'Beebeeto-framework',))

POC_DIR = os.path.abspath(os.path.join(BEESCAN_DIR,
                                        'pocs',))


sys.path.extend([BASE_DIR, FRAMEWORK_DIR, POC_DIR])

VERSION = '0.1.0'


if __name__ == '__main__':
    print BASE_DIR
    print BEESCAN_DIR
    print FRAMEWORK_DIR
    print POC_DIR
