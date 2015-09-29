#!/usr/bin/env bash
echo "Installing utilities"
port install emacs-app htop xxdiff ImageMagick wget ffmpeg fftw-2 openssh pandoc pigz bash zsh hdf5 gsed gawk texlive readline xz
echo "Installing gcc+mpi"
port install autoconf automake cmake gcc49 gc5 mpich openmpi gsl boost gdb gdb-apple
echo "Installing python+packages"
port install python27 python34 python35 py27-matplotlib py34-matplotlib py27-numpy py34-numpy py27-scipy py34-scipy py27-astropy py34-astropy py27-ipython py34-ipython py27-mpi4py py34-mpi4py zmq py27-zmq py34-zmq py27-pip py34-pip py27-setuptools py34-setuptools py27-ipdb py34-ipdb py27-terminado py34-terminado py34-jupyter py27-jupyter py27-cython py34-cython py27-notebook py34-notebook py27-tornado py34-tornado
echo "Done."
