# I2P RPM Packaging

RPM packaging for [I2P](https://i2p.net/), the Invisible Internet Project anonymous network router.

Produces installable `.rpm` packages for Fedora, RHEL/CentOS/Rocky/Alma Linux, and openSUSE.

> **Note:** Despite the "jpackage" name, this repository does not use Java's `jpackage` tool.
> The name follows the I2P project's convention of prefixing deployment packaging repos with
> `i2p-jpackage-` (e.g., `i2p-jpackage-deb`, `i2p-jpackage-rpm`) to keep them organized
> under a common namespace.

## Supported Distributions

| Distribution | Build System | Status |
|---|---|---|
| Fedora 41+ | [COPR](https://copr.fedorainfracloud.org/coprs/i2porg/i2p/) | Active |
| RHEL/CentOS/Rocky/Alma 9+ | COPR (with EPEL) | Active |
| openSUSE Tumbleweed | [OBS](https://build.opensuse.org/) | In progress |
| openSUSE Leap 15.6 | OBS | In progress |

## Install from COPR (Fedora/RHEL)

```bash
sudo dnf copr enable i2porg/i2p
sudo dnf install i2p
```

## Install from OBS (openSUSE)

See [obs/README.md](obs/README.md) for OBS setup and build instructions.

## Quick Start (Build Locally)

### Fedora

```bash
# Using the build container (recommended)
podman build -t i2p-rpm-builder -f docker/Dockerfile.build .
podman run --rm -v ./output:/output i2p-rpm-builder /build/scripts/build-rpm.sh 2.11.0

# Or build locally
sudo dnf install rpm-build rpmdevtools java-latest-openjdk-devel ant gettext systemd-rpm-macros
./scripts/build-rpm.sh 2.11.0
```

### openSUSE

```bash
# Using the build container
./scripts/build-obs.sh 2.11.0

# Or build locally
sudo zypper install rpm-build rpmdevtools java-17-openjdk-devel ant gettext-runtime systemd-rpm-macros sysuser-tools
./scripts/build-rpm.sh 2.11.0
```

The built RPMs will be in `./output/`.

## Installing (from local build)

```bash
# Fedora
sudo dnf install ./output/i2p-*.noarch.rpm

# openSUSE
sudo zypper install ./output/i2p-*.noarch.rpm
```

## Post-Install

```bash
# Start I2P
sudo systemctl start i2p

# Enable at boot
sudo systemctl enable i2p

# Check status
sudo systemctl status i2p

# Router console (available after startup)
# http://127.0.0.1:7657
```

## Configuration

- `/etc/sysconfig/i2p` — Java options (heap size, JAVA_HOME override)
- `/var/lib/i2p/` — Router state, keys, and runtime configuration
- `/var/log/i2p/` — Log files

## Project Structure

```
SPEC/i2p.spec            # RPM spec file (multi-distro with conditionals)
SOURCES/                  # Systemd units, configs, wrapper script
scripts/                  # Build and test scripts
docker/                   # Build container Dockerfiles (Fedora + openSUSE)
obs/                      # openSUSE Build Service files
.github/workflows/       # CI pipelines
.copr/                   # COPR build integration
```

## Testing

```bash
# Test on Fedora
./scripts/test-install.sh

# Test on openSUSE
./scripts/test-install-suse.sh
```

## License

I2P is a multi-licensed project. See the spec file for the full SPDX license expression.
The packaging files in this repository are licensed under Apache-2.0.
