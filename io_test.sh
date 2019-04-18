#!/bin/bash

if [ "$(uname)" == "Darwin" ]; then
    dd_command="gdd"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    dd_command="dd"
fi

echo "Seq Write (5GiB)..."
$dd_command if=/dev/zero of=speetest bs=1G count=5 conv=fdatasync
# five writes will accumulate to 5GiB
echo "Seq Read (5GiB)..."
$dd_command if=speetest of=/dev/null bs=1G
rm ./speetest
echo "4K Random Write (512MiB, ordinarily 1 Queue depth)"
$dd_command if=/dev/urandom of=speetest bs=4k count=131072 conv=fdatasync
echo "4K Random Read (512MiB, ordinarily 1 Queue depth)"
$dd_command if=speetest of=/dev/null bs=4k
rm ./speetest