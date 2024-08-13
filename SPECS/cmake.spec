%global package_speccommit 5b6c8efc797f98c1c52d798829067d175e971efe
%global usver 3.26.4
%global xsver 3
%global xsrel %{xsver}%{?xscount}%{?xshash}

# Set to bcond_without or use --with bootstrap if bootstrapping a new release
# or architecture
%bcond_without bootstrap
# Bootstrapping help
%{!?vimfiles_root: %global vimfiles_root %{_datadir}/vim/vimfiles}
%{!?_emacs_sitelispdir: %global _emacs_sitelispdir %{_datadir}/emacs/site-lisp}

# Run git tests
%bcond_without git_test

# Use ncurses for colorful output
%bcond_with ncurses

# Setting the Python-version used by default
%bcond_without python3

# Enable RPM dependency generators for cmake files written in Python
%bcond_without rpm

%bcond_with sphinx

# Possibly change to use non-bundled later
%bcond_without bundled_jsoncpp
%bcond_without bundled_rhash

# Run tests
%bcond_without test

# Disable X11 tests
%bcond_with X11_test

# Do not build non-lto objects to reduce build time significantly.
%global optflags %(echo '%{optflags}' | sed -e 's!-ffat-lto-objects!-fno-fat-lto-objects!g')

# Place rpm-macros into proper location
%global rpm_macros_dir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

