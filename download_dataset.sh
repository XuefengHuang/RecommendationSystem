#!/usr/bin/env bash

#hash wget 2>/dev/null || { echo >&2 "Wget required.  Aborting."; exit 1; }
#hash unzip 2>/dev/null || { echo >&2 "unzip required.  Aborting."; exit 1; }

#wget http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip
unzip -o "BX-CSV-Dump"
DESTINATION="./datasets/"
mkdir -p $DESTINATION
mv ml-latest $DESTINATION