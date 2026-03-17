#!/bin/bash
# /usr/libexec/i2p/i2p-wrapper.sh
# Launcher script for the I2P router under systemd
#
# This script sets up the Java classpath, I2P directory properties,
# and launches the I2P router process.

set -euo pipefail

# Detect JAVA_HOME if not set via /etc/sysconfig/i2p
if [ -z "${JAVA_HOME:-}" ]; then
    # Use system java
    JAVA_BIN=$(readlink -f "$(command -v java)")
    JAVA_HOME=$(dirname "$(dirname "$JAVA_BIN")")
fi

JAVA="${JAVA_HOME}/bin/java"

if [ ! -x "$JAVA" ]; then
    echo "ERROR: Java not found at ${JAVA}" >&2
    exit 1
fi

# I2P directory layout (FHS-compliant)
I2P_BASE="/usr/share/i2p"
I2P_CONFIG="/var/lib/i2p"
I2P_LOG="/var/log/i2p"
I2P_PID="/run/i2p"

# Build classpath from all JARs in the lib directory
CLASSPATH=""
for jar in "${I2P_BASE}/lib/"*.jar; do
    if [ -f "$jar" ]; then
        if [ -n "$CLASSPATH" ]; then
            CLASSPATH="${CLASSPATH}:"
        fi
        CLASSPATH="${CLASSPATH}${jar}"
    fi
done

if [ -z "$CLASSPATH" ]; then
    echo "ERROR: No JAR files found in ${I2P_BASE}/lib/" >&2
    exit 1
fi

# Copy default configs on first run
for cfg in "${I2P_BASE}"/*.config; do
    cfg_name=$(basename "$cfg")
    if [ ! -f "${I2P_CONFIG}/${cfg_name}" ]; then
        cp "$cfg" "${I2P_CONFIG}/${cfg_name}"
    fi
done

# I2P system properties
I2P_PROPS=(
    "-Di2p.dir.base=${I2P_BASE}"
    "-Di2p.dir.config=${I2P_CONFIG}"
    "-Di2p.dir.router=${I2P_CONFIG}"
    "-Di2p.dir.log=${I2P_LOG}"
    "-Di2p.dir.pid=${I2P_PID}"
    "-Djava.library.path=/usr/lib64/i2p:/usr/lib/i2p"
    "--enable-native-access=ALL-UNNAMED"
)

# Launch the I2P router
# shellcheck disable=SC2086
exec "$JAVA" \
    -cp "$CLASSPATH" \
    "${I2P_PROPS[@]}" \
    ${JAVA_OPTS:-} \
    net.i2p.router.Router
