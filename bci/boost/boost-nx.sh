#!/bin/sh

if [ -n "$1" ] ; then
    dir=$1
elif [ -n "$LINIX_X86_64" ] ; then
    dir="linux-x86-64"
elif [ -n "$LINIX_X86" ] ; then
    dir="linux-x86"
elif [ -n "$MACOSX_X86_64" ] ; then
    dir="macosx-x86-64"
else 
    echo "No build directory supplied.  Exiting..."
    exit 1
fi

echo "Installing boost into $dir..."

tar xzvf boost_1_54_0.tar.bz2
if [ -z "$?" ] ; then
    echo "Failed to untar boost "
    exit 1
fi

cd boost_1_54_0
./bootstrap.sh --prefix=../$dir -with-libraries=thread,test,python
if [ -z "$?" ] ; then
    echo "Failed to boostrap boost "
    exit 1
fi

./b2 install
if [ -z "$?" ] ; then
    echo "Failed to install boost "
    exit 1
fi
