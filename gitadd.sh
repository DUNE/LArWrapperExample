#./jclean.sh jupyter/findRequests.ipynb
#./jclean.sh jupyter/convert.ipynb

git add *.sh batch/*.sh batch/*.cfg python/*.py docs/source/*.rst docs/source/conf.py fcl/*.fcl \
  tests/*.sh docs/*.jpg docs/*.sh docs/google* analysis/*.ipynb analysis/*.py README.rst docs/source/*.csv \
  docs/source/*.json sql/*.sql jupyter/*.ipynb jupyter/*.py datasets/*.json scripts/*.py
  
# patch to recover the google html once a make clean has been run
cp docs/google* docs/build/html/
