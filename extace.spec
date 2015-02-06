%define name     extace
%define title    eXtace
%define mainname %{name}
%define alsaname %{name}-alsa
%define ossname	 %{name}-oss
%define version  1.9.6
%define release  6
%define descr    %{title} - An Extace Waveform Viewer
%define summalsa %{descr} with ALSA support
%define summoss  %{descr} without ALSA support
%define group    Sound
%define section  Multimedia/%{group}
%define iconname multimedia_section.png
# Change to 1 if ALSA compiles cleanly again
%define buildalsa 0

Summary:         Visual sound display/analysis program
Name:            %{name}
Version:         %{version}
Release:         %{release}
Source:          %{name}-%{version}.tar.bz2
Patch0:		 extace-1.9.6-desktop-file.patch
License:	 GPL
Group:           %{group}
BuildRoot:       %{tmppath_}/%{name}-%{version}-%{release}-buildroot
Requires:        gnome-libs >= 1.0.11, esound
BuildRequires:   fftw3-devel
BuildRequires:   alsa-lib
BuildRequires:   coreutils
BuildRequires:   perl
BuildRequires:   gtk-devel
BuildRequires:   esound-devel
BuildRequires:   imlib-devel
BuildRequires:   gdkimlib-devel
BuildRequires:   desktop-file-utils
BuildRequires:   imagemagick
#Obsoletes:       %{alsaname}
URL:		 http://extace.sf.net

%description
eXtace is a visual sound display/analysis program for the Gnome Desktop
environment (though it works under other environments as long as gnome/esd
installed and used). Requires ESD to function. Includes
various fourier transforms of the audio data in real-time. Displays include
3D textured flying landscape, 16-128 channel graphic EQ, scope, and a 3D
pointed flying landscape. All aspects of the display are fully configurable,
even the axis placement. 

%if %{buildalsa}
This version is for users who don't use ALSA.
%endif

%if %{buildalsa}
%package alsa
Summary:         %{summalsa}
Group:           %{group}
Obsoletes:       %{mainname}

%description alsa
eXtace is a visual sound display/analysis program for the Gnome Desktop
environment (though it works under other environments as long as gnome/esd
or ALSA is installed and used). Requires ESD or ALSA to function. Includes
various fourier transforms of the audio data in real-time. Displays include
3D textured flying landscape, 16-128 channel graphic EQ, scope, and a 3D
pointed flying landscape. All aspects of the display are fully configurable,
even the axis placement. 

This version is for users who use ALSA.
%endif

%prep
# remove build directories.  better do it by hand as I later on move
# them around
rm -fr $RPM_BUILD_DIR/%{name}-%{version} $RPM_BUILD_DIR/%{alsaname}

# Unpack main source
%setup -q
%patch0 -p1

%if %{buildalsa}
	# Copy source tree to dir %{alsaname} for later building the alsa version
	cp -a $RPM_BUILD_DIR/%{name}-%{version} $RPM_BUILD_DIR/%{alsaname}
%endif

%build
# First build the normal/OSS version, and force to ignore ALSA even if present
%configure2_5x --disable-alsa --disable-rpath
# Remove ALSA support from this build
perl -pi -e 's|(^#define HAVE_ALSA.*$)|/* $1 */|' config.h
for f in {extace,.}/Makefile ; do
	perl -pi -e 's|(^ALSA_LIBS\s+=\s+).*$|$1|' $f
	perl -pi -e 's|-lasound||' $f
done
%make

%if %{buildalsa}
	# Now build the ALSA version.  ALSA support is built by default if available
	cd $RPM_BUILD_DIR/%{alsaname}
	%configure2_5x --disable-rpath
	%make
%endif

%install
rm -rf %buildroot

# First install the OSS version
%makeinstall

mkdir -p %{buildroot}%{_bindir}

# Use /etc/alternatives to have it point to the right binary
# The "normal" one is named extace-oss, the alsa bin is called extace-alsa
mv %{buildroot}%{_bindir}/%{name} %buildroot%{_bindir}/%{ossname}

%if %{buildalsa}
	# And now install the alsa version
	cd $RPM_BUILD_DIR/%{alsaname}
	%makeinstall
	# Rename the binary so that it doesn't overwrite the pointer to /etc/alternatives
	mv %{buildroot}%{_bindir}/%{name} %buildroot%{_bindir}/%{alsaname}
%endif

mkdir -p %buildroot%_datadir/applications/
desktop-file-install --vendor='' \
	--dir=%buildroot%_datadir/applications/ \
	%buildroot%_datadir/gnome/apps/Multimedia/extace.desktop

rm -f %buildroot%_datadir/gnome/apps/Multimedia/extace.desktop

mkdir -p %buildroot%_iconsdir/
convert src/logo.xpm %buildroot%_iconsdir/%{name}.png

%post
# Update /etc/alternatives to point to the right binary file
update-alternatives --install %{_bindir}/%{name} %{name} %{_bindir}/%{ossname} 100

# Only in Mandriva:
# Update menus
%if %mdkversion < 200900
%{update_menus}
%endif

%postun
update-alternatives --remove %{name} %{_bindir}/%{ossname}

