#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl):	Modu³ do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich w³a¶cicieli
Name:		apache1-mod_%{mod_name}
Version:	0.5.2
Release:	1.12
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz
# Source0-md5:	337909e87027af124052baddddbd2994
Source1:	%{name}.conf
Source2:	%{name}.logrotate
URL:		http://www.suphp.org/
BuildRequires:	apache1-devel >= 1.3.33-2
BuildRequires:	autoconf
BuildRequires:	automake
Requires(triggerpostun):	%{apxs}
Requires(triggerpostun):	grep
Requires(triggerpostun):	sed >= 4.0
Requires:	apache
Requires:	php-cgi
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
suPHP is a tool for executing PHP scripts with the permissions of
their owners. It consists of an Apache module (mod_suphp) and a setuid
root binary (suphp) that is called by the Apache module to change the
uid of the process executing the PHP interpreter.

%description -l pl
suPHP jest narzêdziem pozwalaj±cym na wykonywanie skryptów w PHP z
uprawnieniami ich w³a¶cicieli. Sk³ada siê z modu³u (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
modu³ w celu zmiany uid procesu uruchamiaj±cego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}

# common GPL license
rm -f doc/{de,en}/LICENSE
# common Apache license
rm -f doc/{de,en}/apache/LICENSE

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
chmod 755 configure
%configure \
	%{?with_checkpath: --enable-checkpath} \
	%{!?with_checkpath: --disable-checkpath} \
	--with-apache-user=http \
	--with-min-uid=500 \
	--with-min-gid=1000 \
	--with-apxs=%{apxs} \
	--with-php=/usr/bin/php.cgi \
	--disable-checkuid \
	--disable-checkgid

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir},%{_sysconfdir}/conf.d}

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf

install -d $RPM_BUILD_ROOT/etc/logrotate.d
# TODO: apache1-mod_suphp + trigger
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q apache restart

%preun
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
%doc AUTHORS ChangeLog doc/en doc/de
%attr(4755,root,root) %{_sbindir}/suphp
%attr(755,root,root) %{_pkglibdir}/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
