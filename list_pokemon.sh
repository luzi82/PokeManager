#!/bin/bash

. _config.sh

if [ "$#" = "1" ]; then
	ARG_SORT=${1}
else
	ARG_SORT="recent"
fi

echo ${ARG_SORT}

python "./pogo/list_pokemon.py" -a google -u "${USER_ID}" -p "${PASSWORD}" -s ${ARG_SORT}
