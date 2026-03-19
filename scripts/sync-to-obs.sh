#!/bin/bash
# Sync packaging files to an OBS (osc) checkout directory
#
# Usage: ./scripts/sync-to-obs.sh /path/to/osc/checkout [version]
#
# Prerequisites:
#   osc checkout home:USERNAME/i2p
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

OBS_DIR="${1:?Usage: $0 /path/to/osc/checkout [version]}"
VERSION="${2:-$(grep '^Version:' "${REPO_DIR}/SPEC/i2p.spec" | awk '{print $2}')}"

echo "Syncing i2p ${VERSION} to OBS checkout at ${OBS_DIR}"

# Copy spec file
cp "${REPO_DIR}/SPEC/i2p.spec" "${OBS_DIR}/"

# Copy all source files
cp "${REPO_DIR}/SOURCES/"* "${OBS_DIR}/"

# Copy OBS-specific files
cp "${REPO_DIR}/obs/i2p.changes" "${OBS_DIR}/"

# Copy _service if it exists
if [ -f "${REPO_DIR}/obs/_service" ]; then
    cp "${REPO_DIR}/obs/_service" "${OBS_DIR}/"
fi

# Download source tarball if not already present
TARBALL="i2psource_${VERSION}.tar.bz2"
if [ ! -f "${OBS_DIR}/${TARBALL}" ]; then
    echo "Downloading source tarball..."
    curl -fSL -o "${OBS_DIR}/${TARBALL}" \
        "https://files.i2p-projekt.de/${VERSION}/${TARBALL}"
fi

echo ""
echo "Done. Now cd to ${OBS_DIR} and run:"
echo "  osc addremove"
echo "  osc ci -m 'Update to ${VERSION}'"
