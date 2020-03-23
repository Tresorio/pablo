#!/usr/bin/env sh

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

mkdir tresorio
ln -s ../bundle_modules ./tresorio/bundle_modules
ln -s ../config ./tresorio/config
cp -r ./src ./tresorio/src
echo "MODE = \"$1\"" >> ./tresorio/src/config/api.py
ln -s ../__init__.py ./tresorio/__init__.py
ln -s ../assets ./tresorio/assets

zip -r tresorio.zip tresorio
rm -rf tresorio
