#!/bin/sh

python nevowdriver.py

cd core
$LORE --config template=template.tpl --config ext= *.html
cd ..
