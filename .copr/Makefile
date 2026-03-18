# COPR SCM build integration
# COPR calls: make srpm outdir=/path/to/output

VERSION ?= 2.11.0

srpm:
	./scripts/fetch-source.sh $(VERSION) SOURCES/
	mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cp SOURCES/* rpmbuild/SOURCES/
	cp SPEC/i2p.spec rpmbuild/SPECS/
	sed -i 's/^Version:.*/Version:        $(VERSION)/' rpmbuild/SPECS/i2p.spec
	rpmbuild -bs \
		--define "_topdir $(shell pwd)/rpmbuild" \
		--define "_sourcedir $(shell pwd)/rpmbuild/SOURCES" \
		rpmbuild/SPECS/i2p.spec
	cp rpmbuild/SRPMS/*.src.rpm $(outdir)
