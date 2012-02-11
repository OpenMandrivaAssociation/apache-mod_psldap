#Module-Specific definitions
%define mod_name mod_psldap
%define mod_conf B57_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A LDAP authentication module for apache
Name:		apache-%{mod_name}
Version:	0.94
Release: 	%mkrel 4
Group:		System/Servers
License:	GPL
URL:		http://sourceforge.net/projects/mod-psldap/
Source0:	http://garr.dl.sourceforge.net/project/mod-psldap/mod-psldap/mod-psldap%20%{version}/mod_psldap-%{version}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	libxml2-devel
BuildRequires:	libxslt-devel
BuildRequires:	openldap-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_psldap is an Apache module that performs authentication authorization
against an LDAP server using several different means of managing the
authentication and authorization processes. This implementation can also manage
records through a Web interface, and authenticate against an LDAP server that
restricts the user from reading the password and the implementation of
Kerberos-based authentication to connect to the LDAP server itself.

%prep

%setup -q -n %{mod_name}
cp %{SOURCE1} %{mod_conf}

find -type f | xargs chmod 644

# fix version
perl -pi -e "s|^#define PSLDAP_VERSION_LABEL .*|#define PSLDAP_VERSION_LABEL \"%{version}\"|g" %{mod_name}.c

%build
sh ./configure
%{_sbindir}/apxs -I%{_includedir}/libxml2 \
    -I%{_includedir}/libxslt -DUSE_LIBXML2_LIBXSL \
    -c %{mod_name}.c -lldap -llber -lxml2 -lxslt

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog FAQ.html README RELEASE psind.schema psldap.schema
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

