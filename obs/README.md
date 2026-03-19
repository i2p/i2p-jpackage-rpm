# Building I2P for openSUSE via OBS

## Prerequisites

- Account on https://build.opensuse.org
- `osc` command-line tool installed (`zypper install osc` or `dnf install osc`)
- Configured `~/.config/osc/oscrc` with your credentials

## Initial OBS Setup (one-time)

1. Log in to https://build.opensuse.org
2. Go to your home project (Home Project button)
3. Create a subproject: "i2p" (becomes `home:USERNAME:i2p`)
4. Add target repositories:
   - openSUSE Tumbleweed (x86_64)
   - openSUSE Leap 15.6 (x86_64)
5. Checkout locally:
   ```
   osc checkout home:USERNAME:i2p
   cd home:USERNAME:i2p
   osc mkpac i2p
   ```

## Syncing and Building

From the repo root:

```bash
# Sync all files to your OBS checkout
./scripts/sync-to-obs.sh /path/to/home:USERNAME:i2p/i2p

# Commit and trigger build
cd /path/to/home:USERNAME:i2p/i2p
osc addremove
osc ci -m "Update to version X.Y.Z"

# Watch the build
osc results
osc buildlog openSUSE_Tumbleweed x86_64
```

## Local Build Testing

```bash
# Using the openSUSE container
./scripts/build-obs.sh 2.11.0

# Test installation
./scripts/test-install-suse.sh
```

## Submitting to security:privacy

Once the package is stable in your home project, submit it to the
`security:privacy` OBS project (where i2pd already lives):

```
osc submitrequest home:USERNAME:i2p/i2p security:privacy i2p
```
