#!/bin/bash

# launch script from project root directory

pyinstaller \
 --clean \
 --noconfirm \
 --distpath build/dist \
 --workpath build/tmp \
  pyinstaller_base.spec