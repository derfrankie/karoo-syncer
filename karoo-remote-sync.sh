#!/bin/bash

# Read users and configuration from ksync.json
users=$(jq -r '.users[]' ksync.json)

for user in $users; do
    # Get the username and password for the current user
    username=$(echo "$user" | jq -r '.username')
    password=$(echo "$user" | jq -r '.password')

    # Get the token from the Dashboard Login page
    token=$(curl 'https://dashboard.hammerhead.io/v1/auth/token' \
      -H 'Accept: application/json; charset=UTF-8' \
      -H 'Content-Type: application/json' \
      --data-raw '{"grant_type": "password", "username": "'"$username"'", "password": "'"$password"'"}' | jq '.access_token')

    # Get the userid from the jwt token
    userid=$(echo "$token" | jwt_decode | jq '.sub')

    # Remove the double quotes from the token string
    token=$(sed -e 's/^"//' -e 's/"$//' <<<"$token")

    # Remove the double quotes from the userid string
    userid=$(sed -e 's/^"//' -e 's/"$//' <<<"$userid")

    # Refresh the routes
    curl "https://dashboard.hammerhead.io/v1/users/$userid/routes/sync" \
      -H 'Accept: */*' \
      -H 'Accept-Language: en-US,en;q=0.9,nl;q=0.8' \
      -H "Authorization: Bearer $token" \
      -H 'Connection: keep-alive' \
      -H 'Content-Type: application/json' \
      -H 'Origin: https://dashboard.hammerhead.io' \
      -H 'Referer: https://dashboard.hammerhead.io/routes' \
      --data-raw 'null' \
      --compressed

done
