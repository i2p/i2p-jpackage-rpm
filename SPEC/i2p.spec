# I2P RPM Spec File
# Produces an installable RPM for the I2P anonymous network router

%global i2p_home    /usr/share/i2p
%global i2p_confdir /var/lib/i2p
%global i2p_logdir  /var/log/i2p
%global i2p_rundir  /run/i2p
%global i2p_libexec /usr/libexec/i2p

Name:           i2p
Version:        2.11.0
Release:        4%{?dist}
Summary:        Anonymous network providing privacy-preserving communication
%if 0%{?suse_version}
Group:          Productivity/Networking/Other
%endif

License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT AND GPL-2.0-only AND GPL-2.0-or-later AND GPL-3.0-only AND LGPL-2.1-only AND EPL-1.0 AND CC-BY-3.0 AND Artistic-2.0
URL:            https://i2p.net/
Source0:        https://github.com/i2p/i2p.i2p/releases/download/i2p-%{version}/i2psource_%{version}.tar.bz2
Source1:        i2p.service
Source2:        i2p.sysusers
Source3:        i2p.tmpfiles
Source4:        i2p.conf
Source5:        i2p-wrapper.sh
Source6:        i2p.logrotate

BuildRequires:  java-devel >= 1:17
BuildRequires:  ant
BuildRequires:  systemd-rpm-macros
%if 0%{?suse_version}
BuildRequires:  gettext-tools
BuildRequires:  sysuser-tools
%else
BuildRequires:  gettext
%endif

Requires:       java-headless >= 1:17
Requires:       logrotate
%if 0%{?suse_version}
Requires(pre):  shadow
%else
Requires(pre):  shadow-utils
%endif

# Disable automatic dependency generation — I2P bundles its own JARs
AutoReqProv:    no

# Bundled libraries that cannot be unbundled (tightly coupled upstream build)
Provides:       bundled(jetty) = 12.0.28
Provides:       bundled(apache-tomcat) = 9.0.107
Provides:       bundled(java-service-wrapper) = 3.5.56
Provides:       bundled(jstl) = 1.2
Provides:       bundled(slf4j) = 2.0.17

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

# Remove pre-built JARs not needed for headless Linux build
# Installer tools (izpack, launch4j) — only used for GUI installer
rm -rf installer/lib/izpack/
rm -rf installer/lib/launch4j/
# Gradle wrapper — we build with ant
rm -f gradle/wrapper/gradle-wrapper.jar

%build
# Build I2P using the pkg target (headless Linux, no installer)
ant preppkg-linux-only \
    -Dfile.encoding=UTF-8 \
    -Djavac.compilerargs="--release 17" \
    -Dbuild.built-by="RPM Build"

%install
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

# Copy eepsite template directory (hidden service webserver config)
cp -a pkg-temp/eepsite/ %{buildroot}%{i2p_home}/ 2>/dev/null || true

# Ensure CGI context is disabled (requires fcgiwrap + extra JARs not in base)
if [ -f %{buildroot}%{i2p_home}/eepsite/contexts/cgi-context.xml ]; then
    mv %{buildroot}%{i2p_home}/eepsite/contexts/cgi-context.xml \
       %{buildroot}%{i2p_home}/eepsite/contexts/cgi-context.xml.disabled
fi

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
%if 0%{?suse_version}
%service_add_pre i2p.service
%sysusers_create_package i2p %{SOURCE2}
%else
%sysusers_create_compat %{SOURCE2}
%endif

%post
%if 0%{?suse_version}
%service_add_post i2p.service
%else
%systemd_post i2p.service
%endif

%preun
%if 0%{?suse_version}
%service_del_preun i2p.service
%else
%systemd_preun i2p.service
%endif

%postun
%if 0%{?suse_version}
%service_del_postun_with_restart i2p.service
%else
%systemd_postun_with_restart i2p.service
%endif

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
* Wed Mar 18 2026 StormyCloud <admin@i2p.net> - 2.11.0-4
- Add openSUSE/SLES conditional macros for multi-distro support
- Add Group tag, sysuser-tools BuildRequires for openSUSE
- Use distro-specific systemd and sysusers scriptlet macros

* Wed Mar 18 2026 StormyCloud <admin@i2p.net> - 2.11.0-3
- Remove pre-built JARs not needed for build (installer, gradle wrapper)
- Add Provides: bundled() for Jetty, Tomcat, JSTL, SLF4J

* Wed Mar 18 2026 StormyCloud <admin@i2p.net> - 2.11.0-2
- Add Requires: logrotate for log rotation config
- Fix URL field to i2p.net
- Remove unnecessary rm -rf buildroot from install
- Add rpmlint suppression config (i2p.rpmlintrc)

* Tue Mar 17 2026 StormyCloud <admin@i2p.net> - 2.11.0-1
- Use virtual java-devel/java-headless deps instead of java-17-openjdk
- Initial RPM package for I2P

