#!/usr/bin/env python3

from distutils.core import setup
import glob
import os
from DistUtilsExtra.command import *

setup(name='indicator-places',
      version='1.0.0',
      description='Simple indicator places for Stalonetray/Openbox',
      author='Alexandre C Vieira',
      author_email='acamargo.vieira@gmail.com',
      url='https://github.com/alexandrecvieira/indicator-places',
      scripts=[
          'indicator-places',
      ],
      cmdclass={"build": build_extra.build_extra,
                "build_i18n": build_i18n.build_i18n}
      )
