# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           spiff
Version:        0.1.0
Release:        1%{?dist}
Summary:        Spaceman Spiff Manages Spaces

License:        AGPLv2
URL:            http://github.com/synhak/spiff
Source0:        %{name}-%{version}.tar.bz2

BuildArch:      noarch
BuildRequires:  python-devel

%description
Spaceman Spiff Manages Spaces

%package -n python-spiff
Summary:        Python client to Spiff

%description -n python-spiff
Python client to Spiff

%package bonehead-plugin
Summary:        A bonehead plugin for Spiff
Requires:       bonehead = 0.1.0

%description bonehead-plugin
A bonehead plugin for Spiff


%prep
%setup -q


%build
cd client/python/
# Remove CFLAGS=... for noarch packages (unneeded)
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
cd client/python/
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

cd ../bonehead/
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%files -n python-spiff
%doc
# For noarch packages: sitelib
%{python_sitelib}/*

%files bonehead-plugin
%{_datadir}/bonehead/plugins/*


%changelog
