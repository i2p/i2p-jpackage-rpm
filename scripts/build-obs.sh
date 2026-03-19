#!/bin/bash
# Build the I2P RPM as if on openSUSE (using container or osc build)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

VERSION="${1:-$(grep '^Version:' "${REPO_DIR}/SPEC/i2p.spec" | awk '{print $2}')}"

CONTAINER_ENGINE="podman"
if ! command -v podman &>/dev/null; then
    CONTAINER_ENGINE="docker"
fi

echo "=== Building I2P ${VERSION} RPM for openSUSE ==="

# Build the container image
echo "--- Building openSUSE builder image ---"
${CONTAINER_ENGINE} build -t i2p-rpm-builder-suse \
    -f "${REPO_DIR}/docker/Dockerfile.build-suse" \
    "${REPO_DIR}"

# Create output directory
mkdir -p "${REPO_DIR}/output"

echo "--- Building RPM in openSUSE container ---"
${CONTAINER_ENGINE} run --rm \
    -v "${REPO_DIR}/output:/output" \
    i2p-rpm-builder-suse \
    /bin/bash -c "
        set -euo pipefail

        VERSION='${VERSION}'

        # Setup rpmbuild tree
        rpmdev-setuptree

        # Copy spec and sources
        cp /build/SPEC/i2p.spec ~/rpmbuild/SPECS/
        cp /build/SOURCES/* ~/rpmbuild/SOURCES/

        # Update version in spec
        sed -i \"s/^Version:.*/Version:        \${VERSION}/\" ~/rpmbuild/SPECS/i2p.spec

        # Download source tarball
        /build/scripts/fetch-source.sh \"\${VERSION}\" ~/rpmbuild/SOURCES/

        # Build RPM
        rpmbuild -ba ~/rpmbuild/SPECS/i2p.spec

        # Copy output
        cp ~/rpmbuild/RPMS/*/*.rpm /output/ 2>/dev/null || true
        cp ~/rpmbuild/SRPMS/*.rpm /output/ 2>/dev/null || true

        echo ''
        echo '=== Build complete ==='
        ls -la /output/*.rpm 2>/dev/null || echo 'No RPMs produced'
    "

echo ""
echo "RPMs in ${REPO_DIR}/output/"
ls -la "${REPO_DIR}/output/"*.rpm 2>/dev/null || true
