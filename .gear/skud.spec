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

#mkdir -p %buildroot/bin/
mkdir -p %buildroot%{_sharedstatedir}/skud
               
echo -e "%buildroot"
echo -e "%_sysconfdir"
echo -e "%buildroot%_sysconfdir"
pwd 
ls -al
#cd SKUD && ls -al && cd ..
chmod u+x skud.py
mv skud.py skud
mkdir -p %buildroot%_bindir
cp skud %buildroot%_bindir/
#cd SKUD

#install -Dm0755 -v main.py \
#    %buildroot%python3_sitelibdir_noarch/SKUD
#install -Dm0755 -v service.py \
#    %buildroot%python3_sitelibdir_noarch/SKUD
#mkdir -p %buildroot%python3_sitelibdir_noarch/SKUD/controllers

#install -Dm0755 -v ORM/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/ORM/
#install -Dm0755 -v general/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/general/
#install -Dm0755 -v remote/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/remote/
#install -Dm0755 -v hardware/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/hardware/
#install -Dm0755 -v controllers/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/controllers/
#install -Dm0755 -v dbscript/* \
#    %buildroot%python3_sitelibdir_noarch/SKUD/dbscript/
#cd ..

export PYTHONPATH=%_sourcedir
mkdir -p %buildroot%_sysconfdir/systemd/user/

cp %name-service.service %buildroot%_sysconfdir/systemd/user/

cd %buildroot%python3_sitelibdir_noarch/SKUD
ls -al
cd %buildroot%python3_sitelibdir_noarch/SKUD/dbscripts
ls -al

%files 
%python3_sitelibdir_noarch/
%{_bindir}/skud
%_sysconfdir/systemd/user/
%{_sharedstatedir}/skud

#%python3_sitelibdir_noarch/SKUD/ORM
#%python3_sitelibdir_noarch/SKUD/general
#%python3_sitelibdir_noarch/SKUD/remote
#%python3_sitelibdir_noarch/SKUD/hardware
#%python3_sitelibdir_noarch/SKUD/controllers

#%python3_sitelibdir/%pypi_name-%version.dist-info

%changelog
* Mon Sep 2 2024 none none <none@none> 1.0.0-alt1
- fixed build for p11