# Setup _pkgdocdir if not defined already
%{!?_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

# Setup _vpath_builddir if not defined already
%{!?_vpath_builddir:%global _vpath_builddir %{_target_platform}}

%global major_version 3
%global minor_version 26
%global patch_version 4

# Set to RC version if building RC, else comment out.
#global rcsuf rc1

%if 0%{?rcsuf:1}
%global pkg_version %{major_version}.%{minor_version}.%{patch_version}~%{rcsuf}
%global tar_version %{major_version}.%{minor_version}.%{patch_version}-%{rcsuf}
%else
%global pkg_version %{major_version}.%{minor_version}.%{patch_version}
%global tar_version %{major_version}.%{minor_version}.%{patch_version}
%endif

# For handling bump release by rpmdev-bumpspec and mass rebuild
%global baserelease 4

# Uncomment if building for EPEL/xs8:
%if 0%{?xenserver} < 9
%global name_suffix %%{major_version}
Provides:       cmake
Obsoletes:      cmake
%endif
%global orig_name cmake

Name:           %{orig_name}%{?name_suffix}
Version:        3.26.4
Release: %{?xsrel}%{?dist}
Summary:        Cross-platform make system

# most sources are BSD
# Source/CursesDialog/form/ a bunch is MIT
# Source/kwsys/MD5.c is zlib
# some GPL-licensed bison-generated files, which all include an
# exception granting redistribution under terms of your choice
License:        BSD and MIT and zlib
URL:            http://www.cmake.org
Source0: cmake-3.26.4.tar.gz
Source1: cmake-init.el
Source2: macros.cmake.in
Patch0: cmake-findruby.patch
Patch1: cmake-mingw-dl.patch
Patch2: 0001-Sphinx-Specify-encoding-when-opening-files-for-title.patch
Patch3: 0002-Sphinx-Modernize-UTF-8-encoding-handling-when-updati.patch
Patch4: 0003-Tests-Always-load-presets-schema-as-UTF-8.patch
Patch5: 0004-CMakeDetermineCompilerABI-Avoid-removing-the-flag-af.patch
Patch6: 0005-FindBoost-Add-support-for-Boost-1.82.patch
# See https://bugzilla.redhat.com/show_bug.cgi?id=1202899
Source3: cmake.attr
Source4: cmake.prov
Source5: cmake.req

BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  sed
%if %{with git_test}
# Tests fail if only git-core is installed, bug #1488830
BuildRequires:  git
%else
BuildConflicts: git-core
%endif
%if %{with X11_test}
BuildRequires:  libX11-devel
%endif
%if %{with ncurses}
BuildRequires:  ncurses-devel
%endif
%if %{with sphinx}
BuildRequires:  %{_bindir}/sphinx-build
%endif
%if %{without bootstrap}
BuildRequires:  bzip2-devel
BuildRequires:  curl-devel
BuildRequires:  expat-devel
%if %{with bundled_jsoncpp}
Provides: bundled(jsoncpp)
%else
BuildRequires:  jsoncpp-devel
%endif
BuildRequires:  libarchive-devel
%endif
%if %{with bundled_rhash}
Provides:  bundled(rhash)
%else
BuildRequires:  rhash-devel
%endif
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  vim-filesystem
BuildRequires:  openssl-devel
%if %{with rpm}
%if %{with python3}
%{!?python3_pkgversion: %global python3_pkgversion 3}
BuildRequires:  python%{python3_pkgversion}-devel
%else
BuildRequires:  python2-devel
%endif
%endif

BuildRequires: pkgconfig(bash-completion)
%global bash_completionsdir %(pkg-config --variable=completionsdir bash-completion 2>/dev/null || echo '%{_datadir}/bash-completion/completions')

%if %{without bootstrap}
# Ensure we have our own rpm-macros in place during build.
BuildRequires:  %{name}-rpm-macros
%endif
BuildRequires: make

Requires:       %{name}-data = %{version}-%{release}
Requires:       %{name}-rpm-macros = %{version}-%{release}
Requires:       %{name}-filesystem%{?_isa} = %{version}-%{release}

# Explicitly require make.  (rhbz#1862014)
Requires:       make

# Provide the major version name
Provides: %{orig_name}%{major_version} = %{version}-%{release}

# Source/kwsys/MD5.c
# see https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries
Provides: bundled(md5-deutsch)

# https://fedorahosted.org/fpc/ticket/555
Provides: bundled(kwsys)

%description
CMake is used to control the software compilation process using simple
platform and compiler independent configuration files. CMake generates
native makefiles and workspaces that can be used in the compiler
environment of your choice. CMake is quite sophisticated: it is possible
to support complex environments requiring system configuration, preprocessor
generation, code generation, and template instantiation.


%package        data
Summary:        Common data-files for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-filesystem = %{version}-%{release}
Requires:       %{name}-rpm-macros = %{version}-%{release}
Requires:       vim-filesystem

BuildArch:      noarch

%description    data
This package contains common data-files for %{name}.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
This package contains documentation for %{name}.


%package        filesystem
Summary:        Directories used by CMake modules

%description    filesystem
This package owns all directories used by CMake modules.

%package        rpm-macros
Summary:        Common RPM macros for %{name}
Requires:       rpm
# when subpkg introduced
Conflicts:      cmake-data < 3.10.1-2

BuildArch:      noarch

%description    rpm-macros
This package contains common RPM macros for %{name}.


%prep
%autosetup -n %{orig_name}-%{tar_version} -p 1

%if %{with rpm}
%if %{with python3}
echo '#!%{__python3}' > %{name}.prov
echo '#!%{__python3}' > %{name}.req
%else
echo '#!%{__python2}' > %{name}.prov
echo '#!%{__python2}' > %{name}.req
%endif
tail -n +2 %{SOURCE4} >> %{name}.prov
tail -n +2 %{SOURCE5} >> %{name}.req
%endif


%build
%if 0%{?set_build_flags:1}
%{set_build_flags}
%else
CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS
FFLAGS="${FFLAGS:-%optflags%{?_fmoddir: -I%_fmoddir}}" ; export FFLAGS
FCFLAGS="${FCFLAGS:-%optflags%{?_fmoddir: -I%_fmoddir}}" ; export FCFLAGS
%{?__global_ldflags:LDFLAGS="${LDFLAGS:-%__global_ldflags}" ; export LDFLAGS ;}
%endif
SRCDIR="$(/usr/bin/pwd)"
mkdir %{_vpath_builddir}
pushd %{_vpath_builddir}
$SRCDIR/bootstrap --prefix=%{_prefix} \
                  --datadir=/share/%{name} \
                  --docdir=/share/doc/%{name} \
                  --mandir=/share/man \
                  --%{?with_bootstrap:no-}system-libs \
                  --parallel="$(echo %{?_smp_mflags} | sed -e 's|-j||g')" \
%if %{with bundled_rhash}
                  --no-system-librhash \
%endif
%if %{with bundled_jsoncpp}
                  --no-system-jsoncpp \
%endif
%if %{with sphinx}
                  --sphinx-man --sphinx-html \
%else
                  --sphinx-build=%{_bindir}/false \
%endif
                  --%{!?with_gui:no-}qt-gui \
                  -- \
                  -DCMAKE_C_FLAGS_RELEASE:STRING="-O2 -g -DNDEBUG" \
                  -DCMAKE_CXX_FLAGS_RELEASE:STRING="-O2 -g -DNDEBUG" \
                  -DCMAKE_Fortran_FLAGS_RELEASE:STRING="-O2 -g -DNDEBUG" \
                  -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
                  -DCMAKE_INSTALL_DO_STRIP:BOOL=OFF
popd
%make_build -C %{_vpath_builddir}


%install
mkdir -p %{buildroot}%{_pkgdocdir}
%make_install -C %{_vpath_builddir} CMAKE_DOC_DIR=%{buildroot}%{_pkgdocdir}
find %{buildroot}%{_datadir}/%{name}/Modules -type f | xargs chmod -x
rm -f %{buildroot}%{_datadir}/%{name}/Modules/FindRuby.cmake.orig  # xs8 patch creates it
[ -n "$(find %{buildroot}%{_datadir}/%{name}/Modules -name \*.orig)" ] &&
  echo "Found .orig files in %{_datadir}/%{name}/Modules, rebase patches" &&
  exit 1
# Install major_version name links
%{!?name_suffix:for f in ccmake cmake cpack ctest; do ln -s $f %{buildroot}%{_bindir}/${f}%{major_version}; done}
# The above does nothing for xs8. Do it the old way for xs8:
%if 0%{?xenserver} < 9
%if 0%{?name_suffix} > 0
for f in ccmake cmake cpack ctest; do ln -svf $f %{buildroot}%{_bindir}/${f}%{major_version}; done
%endif
%endif

rm -rf %{buildroot}%{_emacs_sitelispdir}
# RPM macros
install -p -m0644 -D %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.%{name}
sed -i -e "s|@@CMAKE_VERSION@@|%{version}|" -e "s|@@CMAKE_MAJOR_VERSION@@|%{major_version}|" %{buildroot}%{rpm_macros_dir}/macros.%{name}
touch -r %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.%{name}
%if %{with rpm} && 0%{?_rpmconfigdir:1}
# RPM auto provides
install -p -m0644 -D %{SOURCE3} %{buildroot}%{_prefix}/lib/rpm/fileattrs/%{name}.attr
install -p -m0755 -D %{name}.prov %{buildroot}%{_prefix}/lib/rpm/%{name}.prov
install -p -m0755 -D %{name}.req %{buildroot}%{_prefix}/lib/rpm/%{name}.req
%endif
mkdir -p %{buildroot}%{_libdir}/%{orig_name}
# Install copyright files for main package
find Source Utilities -type f -iname copy\* | while read f
do
  fname=$(basename $f)
  dir=$(dirname $f)
  dname=$(basename $dir)
  cp -p $f ./${fname}_${dname}
done
# Cleanup pre-installed documentation
%if %{with sphinx}
mv %{buildroot}%{_docdir}/%{name}/html .
%endif
rm -rf %{buildroot}%{_docdir}/%{name}
# Install documentation to _pkgdocdir
mkdir -p %{buildroot}%{_pkgdocdir}
cp -pr %{buildroot}%{_datadir}/%{name}/Help %{buildroot}%{_pkgdocdir}
mv %{buildroot}%{_pkgdocdir}/Help %{buildroot}%{_pkgdocdir}/rst
%if %{with sphinx}
mv html %{buildroot}%{_pkgdocdir}
%endif

# create manifests for splitting files and directories for filesystem-package
find %{buildroot}%{_datadir}/%{name} -type d | \
  sed -e 's!^%{buildroot}!%%dir "!g' -e 's!$!"!g' > data_dirs.mf
find %{buildroot}%{_datadir}/%{name} -type f | \
  sed -e 's!^%{buildroot}!"!g' -e 's!$!"!g' > data_files.mf
find %{buildroot}%{_libdir}/%{orig_name} -type d | \
  sed -e 's!^%{buildroot}!%%dir "!g' -e 's!$!"!g' > lib_dirs.mf
find %{buildroot}%{_libdir}/%{orig_name} -type f | \
  sed -e 's!^%{buildroot}!"!g' -e 's!$!"!g' > lib_files.mf
find %{buildroot}%{_bindir} -type f -or -type l -or -xtype l | \
  sed -e '/.*-gui$/d' -e '/^$/d' -e 's!^%{buildroot}!"!g' -e 's!$!"!g' >> lib_files.mf


%if %{with test}
%check
pushd %{_vpath_builddir}
# CTestTestUpload requires internet access.
NO_TEST="CTestTestUpload"
# Likely failing for hardening flags from system.
NO_TEST="$NO_TEST|CustomCommand|RunCMake.PositionIndependentCode"
# Failing for rpm 4.19
NO_TEST="$NO_TEST|CPackComponentsForAll-RPM-default"
NO_TEST="$NO_TEST|CPackComponentsForAll-RPM-OnePackPerGroup"
NO_TEST="$NO_TEST|CPackComponentsForAll-RPM-AllInOne"
# curl test may fail during bootstrap
%if %{with bootstrap}
NO_TEST="$NO_TEST|curl"
%endif
%ifarch riscv64
# These three tests timeout on riscv64, skip them.
NO_TEST="$NO_TEST|Qt5Autogen.ManySources|Qt5Autogen.MocInclude|Qt5Autogen.MocIncludeSymlink"
%endif
bin/ctest %{?_smp_mflags} -V -E "$NO_TEST" --output-on-failure
## do this only periodically, not for every build -- besser82 20221102
# Keep an eye on failing tests
#bin/ctest %{?_smp_mflags} -V -R "$NO_TEST" --output-on-failure || :
popd
%endif


%files -f lib_files.mf
%doc %dir %{_pkgdocdir}
%license Copyright.txt*
%license COPYING*
%if %{with sphinx}
%{_mandir}/man1/c%{name}.1.*
%{_mandir}/man1/%{name}.1.*
%{_mandir}/man1/cpack%{?name_suffix}.1.*
%{_mandir}/man1/ctest%{?name_suffix}.1.*
%{_mandir}/man7/*.7.*
%endif


%files data -f data_files.mf
%{_datadir}/aclocal/%{orig_name}.m4
%{bash_completionsdir}/c*
%{vimfiles_root}/indent/%{orig_name}.vim
%{vimfiles_root}/syntax/%{orig_name}.vim


%files doc
# Pickup license-files from main-pkg's license-dir
# If there's no license-dir they are picked up by %%doc previously
%{?_licensedir:%license %{_datadir}/licenses/%{name}*}
%doc %{_pkgdocdir}


%files filesystem -f data_dirs.mf -f lib_dirs.mf


%files rpm-macros
%{rpm_macros_dir}/macros.%{name}
%if %{with rpm} && 0%{?_rpmconfigdir:1}
%{_rpmconfigdir}/fileattrs/%{name}.attr
%{_rpmconfigdir}/%{name}.prov
%{_rpmconfigdir}/%{name}.req
%endif


%changelog
* Fri Apr 12 2024 Bernhard Kaindl <bernhard.kaindl@cloud.com> - 3.26.4-3
- CP-40289/XS8: Fix cmake3.rpm to provide and obsolete cmake to fix conflict
* Fri Nov 10 2023 Bernhard Kaindl <bernhard.kaindl@cloud.com> - 3.26.4-2
- Create cmake3{,-subpackages}-%.rpms for XS8 to complement cmake2 rpms
* Mon Jun 26 2023 Tim Smith <tim.smith@citrix.com> - 3.26.4-1
- First imported release

