#!/bin/bash
#===============================================================================
#
#          FILE:  irssi_notify.sh
# 
#         USAGE:  ./irssi_notify.sh 
# 
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Dan Colish (), dan@unencrypted.org
#       COMPANY:  
#       VERSION:  1.0
#       CREATED:  10/22/2009 03:49:01 PM PDT
#      REVISION:  ---
#===============================================================================
(ssh teh "tail -n 10 ~/.irssi/fnotify; : > ~/.irssi/fnotify ; tail -f ~/.irssi/fnotify" \
| sed -u 's/[\<\@\&]//g' \
| while read heading message; \
do notify-send -i gtk-dialog-info -t 10000 -- "${heading}" "${message}"; done) 2>&1 > /dev/null &
