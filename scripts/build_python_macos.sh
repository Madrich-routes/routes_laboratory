CONFIGURE_OPTS=""
CONFIGURE_OPTS="$CONFIGURE_OPTS --enable-optimizations"
CONFIGURE_OPTS="$CONFIGURE_OPTS --with-lto"
CONFIGURE_OPTS="$CONFIGURE_OPTS --with-computed-gotos"
CONFIGURE_OPTS="$CONFIGURE_OPTS --enable-loadable-sqlite-extensions"
CONFIGURE_OPTS="$CONFIGURE_OPTS --without-ensurepip"
CONFIGURE_OPTS="$CONFIGURE_OPTS --enable-shared"
CONFIGURE_OPTS="$CONFIGURE_OPTS --enable-ipv6"
CONFIGURE_OPTS="$CONFIGURE_OPTS --with-openssl=/usr/local/opt/openssl@1.1"
CONFIGURE_OPTS="$CONFIGURE_OPTS ax_cv_c_float_words_bigendian=no"
#CONFIGURE_OPTS="$CONFIGURE_OPTS --with-hash-algorithm=fnv"  # довольно тупая идея
export CONFIGURE_OPTS

#--with-dtrace

CFLAGS=""
CFLAGS="$CFLAGS -pipe -Wno-unused-value -Wno-empty-body -Qunused-arguments -Wno-parentheses-equality"
CFLAGS="$CFLAGS -mtune=native"
CFLAGS="$CFLAGS -march=native"
CFLAGS="$CFLAGS -DNDEBUG"

#CFLAGS="$CFLAGS -flto"
#CFLAGS="$CFLAGS -ffat-lto-objects"
#CFLAGS="$CFLAGS -fuse-linker-plugin"
#CFLAGS="$CFLAGS -fprefetch-loop-arrays"
#CFLAGS="$CFLAGS -ffast-math"

#CFLAGS="$CFLAGS -ftree-vectorize"
#CFLAGS="$CFLAGS -feliminate-unused-debug-types"
#CFLAGS="$CFLAGS -fno-trapping-math"
#CFLAGS="$CFLAGS -fno-strict-aliasing"
#CFLAGS="$CFLAGS -fvectorize"

# polyhedral and shit
#CFLAGS="$CFLAGS -O2 -mllvm -polly -mllvm -polly-vectorizer=stripmine"
#CFLAGS="$CFLAGS -mllvm -polly-optimizer=isl"
export CFLAGS

export LDFLAGS="-L/usr/local/opt/sqlite/lib"
export CPPFLAGS="-I/usr/local/opt/sqlite/include"
export PKG_CONFIG_PATH="/usr/local/opt/sqlite/lib/pkgconfig"

#CFLAGS="$CFLAGS -floop-interchange"
#-floop-nest-optimize
#-fgraphite-identity
#-ftree-loop-distribute-patterns
#-fno-semantic-interposition
#-fweb
#-fcx-fortran-rules
#-fno-stack-protector
#-no-pie

export MAKE_OPTS="-j12"

#export CC='clang-11'
#export CXX='clang++-11'
#export AR="llvm-ar"

#export CC='/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'
#export CXX='/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'

#export CC='gcc'
#export CXX='g++'

#export CC='gcc-10'
#export CXX='g++-10'

pyenv install -v 3.9.0
