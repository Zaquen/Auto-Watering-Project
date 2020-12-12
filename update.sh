#!/bin/bash

while :
do
git add data.txt

git commit -m 'Updating Data'

git push origin master

sleep 3600

done

