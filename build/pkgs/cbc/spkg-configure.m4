SAGE_SPKG_CONFIGURE([cbc], [
    dnl  checking with pkg-config
    PKG_CHECK_MODULES([CBC], [cbc >= 2.9.4], [], [sage_spkg_install_cbc=yes])
])
