#
# Available build options:
%bcond_with	checkpath	# enable check if php execution is within
				# DOCUMENT_ROOT of the vhost
#
%define		mod_name	suphp
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: suPHP - execute PHP scripts with the permissions of their owners
Summary(pl):	Modu³ do apache: suPHP - uruchamianie skryptów PHP z uprawnieniami ich w³a¶cicieli
Name:		apache1-mod_%{mod_name}
Version:	0.5.2
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.suphp.org/download/%{mod_name}-%{version}.tar.gz	
# Source0-md5:	337909e87027af124052baddddbd2994
Source1:	%{name}.logrotate
Source2:	%{name}.conf
URL:		http://www.suphp.org/
BuildRequires:	%{apxs}
BuildRequires:	apache1-devel
BuildRequires:	autoconf
BuildRequires:	automake
Requires(post,preun):	%{apxs}
Requires:	apache
Requires:	php-cgi
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR)
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)

%description
suPHP is a tool for executing PHP scripts with the permissions of their
owners. It consists of an Apache module (mod_suphp) and a setuid root
binary (suphp) that is called by the Apache module to change the uid of
the process executing the PHP interpreter.

%description -l pl
suPHP jest narzêdziem pozwalaj±cym na wykonywanie skryptów w PHP z
uprawnieniami ich w³a¶cicieli. Sk³ada siê z modu³u (mod_suphp) oraz
programu (suphp) z ustawionym bitem suid, który uruchamiany jest przez
modu³ w celu zmiany uid procesu uruchamiaj±cego interpreter PHP.

%prep
%setup -q -n %{mod_name}-%{version}

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
	--disable-checkuid \
	--disable-checkgid 

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_pkglibdir}}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/conf.d

install src/suphp $RPM_BUILD_ROOT%{_sbindir}
install src/apache/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod-suphp.conf

install -d $RPM_BUILD_ROOT/etc/logrotate.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/apache-mod_suphp

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS ChangeLog doc
%attr(4755,root,root) %{_sbindir}/suphp
%attr(755,root,root) %{_pkglibdir}/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/*
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/conf.d/*
