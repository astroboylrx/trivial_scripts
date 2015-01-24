#!/bin/bash
ls -1 $1/* | sed s/"\/"/"ln -s \/"/ | bash
