#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl.UTF-8):	Moduł do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich właścicieli
Name:		apache1-mod_%{mod_name}
Version:	0.6.1
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz
# Source0-md5:	7eb8ae29404392d9eb07c69d5242d716
Source1:	%{name}.logrotate
Source2:	%{name}.conf
Source2:	%{name}-suphp.conf
Patch0:		%{name}-apr.patch
Patch1:		%{name}-notallowed.patch
URL:		http://www.suphp.org/
BuildRequires:	apache1-apxs
BuildRequires:	apache1-devel >= 1.3.33-2
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(triggerpostun):	%{apxs}
Requires(triggerpostun):	grep
Requires(triggerpostun):	sed >= 4.0
Requires:	apache1
Requires:	php-cgi
Conflicts:	logrotate < 3.7-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
suPHP is a tool for executing PHP scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp) and a setuid
root binary (suphp) that is called by the Apache module to change the
uid of the process executing the PHP interpreter.

%description -l pl.UTF-8
suPHP jest narzędziem pozwalającym na wykonywanie skryptów w PHP z
uprawnieniami ich właścicieli. Składa się z modułu (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
moduł w celu zmiany uid procesu uruchamiającego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
export APACHE_VERSION=$(rpm -q --qf '%%{version}' apache1-apxs)
%configure \
	%{?with_checkpath: --enable-checkpath} \
	%{!?with_checkpath: --disable-checkpath} \
	--with-apache-user=http \
	--with-min-uid=500 \
	--with-min-gid=1000 \
	--with-apxs=%{apxs} \
	--disable-checkuid \
	--disable-checkgid \
	--with-setid-mode=owner \
	--with-logfile=/var/log/apache/suphp_log

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir},%{_sysconfdir}/conf.d}

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache/.libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{mod_name}.conf

install -d $RPM_BUILD_ROOT/etc/logrotate.d
# TODO: apache1-mod_suphp + trigger
install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q apache restart

%postun
if [ "$1" = "0" ]; then
	%service -q apache restart
fi

# TODO remove the trigger, if no longer needed
%triggerpostun -- %{name} <= 0.5.2-1
if grep -q '^Include conf\.d' /etc/apache/apache.conf; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	sed -i -e '
		/^Include.*mod_%{mod_name}\.conf/d
	' /etc/apache/apache.conf

	%service -q apache restart
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README doc
%attr(4755,root,root) %{_sbindir}/suphp
%attr(755,root,root) %{_pkglibdir}/*.so
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{mod_name}.conf
