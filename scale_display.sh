#!/bin/sh
xrandr --newmode "1920x1200_60.00"  193.25  1920 2056 2256 2592  1200 1203 1209 1245 -hsync +vsync
if [ $# -eq 1 ]
   then
       xrandr --addmode $1 1920x1200_60.00
       xrandr --output $1 --mode 1920x1200_60.00
else
       xrandr --addmode HDMI1 1920x1200_60.00
       xrandr --output HDMI1 --mode 1920x1200_60.00
fi

   
