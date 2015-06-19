#!/bin/sh
# Run me with "sudo -u www-data ./generate.sh on pyramid
export PYTHONPATH=.:$PYTHONPATH
export LORE=/var/www/Projects/Twisted/trunk/bin/lore/lore

for subdir in developers glyph images products services; 
    do $LORE -e .html --prefixurl="../" --docsdir $subdir \
           --config template=template.tpl \
           --config ext= \
           --config pageclass=nevowdriver.TMPage \
           -i nevow
    done

cd documents
$LORE -e .html --prefixurl="../" \
           --config template=../template.tpl \
           --config ext= \
           admin.html index.html
cd ..



$LORE -e .html --config template=template.tpl --config ext= \
              --config pageclass=nevowdriver.TMPage \
	      -i nevow index-old.html labs.html sponsor.html news.html


cd projects
./generate.sh
cd ..
