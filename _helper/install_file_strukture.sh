#!/bin/bash

# Liste mit festen Ordnern (inkl. Subfolder)
ORDNERLISTE=(
    "server/api/routes"
    "server/api/models"
    "server/api/serices"

    "server/scripts"
    "server/config"

    "client/ui/windows"
    "client/ui/widgets"
    "client/ui/styles"

    "client/controllers"
    "client/services"

    "shared/models"
    "shared/utils"

    "config/caddy"
    "config/app"

    "data/backups"
    "data/logs"
    "data/certs"
)

# Schleife durch die Liste
for ORDNER in "${ORDNERLISTE[@]}"; do
    ORDNER="../$ORDNER"
    if [ ! -d "$ORDNER" ]; then
        mkdir -p "$ORDNER"
        if [ -d "$ORDNER" ]; then
            echo "Erstellt: $ORDNER"
        fi
    else
        echo "Übersprungen (existiert schon): $ORDNER"
    fi
done
