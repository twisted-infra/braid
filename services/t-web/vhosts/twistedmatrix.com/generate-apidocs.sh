#!/bin/bash

if [ "$1" = "" ]; then
       OUT="api"
else
       OUT="$1"
fi

pushd documents/current
bunzip2 --keep twisted-doc-model.bz2
pydoctor -p twisted-doc-model --make-html --html-writer=pydoctor.nevowhtml.NevowWriter --html-output="$OUT" --html-write-function-pages
rm twisted-doc-model
ln -sf twisted.html "$OUT"/index.html
popd
