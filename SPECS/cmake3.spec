# Set to bcond_without or use --with bootstrap if bootstrapping a new release
# or architecture
%bcond_with bootstrap

# Set to bcond_with or use --without gui to disable qt4 gui build
%bcond_without gui

# Setting the Python-version used by default
%if 0%{?rhel} && 0%{?rhel} < 7
%bcond_with python3
%else
%bcond_without python3
%endif

# Do we add appdata-files?
%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_without appdata
%else
%bcond_with appdata
%endif

# Sphinx-build cannot import CMakeLexer on EPEL <= 6
%if 0%{?fedora} || 0%{?rhel} >= 7
%bcond_without sphinx
%else
%bcond_with sphinx
%endif

# Run tests
%bcond_without test

# Verbose test?
%bcond_with debug

# Place rpm-macros into proper location
%global rpm_macros_dir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

# Setup _pkgdocdir if not defined already
%{!?_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

%global major_version 3
%global minor_version 13
# Set to RC version if building RC, else %%{nil}
#global rcver rc1

# Uncomment if building for EPEL
%global name_suffix %{major_version}
%global orig_name cmake

Name:           %{orig_name}%{?name_suffix}
Version:        %{major_version}.%{minor_version}.4
Release:        2%{?dist}
Summary:        Cross-platform make system

# most sources are BSD
# Source/CursesDialog/form/ a bunch is MIT
# Source/kwsys/MD5.c is zlib
# some GPL-licensed bison-generated files, which all include an
# exception granting redistribution under terms of your choice
License:        BSD and MIT and zlib
URL:            http://www.cmake.org
Source0:        http://www.cmake.org/files/v%{major_version}.%{minor_version}/%{orig_name}-%{version}%{?rcver:-%rcver}.tar.gz
Source1:        %{name}-init.el
Source2:        macros.%{name}
# See https://bugzilla.redhat.com/show_bug.cgi?id=1202899
Source3:        %{name}.attr
Source4:        %{name}.prov

# Patch to fix RindRuby vendor settings
# http://public.kitware.com/Bug/view.php?id=12965
# https://bugzilla.redhat.com/show_bug.cgi?id=822796
Patch2:         %{name}-findruby.patch
# replace release flag -O3 with -O2 for fedora
Patch3:         %{name}-fedora-flag_release.patch

# Patch for renaming on EPEL
%if 0%{?name_suffix:1}
Patch1000:      %{name}-rename.patch
Patch1001:      %{name}-libarchive3.patch
%endif

BuildRequires:  gcc-gfortran, gcc-c++
BuildRequires:  ncurses-devel, libX11-devel
BuildRequires:  bzip2-devel
BuildRequires:  curl-devel
BuildRequires:  expat-devel
BuildRequires:  jsoncpp-devel
%if 0%{?fedora} || 0%{?rhel} >= 7
BuildRequires:  libarchive-devel
BuildRequires:  /usr/bin/sphinx-build
BuildRequires:  rhash-devel
BuildRequires:  libuv-devel
%else
BuildRequires:  libarchive3-devel
%endif
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  emacs
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-devel
%else
BuildRequires:  python2-devel
%endif
%if %{without bootstrap}
#BuildRequires: xmlrpc-c-devel
%endif
%if %{with gui}
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires: pkgconfig(Qt5Widgets)
BuildRequires: libappstream-glib
%else
BuildRequires: pkgconfig(QtGui)
%endif
BuildRequires: desktop-file-utils
%global qt_gui --qt-gui
%endif

Requires:       %{name}-data = %{version}-%{release}
Requires:       rpm

# Source/kwsys/MD5.c
# see https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries
Provides: bundled(md5-deutsch)

# https://fedorahosted.org/fpc/ticket/555
Provides: bundled(kwsys)

# cannot do this in epel, ends up replacing os-provided cmake -- Rex
%if 0%{?fedora}
%{?name_suffix:Provides: %{orig_name} = %{version}}
%endif # 0#{?fedora}

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
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: emacs-filesystem >= %{_emacs_version}
%endif

BuildArch:      noarch

%description    data
This package contains common data-files for %{name}.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
This package contains documentation for %{name}.


%package        gui
Summary:        Qt GUI for %{name}

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       hicolor-icon-theme
Requires:       shared-mime-info%{?_isa}

%description    gui
The %{name}-gui package contains the Qt based GUI for %{name}.


%prep
%setup -qn %{orig_name}-%{version}%{?rcver:-%rcver}

# Apply renaming on EPEL before all other patches
%if 0%{?name_suffix:1}
%patch1000 -p1 -b .patch_rename
%if 0%{?rhel} && 0%{?rhel} <= 6
%patch1001 -p1 -b patch_libarchive3
%endif
%endif

# We cannot use backups with patches to Modules as they end up being installed
%patch2 -p1
%patch3 -p1 -b .patch_fedora_flags

%if %{with python3}
echo '#!%{__python3}' > %{name}.prov
%else
echo '#!%{__python2}' > %{name}.prov
%endif
tail -n +2 %{SOURCE4} >> %{name}.prov


%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{__global_ldflags}"
mkdir build
pushd build
../bootstrap --prefix=%{_prefix} --datadir=/share/%{name} \
             --docdir=/share/doc/%{name} --mandir=/share/man \
             --%{?with_bootstrap:no-}system-libs \
             --parallel=`/usr/bin/getconf _NPROCESSORS_ONLN` \
             %{?with_sphinx:--sphinx-man --sphinx-html} \
             %{?qt_gui};
%make_build VERBOSE=1


%install
%make_install -C build
find %{buildroot}%{_datadir}/%{name}/Modules -type f | xargs chmod -x
[ -n "$(find %{buildroot}%{_datadir}/%{name}/Modules -name \*.orig)" ] &&
  echo "Found .orig files in %{_datadir}/%{name}/Modules, rebase patches" &&
  exit 1

# Install major_version name links
%{!?name_suffix:for f in ccmake cmake cpack ctest; do ln -s $f %{buildroot}%{_bindir}/${f}%{major_version}; done}
# Install bash completion symlinks
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
for f in %{buildroot}%{_datadir}/%{name}/completions/*
do
  ln -s ../../%{name}/completions/$(basename $f) %{buildroot}%{_datadir}/bash-completion/completions/
done
# Install emacs cmake mode
mkdir -p %{buildroot}%{_emacs_sitelispdir}/%{name}
install -p -m 0644 Auxiliary/cmake-mode.el %{buildroot}%{_emacs_sitelispdir}/%{name}/%{name}-mode.el
%{_emacs_bytecompile} %{buildroot}%{_emacs_sitelispdir}/%{name}/%{name}-mode.el
mkdir -p %{buildroot}%{_emacs_sitestartdir}
install -p -m 0644 %SOURCE1 %{buildroot}%{_emacs_sitestartdir}/
# RPM macros
install -p -m0644 -D %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.%{name}
sed -i -e "s|@@CMAKE_VERSION@@|%{version}|" -e "s|@@CMAKE_MAJOR_VERSION@@|%{major_version}|" %{buildroot}%{rpm_macros_dir}/macros.%{name}
touch -r %{SOURCE2} %{buildroot}%{rpm_macros_dir}/macros.%{name}
%if 0%{?_rpmconfigdir:1}
# RPM auto provides
install -p -m0644 -D %{SOURCE3} %{buildroot}%{_prefix}/lib/rpm/fileattrs/%{name}.attr
install -p -m0755 -D %{name}.prov %{buildroot}%{_prefix}/lib/rpm/%{name}.prov
%endif
mkdir -p %{buildroot}%{_libdir}/%{name}
# Install copyright files for main package
find Source Utilities -type f -iname copy\* | while read f
do
  fname=$(basename $f)
  dir=$(dirname $f)
  dname=$(basename $dir)
  cp -p $f ./${fname}_${dname}
done
# Cleanup pre-installed documentation
%if 0%{?with_sphinx:1}
mv %{buildroot}%{_docdir}/%{name}/html .
%endif
rm -rf %{buildroot}%{_docdir}/%{name}
# Install documentation to _pkgdocdir
mkdir -p %{buildroot}%{_pkgdocdir}
cp -pr %{buildroot}%{_datadir}/%{name}/Help %{buildroot}%{_pkgdocdir}
mv %{buildroot}%{_pkgdocdir}/Help %{buildroot}%{_pkgdocdir}/rst
%if 0%{?with_sphinx:1}
mv html %{buildroot}%{_pkgdocdir}
%endif

%if %{with gui}
# Desktop file
desktop-file-install --delete-original \
  --dir=%{buildroot}%{_datadir}/applications \
  %{buildroot}/%{_datadir}/applications/CMake%{?name_suffix}.desktop

%if %{with appdata}
# Register as an application to be visible in the software center
#
mkdir -p %{buildroot}%{_metainfodir}
cat > %{buildroot}%{_metainfodir}/CMake3.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2014 Ryan Lerch <rlerch@redhat.com> -->
<!--
EmailAddress: kitware@kitware.com
SentUpstream: 2014-09-17
-->
<application>
  <id type="desktop">CMake3.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <name>CMake GUI</name>
  <summary>Create new CMake projects</summary>
  <description>
    <p>
      CMake is an open source, cross platform build system that can build, test,
      and package software. CMake GUI is a graphical user interface that can
      create and edit CMake projects.
    </p>
  </description>
  <url type="homepage">http://www.cmake.org</url>
  <screenshots>
    <screenshot type="default">https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/CMake/a.png</screenshot>
  </screenshots>
  <!-- FIXME: change this to an upstream email address for spec updates
  <updatecontact>cmake3-owner_at_fedoraproject.org</updatecontact>
   -->
</application>
EOF

appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.appdata.xml
%endif
%endif

%if %{with test}
%check
%if 0%{?rhel} && 0%{?rhel} <= 6
mv -f Modules/FindLibArchive.cmake Modules/FindLibArchive.disabled
%endif
pushd build
#CMake.FileDownload, CTestTestUpload, and curl require internet access
# RunCMake.CPack_RPM is broken if disttag contains "+", bug #1499151
#
# CMakeWizardTest failure: Failed  Required regular expression not found.Regex=[The "cmake -i" wizard mode is no longer supported.
NO_TEST="CMake.FileDownload|CTestTestUpload|curl|RunCMake.CPack_RPM|Server|CMakeWizardTest"
export NO_TEST
%if %{with debug}
bin/ctest%{?name_suffix} -VV --debug %{?_smp_mflags} -E "$NO_TEST"
%else
bin/ctest%{?name_suffix} %{?_smp_mflags} -E "$NO_TEST" 
%endif
popd
%if 0%{?rhel} && 0%{?rhel} <= 6
mv -f Modules/FindLibArchive.disabled Modules/FindLibArchive.cmake
%endif
%endif

%if %{with gui}
%post gui
update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/mime || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun gui
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/mime || :
    update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans gui
update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
%endif

%files
%license Copyright.txt*
%license COPYING*
%{_bindir}/c%{name}
%{!?name_suffix:%{_bindir}/c%{name}%{major_version}}
%{_bindir}/%{name}
%{!?name_suffix:%{_bindir}/%{name}%{major_version}}
%{_bindir}/cpack%{?name_suffix}
%{!?name_suffix:%{_bindir}/cpack%{major_version}}
%{_bindir}/ctest%{?name_suffix}
%{!?name_suffix:%{_bindir}/ctest%{major_version}}
%if 0%{?with_sphinx:1}
%{_mandir}/man1/c%{name}.1.*
%{_mandir}/man1/%{name}.1.*
%{_mandir}/man1/cpack%{?name_suffix}.1.*
%{_mandir}/man1/ctest%{?name_suffix}.1.*
%{_mandir}/man7/*.7.*
%endif
%{_libdir}/%{name}/

%files data
%{_datadir}/aclocal/%{name}.m4
%{_datadir}/bash-completion/
%{_datadir}/%{name}/
%if 0%{?fedora} || 0%{?rhel} >= 7
%{_emacs_sitelispdir}/%{name}
%{_emacs_sitestartdir}/%{name}-init.el
%else
%{_emacs_sitelispdir}
%{_emacs_sitestartdir}
%endif
%{rpm_macros_dir}/macros.%{name}
%if 0%{?_rpmconfigdir:1}
%{_rpmconfigdir}/fileattrs/%{name}.attr
%{_rpmconfigdir}/%{name}.prov
%endif

%files doc
# Pickup license-files from main-pkg's license-dir
# If there's no license-dir they are picked up by %%doc previously
%{?_licensedir:%license %{_datadir}/licenses/%{name}*}
%{_pkgdocdir}/

%if %{with gui}
%files gui
%{_bindir}/%{name}-gui
%if %{with appdata}
%{_metainfodir}/*.appdata.xml
%endif
%{_datadir}/applications/CMake%{?name_suffix}.desktop
%{_datadir}/mime/packages/
%{_datadir}/icons/hicolor/*/apps/CMake%{?name_suffix}Setup.png
%if 0%{?with_sphinx:1}
%{_mandir}/man1/%{name}-gui.1.*
%endif
%endif


%changelog
* Thu Mar 07 2019 Troy Dawson <tdawson@redhat.com> - 3.13.4-2
- Rebuilt to change main python from 3.4 to 3.6

* Sun Feb 03 2019 Antonio Trande <sagitter@fedoraproject.org> - 3.13.4-1
- Update to cmake-3.13.4

* Sat Jan 19 2019 Antonio Trande <sagitter@fedoraproject.org> - 3.13.3-1
- Update to cmake-3.13.3

* Sat Dec 29 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.13.1-1
- Update to cmake-3.13.1
- Use Python3 on epel7
- Perform all tests

* Thu Oct 04 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.12.2-1
- Update to cmake-3.12.2

* Mon Aug 20 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.12.1-1
- Update to cmake-3.12.1

* Fri Jul 27 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.12.0-1
- Update to cmake-3.12.0
- Use %%_metainfodir

* Sat May 19 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.11.2-1
- Update to cmake-3.11.2
- Fix appdata file's entries

* Sat Apr 07 2018 Antonio Trande <sagitter@fedoraproject.org> - 3.11.0-1
- Update to cmake-3.11.0
- Add libuv rhash development packages
- Adapt 'cmake3-rename' patch to CMake-3.11
- Move appdata file into the metainfo sub-data directory

* Thu Feb 09 2017 Orion Poplawski <orion@cora.nwra.com> 3.6.3-1
- Update to 3.6.3
- Fix cmake3.prov error

* Thu Sep 01 2016 Rex Dieter <rdieter@fedoraproject.org> 3.6.1-2
- drop Provides: cmake

* Tue Aug 23 2016 Björn Esser <fedora@besser82.io> - 3.6.1-1
- Update to 3.6.1 (#1353778)

* Fri Apr 22 2016 Björn Esser <fedora@besser82.io> - 3.5.2-2
- Do not own /usr/lib/rpm/fileattrs

* Sat Apr 16 2016 Björn Esser <fedora@besser82.io> - 3.5.2-1
- Update to 3.5.2 (#1327794)

* Fri Mar 25 2016 Björn Esser <fedora@besser82.io> - 3.5.1-1
- Update to 3.5.1 (#1321198)

* Fri Mar 11 2016 Björn Esser <fedora@besser82.io> - 3.5.0-2.1
- fix emacs-filesystem requires for epel6

* Thu Mar 10 2016 Björn Esser <fedora@besser82.io> - 3.5.0-2
- keep Help-directory and its contents in %%_datadir/%%name

* Wed Mar 09 2016 Björn Esser <fedora@besser82.io> - 3.5.0-1.2
- do not provide cmake = %%{version}

* Wed Mar 09 2016 Björn Esser <fedora@besser82.io> - 3.5.0-1.1
- fix macros

* Wed Mar 09 2016 Björn Esser <fedora@besser82.io> - 3.5.0-1
- update to 3.5.0 final

* Tue Mar 08 2016 Björn Esser <fedora@besser82.io> - 3.5.0-0.3.rc3
- bump after review (#1315193)

* Mon Mar 07 2016 Björn Esser <fedora@besser82.io> - 3.5.0-0.2.rc3
- addressing issues from review (#1315193)
  - fix emacs-packaging
  - use %%license-macro
  - fix arch'ed Requires
  - removed BuildRoot
  - use %%global instead of %%define
  - split documentation into noarch'ed doc-subpkg

* Mon Mar 07 2016 Björn Esser <fedora@besser82.io> - 3.5.0-0.1.rc3
- initial epel-release (#1315193)
