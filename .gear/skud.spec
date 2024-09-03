#/home/YOUR_USER/hasher/repo/x86_64/RPMS.hasher
%define pypi_name skud
%define mod_name %pypi_name

Name: %mod_name
Version: 1.0.0
Release: alt1
Summary: The skud prj
License: MIT
Group: Development/Python3

Source0: %name-%version.tar

%py3_provides %pypi_name

BuildRequires(pre): rpm-build-pyproject

# build backend and its deps
BuildRequires: python3-module-setuptools
BuildRequires: python3-module-wheel

%description
The pyvistaqt module.

%prep
%setup -q

%build
%pyproject_build
 
%install
%pyproject_install 

#useradd -r {%mod_name}_user

mkdir -p %buildroot%{_sharedstatedir}/skud
mkdir -p %buildroot%{_sysconfdir}/skud
touch %buildroot%{_sysconfdir}/skud/enabled
touch %buildroot%{_sysconfdir}/skud/global-settings.json

chmod u+x skud.py
mv skud.py skud

mkdir -p %buildroot%_bindir
cp skud %buildroot%_bindir/

#export PYTHONPATH=%_sourcedir
mkdir -p %buildroot%_sysconfdir/systemd/user/

cp %name-service.service %buildroot%_sysconfdir/systemd/user/

%files 
%python3_sitelibdir_noarch/
%{_bindir}/skud
%_sysconfdir/systemd/user/
%{_sysconfdir}/skud/enabled
%{_sysconfdir}/skud/global-settings.json

%changelog
* Mon Sep 2 2024 none none <none@none> 1.0.0-alt1
- fixed build for p11
