#!/bin/bash
basedir=$(pwd)

ls /opt/indicator-places

if [ $? -ne 0 ] ; then
    sudo mkdir /opt/indicator-places
fi

sudo cp indicator-places.py /opt/indicator-places/

cat $HOME/.config/openbox/autostart > ~/Downloads/temp.tmp
temp=$(sed -n '/indicator-places &/p' ~/Downloads/temp.tmp)
if [ ${#temp} -gt 0 ] ; then
    echo "--------------------------------------"
    echo "indicator-places já estava configurado."
    echo "--------------------------------------"
    rm ~/Downloads/temp.tmp
else
    echo "indicator-places &" >> ~/Downloads/temp.tmp
    cp ~/Downloads/temp.tmp $HOME/.config/openbox/autostart
    rm ~/Downloads/temp.tmp
    echo "--------------------------------------"
    echo "indicator-places foi configurado."
    echo "--------------------------------------"
fi

ls /usr/bin/indicator-places

if [ $? -ne 0 ] ; then
    cd /usr/bin/
    sudo ln -s /opt/indicator-places/indicator-places.py indicator-places
fi
