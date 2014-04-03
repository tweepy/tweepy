---
layout: post
title: Harvesting tweets with the python-twitter program
---





To install the python-twitter plugin ( http://code.google.com/p/python-twitter/ )
on an Ubuntu system with root access requires only two lines of code:

```{bash}
sudo apt-get install python-setuptools
sudo easy_install python-twitter
```

A number of additional libraries were needed, which are automatically installed by easy_install.
If you lack root access, these can be installed in a local directory with the following command `python setup.py install --home=/scratch/python`.
Then, to add this directory to Python's search path, the following should typed from the python command line: `sys.path.append('/scratch/python/')`


