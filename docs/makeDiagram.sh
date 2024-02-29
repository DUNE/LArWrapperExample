export TEMP=$PWD
cd $HERE/python
pydeps LArWrapper.py -T jpg --cluster --rankdir BT #--include-missing 
pydeps samtest.py -T jpg  --cluster --rankdir BT #--include-missing 
pydeps CollectionCreatorClass.py -T jpg --cluster --rankdir BT 
pydeps DDInterface.py -T jpg --cluster --rankdir BT 
mv CollectionCreatorClass.jpg $HERE/docs
mv DDInterface.jpg $HERE/docs
mv LArWrapper.jpg $HERE/docs
mv samtest.jpg $HERE/docs
chmod +x $HERE/docs/*.jpg
cd $TEMP
