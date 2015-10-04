#!/usr/bin/env bash
py2="py27"
py3="py34"
echo "Installing utilities"
port install openssh emacs-app htop ffmpeg fftw-3 pigz bash zsh gsed texlive readline
echo "Installing gcc+mpi"
port install autoconf automake cmake gcc49 mpich openmpi gsl boost gdb gdb-apple
echo "Installing python+packages"
port install python27 python34 $py2-matplotlib $py3-matplotlib $py2-numpy $py3-numpy $py2-scipy $py3-scipy $py2-astropy $py3-astropy $py2-ipython $py3-ipython $py2-mpi4py $py3-mpi4py zmq $py2-zmq $py3-zmq $py2-pip $py3-pip $py2-setuptools $py3-setuptools $py2-ipdb $py3-ipdb $py2-terminado $py3-terminado $py3-jupyter $py2-jupyter $py2-cython $py3-cython $py2-notebook $py3-notebook $py2-tornado $py3-tornado $py2-readline $py3-readline $py2-requests $py3-requests $py2-jinja2 $py3-jinja2
echo "Selecting default ports"
port select --set gcc mp-gcc49
port select --set mpi mpich-mp-fortran
port select --set python python34
port select --set ipython py34-ipython
port select --set python2 python27
port select --set ipython2 py27-ipython
port select --set python3 python34
port select --set ipython3 py34-ipython
port select --set pip pip34
port select --set cython cython34
port select --set ipdb ipdb34
port select --set nosetests nosetests34
echo "Done."
echo "Remember to install Mathjax and using pip to install testpath"
