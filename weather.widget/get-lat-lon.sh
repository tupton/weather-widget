#! /usr/bin/env zsh

whereami="/usr/local/bin/whereami"

if (( $# > 0 )); then
    whereami=$1
fi

output=$(which $whereami > /dev/null && $whereami)

if (( $? == 0 )); then
    echo "$output" | /usr/local/bin/awk -vORS=',' 'NR > 2 { exit }; { print $2 }' | sed 's/,$//'
else
    ret=$?
    >&2 echo "Unable to determine latitude and longitude: $output"
    exit ret
fi
