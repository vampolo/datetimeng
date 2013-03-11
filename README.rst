Datetimeng
==========================

The aim of this project is to enhance the datetime module to add nanosecond granularity.

The project is in beta quality.

The goal of this library is to:

- have a datetime like module with nanosecond support
- datetime retrocompatibility
- be fast

The library has basically the same api of the datetime module but class names have been sanitized to camel cased so you have:

- datetimeng.Date
- datetimeng.DateTime
- datetimeng.Time
- datetimeng.TimeDelta
- datetimeng.TzInfo

The basic interface of datetime module has been keep.


The base code comes from `cpython commit 63184:afdb53323065`_ which is a python implementation of the datetime module.

The reasons that lead this work are described in `issue #15443`_

Other useful link is at `issue #5516`_

.. _`cpython commit 63184:afdb53323065`: http://hg.python.org/cpython/annotate/afdb53323065/Lib/datetime.py#1
.. _`issue #15443`: http://bugs.python.org/issue15443
.. _`issue #5516`: http://bugs.python.org/issue5516

Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
