#/home/alexd/hasher/repo/x86_64/RPMS.hasher
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

#BuildRequires: python3-module-numpy
#BuildRequires: python3-module-pyvista
#BuildRequires: python3-module-qtpy
#BuildRequires: python3-module-scooby
#BuildRequires: python3-module-vtk

%description
The pyvistaqt module.

%prep
%setup -q

%build
%pyproject_build
 
%install
%pyproject_install 

#useradd -r {%mod_name}_user
echo -e "{%mod_name}_user"

mkdir -p %buildroot/bin/

mkdir -p /var/lib/skud
               
echo -e "%buildroot"
echo -e "%_sysconfdir"

install -Dm0644 %mod_name %buildroot/bin/

mkdir -p %buildroot%_sysconfdir/systemd/user/

cp %name-service.service %buildroot%_sysconfdir/systemd/user/


%files 
%python3_sitelibdir_noarch/%mod_name

#%python3_sitelibdir/%pypi_name-%version.dist-info

%changelog
* Tue Aug 13 2024 jj jj <none@none> 1.0.0-alt1
- fixed build for p11
