#!/bin/zsh
set -e
cd "${0:A:h}"
swiftc -O -framework AppKit Kurama.swift -o kurama-app
chmod +x kurama
print 'Built Kurama. Run ./kurama start'
