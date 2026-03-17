# I2P RPM Spec File
# Produces an installable RPM for the I2P anonymous network router

%global i2p_home    /usr/share/i2p
%global i2p_confdir /var/lib/i2p
%global i2p_logdir  /var/log/i2p
%global i2p_rundir  /run/i2p
%global i2p_libexec /usr/libexec/i2p

Name:           i2p
Version:        2.11.0
Release:        1%{?dist}
Summary:        Anonymous network providing privacy-preserving communication

License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT AND GPL-2.0-only AND GPL-2.0-or-later AND GPL-3.0-only AND LGPL-2.1-only AND EPL-1.0 AND CC-BY-3.0 AND Artistic-2.0
URL:            https://geti2p.net/
Source0:        https://files.i2p-projekt.de/%{version}/i2psource_%{version}.tar.bz2
Source1:        i2p.service
Source2:        i2p.sysusers
Source3:        i2p.tmpfiles
Source4:        i2p.conf
Source5:        i2p-wrapper.sh
Source6:        i2p.logrotate

BuildRequires:  java-devel >= 1:17
BuildRequires:  ant
BuildRequires:  gettext
BuildRequires:  systemd-rpm-macros

Requires:       java-headless >= 1:17
Requires(pre):  shadow-utils

# Disable automatic dependency generation — I2P bundles its own JARs
AutoReqProv:    no

# I2P is Java (noarch JARs) but may include architecture-specific JNI (jbigi)
# Start as noarch; switch to arch-specific if jbigi native build is added
BuildArch:      noarch

%description
I2P is an anonymous network that provides strong privacy protections for
communication. It offers a simple layer that identity-sensitive applications
can use to securely communicate. All data is wrapped with several layers of
encryption, and the network is both distributed and dynamic, with no trusted
parties.

The I2P router provides HTTP proxy, SOCKS proxy, router console (web UI),
I2PSnark (BitTorrent client), SusiMail (email client), and other services
accessible at 127.0.0.1:7657 after starting the service.

%prep
%setup -q -n i2p-%{version}

%build
# Build I2P using the pkg target (headless Linux, no installer)
ant preppkg-linux-only \
    -Dfile.encoding=UTF-8 \
    -Djavac.compilerargs="--release 17" \
    -Dbuild.built-by="RPM Build"

%install
rm -rf %{buildroot}

# Static data: JARs, webapps, certificates, geoip, docs
install -d -m 755 %{buildroot}%{i2p_home}
install -d -m 755 %{buildroot}%{i2p_home}/lib
install -d -m 755 %{buildroot}%{i2p_home}/webapps
install -d -m 755 %{buildroot}%{i2p_home}/certificates
install -d -m 755 %{buildroot}%{i2p_home}/geoip
install -d -m 755 %{buildroot}%{i2p_home}/docs

# Copy build output from pkg-temp
cp -a pkg-temp/lib/*.jar %{buildroot}%{i2p_home}/lib/
cp -a pkg-temp/webapps/*.war %{buildroot}%{i2p_home}/webapps/ 2>/dev/null || true
cp -a pkg-temp/webapps/ %{buildroot}%{i2p_home}/ 2>/dev/null || true
cp -a pkg-temp/certificates/ %{buildroot}%{i2p_home}/ 2>/dev/null || true
cp -a pkg-temp/geoip/ %{buildroot}%{i2p_home}/ 2>/dev/null || true
cp -a pkg-temp/docs/ %{buildroot}%{i2p_home}/ 2>/dev/null || true

# Copy ALL data and config files from upstream build
for f in pkg-temp/*.txt pkg-temp/*.config; do
    [ -f "$f" ] && cp -a "$f" %{buildroot}%{i2p_home}/ || true
done

# Apply headless-friendly overrides to upstream router.config
# Disable auto-update (package manager handles updates)
echo "" >> %{buildroot}%{i2p_home}/router.config
echo "# RPM package overrides" >> %{buildroot}%{i2p_home}/router.config
echo "router.updateDisabled=true" >> %{buildroot}%{i2p_home}/router.config

# Wrapper script
install -d -m 755 %{buildroot}%{i2p_libexec}
install -m 755 %{SOURCE5} %{buildroot}%{i2p_libexec}/i2p-wrapper.sh

# Systemd service
install -d -m 755 %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/i2p.service

# Sysusers
install -d -m 755 %{buildroot}%{_sysusersdir}
install -m 644 %{SOURCE2} %{buildroot}%{_sysusersdir}/i2p.conf

# Tmpfiles
install -d -m 755 %{buildroot}%{_tmpfilesdir}
install -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/i2p.conf

# Environment config
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/i2p

# Logrotate
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/i2p

# Mutable state directory
install -d -m 750 %{buildroot}%{i2p_confdir}

# Log directory
install -d -m 750 %{buildroot}%{i2p_logdir}

%pre
%sysusers_create_compat %{SOURCE2}

%post
%systemd_post i2p.service

%preun
%systemd_preun i2p.service

%postun
%systemd_postun_with_restart i2p.service

%files
# Static application data
%{i2p_home}/
%{i2p_libexec}/

# Systemd integration
%{_unitdir}/i2p.service
%{_sysusersdir}/i2p.conf
%{_tmpfilesdir}/i2p.conf

# Configuration (survives upgrades)
%config(noreplace) %{_sysconfdir}/sysconfig/i2p
%config(noreplace) %{_sysconfdir}/logrotate.d/i2p

# Mutable state and log directories (owned by i2p user)
%attr(750,i2p,i2p) %dir %{i2p_confdir}
%attr(750,i2p,i2p) %dir %{i2p_logdir}

# Documentation
%doc README*
%license LICENSE*

%changelog
* Mon Mar 17 2026 I2P Developers <dev@lists.i2p2.de> - 2.11.0-1
- Update to I2P 2.11.0
- Use virtual java-devel/java-headless deps instead of java-17-openjdk

* Mon Mar 17 2026 I2P Developers <dev@lists.i2p2.de> - 2.7.0-1
- Initial RPM package for I2P
