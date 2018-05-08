%define _docroot_dir /usr/local/nginx/html

Summary:  nginx package
Name: nginx
Version: 1.14.0
Release: 1
Vendor: mengyun <mengyun8@163.com>
Source: nginx-%{version}.tar.gz 
#Source5: nginx.logrotate 
#为了防止nginx日志文件逐渐增大，影响读写效率，对nginx日志定期进行切割。

URL: http://nginx.org
License: LGPL
Group: Applications/Internet
#Buildroot:	%{_tmppath}/%{name}-%{version}-root/
Requires: bash openssl-devel curl-develpcre pcre-devel openssl   
#主要定义了nginx依赖的一些rpm包。就是在yum装的时候依赖的包。
Autoreq: no

%description
My nginx RPM BUILD

%prep
#yes|cp nginx-%{version}.tar.gz /root/rpmbuild/SOURCES/
%setup -n nginx-%{version}
%build   #这个阶段就是configure阶段。

./configure \
	--with-http_stub_status_module \
	--with-http_ssl_module 

make %{?_smp_mflags}   #make阶段

%install    #make install阶段

[ $RPM_BUILD_ROOT != "/" ]&& rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install  #下面是来指定我要生成什么样的目录和文件等。
mkdir -p ${RPM_BUILD_ROOT}/modules
mkdir -p ${RPM_BUILD_ROOT}/pid
mkdir -p ${RPM_BUILD_ROOT}/conf/include
mkdir -p ${RPM_BUILD_ROOT}%{__docroot_dir}

mkdir -p ${RPM_BUILD_ROOT}/etc/logrotate.d/
mkdir -p ${RPM_BUILD_ROOT}/etc/init.d/

mkdir -p ${RPM_BUILD_ROOT}/usr/sbin
cp objs/nginx ${RPM_BUILD_ROOT}/usr/sbin/nginx
mkdir -p ${RPM_BUILD_ROOT}/etc/nginx
cp conf/fastcgi.conf ${RPM_BUILD_ROOT}/etc/nginx
cp conf/fastcgi_params ${RPM_BUILD_ROOT}/etc/nginx

cp conf/nginx.conf ${RPM_BUILD_ROOT}/nginx.conf.default
mkdir -p ${RPM_BUILD_ROOT}/var/run/nginx
mkdir -p ${RPM_BUILD_ROOT}/var/og/nginx

%files 
#注意这个阶段是把前面已经编译好的内容要打包了,其中exclude是指要排除什么不打包进来。
/etc/nginx/fastcgi.conf
/etc/nginx/fastcgi_params
/nginx.conf.default
/usr/sbin/nginx

%defattr(-,root,root,755)
%{_prefix}
%{_docroot_dir}
#%attr(0655,root,root)   %config %{_sysconfdir}/init.d/nginx
#%attr(0655,root,root)   %config %{_sysconfdir}/logrotate.d/nginx

%pre 
#pre是指在安装前要做什么操作，也就是先把nginx用户建立好。
if [ "$1" -eq "1" ];then
	/usr/sbin/useradd -c "nginx"  \
	-s /sbin/nologin -r -d %{_docroot_dir} nginx 2> /dev/null || :
fi

%post  
#是指安装完成后的操作包括哪些操作。

if [ "$1" -eq "1"];then
	/sbin/chkconfig --add nginx
	/sbin/chkconfig --level 35 nginx on
	chown -R nginx:nginx %{_docroot_dir} %{_prefix}

	echo '# Add    #下面主要是内核参数的优化，包括tcp的快速释放和重利用等。

	net.ipv4.tcp_max_syn_backlog = 65536
	net.core.netdev_max_backlog =  32768
	net.core.somaxconn = 32768
	net.core.wmem_default = 8388608
	net.core.rmem_default = 8388608
	net.core.rmem_max = 16777216
	net.core.wmem_max = 16777216

	net.ipv4.tcp_timestamps = 0
	net.ipv4.tcp_synack_retries = 2
	net.ipv4.tcp_syn_retries = 2
	net.ipv4.tcp_tw_recycle = 1
	net.ipv4.tcp_tw_reuse = 1
	net.ipv4.tcp_mem = 94500000 915000000927000000
	net.ipv4.tcp_max_orphans = 3276800
	#net.ipv4.tcp_fin_timeout = 30
	#net.ipv4.tcp_keepalive_time = 120
	net.ipv4.ip_local_port_range = 1024  65535' >> /etc/sysctl.conf
	sysctl -p 2>&1 /dev/null
fi

if [ "$1" -eq "2"];then

	if [ -f /var/lock/subsys/nginx ]; then
		%{_sysconfdir}/init.d/nginx restart
	fi
fi

rm -fr %{_prefix}/*temp

%preun  
#这是卸载前的准备工作。

if [ "$1" -eq "0"];then

%{_sysconfdir}/init.d/nginx stop > /dev/null 2>&1

/sbin/chkconfig --del nginx
fi

%postun 
#这是卸载的过程，注意卸载前把需要备份的内容手工备份一遍，防止造成后悔一辈子的事情，有时候运维真的伤不起！！！
/usr/sbin/userdel  nginx
%clean