# Only in Mandriva:
# Remove the menu entry
%if %mdkversion < 200900
%{clean_menus}
%endif

%if %{buildalsa}
	%post alsa
	# Update /etc/alternatives to point to the right binary file
	update-alternatives --install %{_bindir}/%{name} %{name} %{_bindir}/%{alsaname} 200

	# Only in Mandriva:
	# Update menus
%if %mdkversion < 200900
	%{update_menus}
%endif

	%postun alsa
	update-alternatives --remove %{name} %{_bindir}/%{alsaname}

	# Only in Mandriva:
	# Remove the menu entry
%if %mdkversion < 200900
	%{clean_menus}
%endif
%endif

%clean
rm -rf %buildroot

%files
%defattr(-,root,root,0755)
%doc TODO AUTHORS CREDITS NEWS ChangeLog README
%{_bindir}/%{ossname}
%{_datadir}/applications/extace.desktop
%{_iconsdir}/*.png

%if %{buildalsa}
%files alsa
%defattr(-,root,root,0755)
%{_bindir}/%{alsaname}
%endif


%changelog
* Thu Sep 03 2009 Thierry Vignaud <tvignaud@mandriva.com> 1.9.6-5mdv2010.0
+ Revision: 428659
- rebuild

  + Oden Eriksson <oeriksson@mandriva.com>
    - lowercase ImageMagick

* Thu Jul 24 2008 Thierry Vignaud <tvignaud@mandriva.com> 1.9.6-4mdv2009.0
+ Revision: 245006
- rebuild

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Thu Feb 14 2008 Thierry Vignaud <tvignaud@mandriva.com> 1.9.6-2mdv2008.1
+ Revision: 168126
- put a real summary
- kill re-definition of %%buildroot on Pixel's request
- s/Mandrake/Mandriva/

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Aug 23 2007 Thierry Vignaud <tvignaud@mandriva.com> 1.9.6-2mdv2008.0
+ Revision: 70213
- fileutils, sh-utils & textutils have been obsoleted by coreutils a long time ago

* Fri Aug 10 2007 Funda Wang <fundawang@mandriva.org> 1.9.6-1mdv2008.0
+ Revision: 61422
- Add desktop-file patch
- fix file list
- use xdg menu item
- New version 1.9.6

  + Nicolas LÃ©cureuil <neoclust@mandriva.org>
    - Import extace



* Tue May  9 2006 Götz Waschk <waschk@mandriva.org> 1.8.11-4mdk
- fix buildrequires

* Thu Oct 06 2005 Nicolas Lécureuil <neoclust@mandriva.org> 1.8.11-3mdk
- Fix BuildRequires
- %%mkrel 

* Fri Sep 10 2004 Lenny Cartier <lenny@mandrakesoft.com> 1.8.11-2mdk
- rebuild

* Wed Aug 20 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.8.11-1mdk
- 1.8.11

* Tue Jan 28 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.6.4-3mdk
- rebuild

* Tue Sep 03 2002 Lenny Cartier <lenny@mandrakesoft.com> 1.6.4-2mdk
- rebuild

* Tue Jan 15 2002 Alexander Skwar <ASkwar@Linux-Mandrake.com> 1.6.4-1mdk
- 1.6.4
- Actually *use* update-alternatives and not only pretend to do so
- alsa subpackage now only contains the alsa binary, thanks to ua
- Remove ALSA support, because ALSA 0.5.x doesn't seem to be supported
  by extace anymore

* Thu Sep 13 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.6.1-1mdk
- 1.6.1

* Thu Jul 05 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.5.1-1mdk
- updated to 1.5.1

* Tue Jan 02 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.4.5-1mdk
- updated to 1.4.5

* Fri Dec 15 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.4.4-1mdk
- updated to 1.4.4

* Tue Dec 5 2000 Daouda Lo <daouda@mandrakesoft.com> 1.4.0-1mdk
- update

* Sun Nov 05 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.3.11-1mdk
- updated to 1.3.11

* Thu Oct 26 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.3.9-1mdk
- updated to 1.3.9

* Wed Oct 18 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.3.8-1mdk
- used srpm from Alexander Skwar <ASkwar@Linux-Mandrake.com> :
	Fri Oct 13 2000 Alexander Skwar <ASkwar@Linux-Mandrake.com> 1.3.8-1mdk
	New version
	Split up in a alsa and non-alsa version, ie. it will create two
  	binary packages
	Use %%{_sysconfdir}/alternatives to have it point to the right binary

* Mon Sep 18 2000 Alexander Skwar <ASkwar@DigitalProjects.com> 1.3.4-1mdk
- New version
- Now with ALSA support
- Hardcoded to use ALSA card 0, Device 0 and Sub Chan 1

* Sun Aug 27 2000 Alexander Skwar <ASkwar@DigitalProjects.com> 1.3.2-1mdk
- New version
- (Build-)requires fftw

* Wed Apr 26 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.2.0-2mdk
- fix group
- spec helper fixes

* Wed Sep 08 1999 Daouda LO <daouda@mandrakesoft.com>
- 1.2.0 

* Tue Jul 20 1999 Chmouel Boudjnah <chmouel@mandrakesoft.com>
- Initalisation of spec file for Mandrake distribution.
