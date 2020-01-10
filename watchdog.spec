Summary:          Software and/or Hardware watchdog daemon
Name:             watchdog
Version:          5.6
Release:          5%{?dist}
License:          GPL+
Group:            System Environment/Daemons

URL:              http://sourceforge.net/projects/watchdog/
Source0:          http://downloads.sourceforge.net/watchdog/watchdog-%{version}.tar.gz
Source1:          watchdog.init
Source2:          README.watchdog.ipmi
Source3:          README.Fedora

Patch1:           bz657750-1-add-watchdog-d.patch
Patch2:           bz657750-2-script-handling.patch
Patch3:           bz657750-3-add_test_directory_to_configuration_file.patch
Patch4:           bz657750-4-Log-binary-names.patch
Patch5:           bz657750-5-man_page_information_for_test_directory.patch
Patch6:           bz1099604-default_timeout.patch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:    automake
BuildRequires:    autoconf >= 2.63

Requires(post):   /sbin/chkconfig
Requires(postun): /sbin/chkconfig
Requires(post):   /sbin/service
Requires(postun): /sbin/service


%description
The watchdog program can be used as a powerful software watchdog daemon 
or may be alternately used with a hardware watchdog device such as the 
IPMI hardware watchdog driver interface to a resident Baseboard 
Management Controller (BMC).  watchdog periodically writes to /dev/watchdog; 
the interval between writes to /dev/watchdog is configurable through settings 
in the watchdog sysconfig file.  This configuration file is also used to 
set the watchdog to be used as a hardware watchdog instead of its default 
software watchdog operation.  In either case, if the device is open but not 
written to within the configured time period, the watchdog timer expiration 
will trigger a machine reboot. When operating as a software watchdog, the 
ability to reboot will depend on the state of the machine and interrupts.  
When operating as a hardware watchdog, the machine will experience a hard 
reset (or whatever action was configured to be taken upon watchdog timer 
expiration) initiated by the BMC.

 
%prep
%setup -q -n %{name}-%{version}

cp %{SOURCE2} .
cp %{SOURCE3} .
%if 0%{?rhel}
mv README.Fedora README.RHEL
%endif

%patch1 -p1 -b .bz657750-1-add-watchdog-d
%patch2 -p1 -b .bz657750-2-script-handling
%patch3 -p1 -b .bz657750-3-add_test_directory_to_configuration_file
%patch4 -p1 -b .bz657750-4-Log-binary-names
%patch5 -p1 -b .bz657750-5-man_page_information_for_test_directory
%patch6 -p1 -b -bz1099604-default_timeout

mv README README.orig
iconv -f ISO-8859-1 -t UTF-8 < README.orig > README


%build
# Because we touch configure.in, the shipped configure script
# no longer works and we have to regenerate it.
autoreconf
%configure 
make %{?_smp_mflags}


%install
rm -Rf ${RPM_BUILD_ROOT}
install -d -m0755 ${RPM_BUILD_ROOT}%{_sysconfdir}
install -d -m0755 ${RPM_BUILD_ROOT}%{_sysconfdir}/watchdog.d
make DESTDIR=${RPM_BUILD_ROOT} install
install -Dp -m0644 %{name}.sysconfig ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/watchdog
install -Dp -m0755 %{SOURCE1} ${RPM_BUILD_ROOT}%{_initrddir}/watchdog

%clean
rm -Rf ${RPM_BUILD_ROOT}


%post
if [ $1 -eq 1 ]; then
  /sbin/chkconfig --add %{name}
fi


%preun 
if [ $1 -eq 0 ]; then
  /sbin/service %{name} stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}
fi


%postun 
if [ $1 -ge 1 ]; then
  /sbin/service %{name} condrestart >/dev/null  2>&1
fi


%files
%defattr(-, root, root, -)
%doc AUTHORS ChangeLog COPYING examples/ IAFA-PACKAGE NEWS README TODO README.watchdog.ipmi
%if 0%{?rhel}
%doc README.RHEL
%else
%doc README.Fedora
%endif
%config(noreplace) %{_sysconfdir}/watchdog.conf
%config(noreplace) %{_sysconfdir}/sysconfig/watchdog
%{_sysconfdir}/rc.d/init.d/watchdog
%{_sysconfdir}/watchdog.d
%{_sbindir}/watchdog
%{_sbindir}/wd_keepalive
%{_mandir}/man5/watchdog.conf.5*
%{_mandir}/man8/watchdog.8*
%{_mandir}/man8/wd_keepalive.8*


%changelog
* Thu Oct 22 2015 Tomas Smetana <tsmetana@redhat.com> - 5.6-5
- Fix initscript: suppress unnecessary [OK]
- Resolves: rhbz#1263040

* Mon Oct 13 2014 Ales Ledvinka <aledvink@redhat.com> - 5.6-4
- With no value provided for watchdog-timeout do not attempt
  to set it. Avoid conflict with custom module parameter.
- Resolves: rhbz#1099604

* Thu Aug  8 2013 Richard W.M. Jones <rjones@redhat.com> - 5.6-2
- Rename README.Fedora to README.RHEL on RHEL.

* Tue Aug  6 2013 Richard W.M. Jones <rjones@redhat.com> - 5.6-1
- Rebase to 5.6 (the same version as RHEL 5)
  Resolves: rhbz#870217

* Thu Feb  3 2011 Richard W.M. Jones <rjones@redhat.com> - 5.5-10
- Import watchdog initscript from Rawhide, includes some LSB-compliance
  fixes.
  Resolves: rhbz#584701

* Tue Jan 25 2011 Lon Hohberger <lhh@redhat.com> - 5.5-9
- Add man page information on test-directory
  (bz657750-5-man_page_information_for_test_directory.patch)
  Resolves: rhbz#657750

* Mon Jan 24 2011 Lon Hohberger <lhh@redhat.com> - 5.5-8
- Add watchdog.d handling
  (bz657750-1-add-watchdog-d.patch)
  This makes the scripts in /etc/watchdog.d behave slightly differently
  (bz657750-2-script-handling.patch)
  Add test-directory to configuration file
  (bz657750-3-add_test_directory_to_configuration_file.patch)
  Log which binaries fail
  (bz657750-4-Log-binary-names.patch)
  Resolves: rhbz#657750

* Fri Jan 29 2010 Richard W.M. Jones <rjones@redhat.com> - 5.5-7.1
- Import Fedora Rawhide package (includes fixed Source0 URL).

* Wed Jan 13 2010 Richard W.M. Jones <rjones@redhat.com> - 5.5-7
- Fix Source0 URL.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 13 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-5
- Updated the cleanup patch and sent upstream.

* Fri Mar 13 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-3
- Remove dubious "cleanup-nfs" patch.

* Thu Mar  5 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-2
- Use '-' in defattr line instead of explicit file mode.

* Thu Feb 26 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-1
- New upstream version 5.5.
- Prepared the package for Fedora review.

* Mon Jun 11  2007 Lon Hohberger <lhh@redhat.com> - 5.3.1-7
- Rebuild for RHEL5 Update 1 - Resolves: 227401

* Wed May 30  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-6
- Fixed the init script file.

* Tue May 29  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-5
- Fixed a compile warning in nfsmount_xdr file.

* Wed May 23  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-4
- Fixed rpmlint warnings.

* Wed May 16  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-3
- Changes to spec, init script and README file per Carol Hebert recommendation.

* Thu Apr 19  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-2
- Added README.watchdog.ipmi

* Mon Apr 16  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-1
- Initial copy. 
