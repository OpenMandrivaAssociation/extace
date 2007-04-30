%define name     extace
%define title    eXtace
%define mainname %{name}
%define alsaname %{name}-alsa
%define ossname	 %{name}-oss
%define version  1.8.11
%define release  %mkrel 4
%define descr    %{title} - An Extace Waveform Viewer
%define summalsa %{descr} with ALSA support
%define summoss  %{descr} without ALSA support
%define group    Sound
%define section  Multimedia/%{group}
%define iconname multimedia_section.png
# Change to 1 if ALSA compiles cleanly again
%define buildalsa 0

# Needed for building generic packages
# Not too sure if these are defined in non-Mandrake distributions:
# %{_exec_prefix}/bin -> /usr/bin
%define bindir_  %{_bindir}
# ~/RPM/tmp
%define tmppath_ %{_tmppath}
# %{_prefix}/share -> /usr/share
%define datadir_ %{_datadir}
# %{_libdir}/menu -> %{_exec_prefix}/%{_lib}/menu -> /usr/lib/menu
%define menudir_ %{_menudir}

Summary:         %{summoss}
Name:            %{name}
Version:         %{version}
Release:         %{release}
Source:          %{name}-%{version}.tar.bz2
License:	 GPL
Group:           %{group}
BuildRoot:       %{tmppath_}/%{name}-%{version}-%{release}-buildroot
Requires:        gnome-libs >= 1.0.11, esound
BuildRequires:   fftw2-devel
BuildRequires:   alsa-lib
BuildRequires:   fileutils
BuildRequires:   perl
BuildRequires:   gtk-devel
BuildRequires:   esound-devel
BuildRequires:   imlib-devel
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
Requires:        gnome-libs >= 1.0.11, fftw, esound, alsa
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
%configure --disable-alsa --disable-rpath
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
	%configure --disable-rpath
	%make
%endif

%install
rm -rf %buildroot

# First install the OSS version
%makeinstall

mkdir -p %{buildroot}%{bindir_}

# Use /etc/alternatives to have it point to the right binary
# The "normal" one is named extace-oss, the alsa bin is called extace-alsa
mv %{buildroot}%{bindir_}/%{name} %buildroot%{bindir_}/%{ossname}

%if %{buildalsa}
	# And now install the alsa version
	cd $RPM_BUILD_DIR/%{alsaname}
	%makeinstall
	# Rename the binary so that it doesn't overwrite the pointer to /etc/alternatives
	mv %{buildroot}%{bindir_}/%{name} %buildroot%{bindir_}/%{alsaname}
%endif

# Copy another nice utility.  This one creates a sine-wave.  Turn you phones to
# LOUD when you use this.... :-]
#cp extace/sine %buildroot%{bindir_}

# Only in Mandrake:
# Create menu entry for the package
mkdir -p %{buildroot}%{menudir_}
cat - << EOF > %buildroot%{menudir_}/%{name}
?package(%{name}):command="%{bindir_}/%{name}-oss" \
                 needs="X11" section="%{section}" title="%{title}" \
                 icon="%{iconname}" longtitle="%{descr}"
EOF

%post
# Update /etc/alternatives to point to the right binary file
update-alternatives --install %{bindir_}/%{name} %{name} %{bindir_}/%{ossname} 100

# Only in Mandrake:
# Update menus
%{update_menus}

%postun
update-alternatives --remove %{name} %{bindir_}/%{ossname}

# Only in Mandrake:
# Remove the menu entry
%{clean_menus}

%if %{buildalsa}
	%post alsa
	# Update /etc/alternatives to point to the right binary file
	update-alternatives --install %{bindir_}/%{name} %{name} %{bindir_}/%{alsaname} 200

	# Only in Mandrake:
	# Update menus
	%{update_menus}

	%postun alsa
	update-alternatives --remove %{name} %{bindir_}/%{alsaname}

	# Only in Mandrake:
	# Remove the menu entry
	%{clean_menus}
%endif

%clean
rm -rf %buildroot
rm -fr $RPM_BUILD_DIR/%{name}-%{version} $RPM_BUILD_DIR/%{alsaname}

%files
%defattr(-,root,root,0755)
%doc TODO AUTHORS CREDITS NEWS ChangeLog README
#%{bindir_}/extace
%{bindir_}/%{ossname}
#%{bindir_}/sine
%{datadir_}/gnome/apps/Multimedia/extace.desktop
# Only Mandrake:
%{menudir_}/%{name}

%if %{buildalsa}
%files alsa
%defattr(-,root,root,0755)
%{bindir_}/%{alsaname}
%endif
