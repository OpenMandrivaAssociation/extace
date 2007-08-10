%define name     extace
%define title    eXtace
%define mainname %{name}
%define alsaname %{name}-alsa
%define ossname	 %{name}-oss
%define version  1.9.6
%define release  %mkrel 1
%define descr    %{title} - An Extace Waveform Viewer
%define summalsa %{descr} with ALSA support
%define summoss  %{descr} without ALSA support
%define group    Sound
%define section  Multimedia/%{group}
%define iconname multimedia_section.png
# Change to 1 if ALSA compiles cleanly again
%define buildalsa 0

Summary:         %{summoss}
Name:            %{name}
Version:         %{version}
Release:         %{release}
Source:          %{name}-%{version}.tar.bz2
License:	 GPL
Group:           %{group}
BuildRoot:       %{tmppath_}/%{name}-%{version}-%{release}-buildroot
Requires:        gnome-libs >= 1.0.11, esound
BuildRequires:   fftw3-devel
BuildRequires:   alsa-lib
BuildRequires:   fileutils
BuildRequires:   perl
BuildRequires:   gtk-devel
BuildRequires:   esound-devel
BuildRequires:   imlib-devel
BuildRequires:   gdkimlib-devel
BuildRequires:   desktop-file-utils
BuildRequires:   ImageMagick
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
	--add-category='Audio;AudioVideo;AudioVideoEditing' \
	%buildroot%_datadir/gnome/apps/Multimedia/extace.desktop

rm -f %buildroot%_datadir/gnome/apps/Multimedia/extace.desktop

mkdir -p %buildroot%_iconsdir/
convert src/logo.xpm %buildroot%_iconsdir/%{name}.png

%post
# Update /etc/alternatives to point to the right binary file
update-alternatives --install %{_bindir}/%{name} %{name} %{_bindir}/%{ossname} 100

# Only in Mandrake:
# Update menus
%{update_menus}

%postun
update-alternatives --remove %{name} %{_bindir}/%{ossname}

# Only in Mandrake:
# Remove the menu entry
%{clean_menus}

%if %{buildalsa}
	%post alsa
	# Update /etc/alternatives to point to the right binary file
	update-alternatives --install %{_bindir}/%{name} %{name} %{_bindir}/%{alsaname} 200

	# Only in Mandrake:
	# Update menus
	%{update_menus}

	%postun alsa
	update-alternatives --remove %{name} %{_bindir}/%{alsaname}

	# Only in Mandrake:
	# Remove the menu entry
	%{clean_menus}
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
