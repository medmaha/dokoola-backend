#!/bin/bash

curl -LO https://trunk.io/releases/trunk && chmod +x ./trunk
./trunk flakytests upload \
    --org-url-slug "dokoola" \
    --token "bad34222bcacf120fd033e9527a545191e262c23" \
    --junit-paths "**/*.xml" # replace this with the path to your junit file
