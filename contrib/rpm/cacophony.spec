%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           python-cacophony
Version:        0.0.1
Release:        1%{?dist}
Summary:        Simple REST Api for automagic SSL certificate generation

License:        AGPLv3+
URL:            https://github.com/RHInception/cacophony
Source0:        cacophony-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       python-flask>=0.9, pyOpenSSL>=0.13.1


%description
Simple REST Api for automagic SSL certificate generation.


%prep
%setup -q -n cacophony-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_datarootdir}/cacophony/{mod_wsgi,test-ca-script}/
cp -rf contrib/mod_wsgi/* $RPM_BUILD_ROOT/%{_datarootdir}/cacophony/mod_wsgi/
cp -rf contrib/test-ca-script/* $RPM_BUILD_ROOT/%{_datarootdir}/cacophony/test-ca-script/


%files
%doc README.md LICENSE
%{python_sitelib}/*
%{_datarootdir}/cacophony/*


%changelog
* Wed Feb 26 2014 Steve Milner <stevem@gnulinux.net>- 0.0.1-1
- Initial spec
