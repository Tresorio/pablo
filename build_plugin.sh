find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

mkdir tresorio
ln -s ../bundle_modules ./tresorio/bundle_modules
ln -s ../config ./tresorio/config 
ln -s ../src ./tresorio/src
ln -s ../__init__.py ./tresorio/__init__.py
ln -s ../icons ./tresorio/icons

zip -r tresorio.zip tresorio
rm -rf tresorio
