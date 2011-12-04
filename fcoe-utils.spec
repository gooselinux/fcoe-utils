Name:           fcoe-utils
Version:        1.0.14
Release:        9%{?dist}
Summary:        Fibre Channel over Ethernet utilities

Group:          Applications/System
License:        GPLv2
URL:            http://www.open-fcoe.org
# This source was pulled from upstream git repository
# To make a tarball, just run:
# git clone git://open-fcoe.org/openfc/fcoe-utils.git && cd fcoe-utils
# git archive --prefix=fcoe-utils-%{version}/ v%{version} > ../fcoe-utils-%{version}.tar
# cd .. && gzip fcoe-utils-%{version}
Source0:        %{name}-%{version}.tar.gz
Source1:        quickstart.txt
Patch0:         fcoe-utils-1.0.7-init.patch
Patch1:         fcoe-utils-1.0.7-init-condrestart.patch
Patch2:         fcoe-utils-1.0.8-includes.patch
Patch3:         fcoe-utils-1.0.8-init-LSB.patch
Patch4:         fcoe-utils-1.0.12-makefile-data-hook.patch
Patch5:         fcoe-utils-1.0.14-man-pages.patch
# A series of upstream patches marked as critical and ported to RHEL-6
Patch6:         fcoe-utils-1.0.14-displaying-luns.patch
Patch7:         fcoe-utils-1.0.14-skip-lun-inquiry.patch
Patch8:         fcoe-utils-1.0.14-zero-valid-fd.patch
Patch9:         fcoe-utils-1.0.14-close-socket.patch
Patch10:        fcoe-utils-1.0.14-recv-nonblocking.patch
Patch11:        fcoe-utils-1.0.14-disable-on-destroy.patch
Patch12:        fcoe-utils-1.0.14-inverted-argument.patch
Patch13:        fcoe-utils-1.0.14-query-clear.patch
# fipvlan critical patches
Patch14:        fcoe-utils-1.0.14-fipvlan-critical-fix.patch
Patch15:        fcoe-utils-1.0.14-fipvlan-loop.patch
BuildRoot:      1{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExcludeArch:    s390 ppc

BuildRequires:    libhbaapi-devel lldpad-devel libtool automake kernel-devel
Requires:         lldpad libhbalinux >= 1.0.9 vconfig device-mapper-multipath
Requires(post):   chkconfig
Requires(preun):  chkconfig initscripts
Requires(postun): initscripts

%description
Fibre Channel over Ethernet utilities
fcoeadm - command line tool for configuring FCoE interfaces
fcoemon - service to configure DCB Ethernet QOS filters, works with dcbd or
lldpad

%prep
%setup -q
%patch0 -p1 -b .initPatch
%patch1 -p1 -b .condrestartPatch
%patch2 -p1 -b .includes-fix
%patch3 -p1 -b .initLSB
%patch4 -p1 -b .data-hook
%patch5 -p1 -b .man-pages
%patch6 -p1 -b .displaying-luns
%patch7 -p1 -b .lun-inquiry
%patch8 -p1 -b .zero-fd
%patch9 -p1 -b .close-socket
%patch10 -p1 -b .recv-noblock
%patch11 -p1 -b .disable-on-destroy
%patch12 -p1 -b .inverted-arg
%patch13 -p1 -b .query-clear
%patch14 -p1 -b .boot-critical
%patch15 -p1 -b .fipvlan-loop

%build
./bootstrap.sh
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mv $RPM_BUILD_ROOT/etc/init.d/fcoe $RPM_BUILD_ROOT%{_initrddir}/fcoe
rm -rf $RPM_BUILD_ROOT/etc/init.d
install -m 644 %SOURCE1 quickstart.txt
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/fcoe/
cp etc/config $RPM_BUILD_ROOT%{_sysconfdir}/fcoe/config
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/fcoe

install -m 755 contrib/fcc.sh $RPM_BUILD_ROOT%{_libexecdir}/fcoe/fcc.sh
install -m 755 contrib/fcoe_edd.sh $RPM_BUILD_ROOT%{_libexecdir}/fcoe/fcoe_edd.sh
install -m 755 contrib/fcoe-setup.sh $RPM_BUILD_ROOT%{_libexecdir}/fcoe/fcoe-setup.sh
install -m 755 debug/fcoedump.sh $RPM_BUILD_ROOT%{_libexecdir}/fcoe/fcoedump.sh
install -m 755 debug/dcbcheck.sh $RPM_BUILD_ROOT%{_libexecdir}/fcoe/dcbcheck.sh


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add fcoe

%triggerun -- fcoe-utils <= 1.0.7-5
if [ -x %{_initrddir}/fcoe-utils ]; then
  /sbin/service fcoe-utils stop > /dev/null 2>&1
  /sbin/chkconfig fcoe-utils off
  # now copy an updated file, which we need to do proper condrestart
  sed 's/\/var\/lock\/subsys\/fcoe/\/var\/lock\/subsys\/fcoe-utils/' %{_initrddir}/fcoe > %{_initrddir}/fcoe-utils
fi

%triggerpostun -- fcoe-utils <= 1.0.7-5
if [ -x %{_initrddir}/fcoe-utils ]; then
  rm -f %{_initrddir}/fcoe-utils # this file should be already deleted, but just in case ...
fi

%preun
if [ $1 = 0 ]; then
        /sbin/service fcoe stop > /dev/null 2>&1
        /sbin/chkconfig --del fcoe
fi

%postun
if [ "$1" -ge "1" ]; then
        /sbin/service fcoe condrestart > /dev/null  2>&1 || :
fi


%files
%defattr(-,root,root,-)
%doc README COPYING quickstart.txt
%{_sbindir}/*
%{_mandir}/man8/*
%dir %{_sysconfdir}/fcoe/
%config(noreplace) %{_sysconfdir}/fcoe/config
%config(noreplace) %{_sysconfdir}/fcoe/cfg-ethx
%{_initrddir}/fcoe
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoe_edd.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoe-setup.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcc.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoedump.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/dcbcheck.sh


%changelog
* Wed Aug 18 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-9
- fixed fipvlan hangup during boot (#624786)

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-8
- fcoe service starts on all init levels - second try (#619604)

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-7
- critical bugfix on fipvlan (#618443)
- fcoe service starts on all init levels (#619604)

* Tue Jul 20 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-6
- some upstream fixes marked as critical (#615416)

* Tue Jul 13 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-5
- fixed init script - condrestart contained a small bug (#599499)

* Tue Jun 22 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-4
- added device-mapper-multipath to requires (#603242)
- added missing man pages (#594173)

* Thu Jun 03 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-3
- yet another update of init script - added condrestart and try-restart options

* Tue May 25 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-2
- updated init script to support force-reload option
  (alias to "restart force" as packaging guidelines suggest)

* Mon May 24 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-1
- rebased to 1.0.14 (see bug #593824 for a list of changes)

* Thu May 06 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.13-2
- added vconfig to requires (#589608)

* Mon Apr 12 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.13-1
- rebased to v1.0.13, some bugfixes, new FCoE related scripts

* Mon Mar 29 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-3.20100323git
- changed the name of sysfs_edd.sh to fcoe_edd.sh

* Tue Mar 23 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-2.20100323git
- some upstream updates:
- better fipvlan support (#571722)
- added sysfs_edd.sh script (#513018)

* Mon Mar 15 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-1
- rebased to version 1.0.12, improved functionality with lldpad
  and dcbd

* Fri Jan 15 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.10-2
- updated quickstart guide

* Wed Jan 13 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.10-1
- rebased to official 1.0.10 release

* Thu Dec 10 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.9-2.20091204git
- excluded s390 and ppc

* Fri Dec 04 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.9-1.20091204git
- rebase to latest version of fcoe-utils

* Mon Sep 14 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-3
- update of init script to be LSB-compliant

* Fri Jul 31 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-2
- patch for clean compilation without usage of upstream's ugly hack

* Thu Jul 30 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-1
- rebase of fcoe-utils to 1.0.8, adjusted spec file

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 9 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-7
- added quickstart file to doc (#500759)

* Thu May 14 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-6
- renamed init script to fcoe, changed lock filename to fcoe
  (#497604)
- init script modified to do condrestart properly
- some modifications in spec file to apply previous change
  to older versions od init script during update
- fixed issue with accepting long options (#498551)

* Mon May 4 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-5
- fixed SIGSEGV when fcoe module isn't loaded (#498550)

* Wed Apr 27 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-4
- added libhbalinux to Requires (#497605)
- correction of spec file (_initddir -> _initrddir)

* Wed Apr 8 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-3
- more minor corrections in spec file

* Thu Apr 2 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-2
- minor corrections in spec file
- moved init script to correct location
- correction in the init script (chkconfig directives)

* Mon Mar 2 2009 Chris Leech <christopher.leech@intel.com> - 1.0.7-1
- initial rpm build of fcoe tools

