<!--- -*- encoding: utf-8; grammar-ext: md; mode: markdown -*-
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  Please keep each sentence on its own unwrapped line.
  It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
  Thank you! -->

- [ ] `git checkout -b X.Y.Z-release`

- [ ] Set version in [`_dimgx/version.py`](_dimgx/version.py)

```diff
diff --git a/_dimgx/version.py b/_dimgx/version.py
index 0123456..fedcba9 100644
--- a/_dimgx/version.py
+++ b/_dimgx/version.py
@@ -25,5 +25,5 @@ from __future__ import (

 __all__ = ()

-__version__ = 'master'
-__release__ = 'master'
+__version__ = 'X.Y.Z'
+__release__ = 'vX.Y.Z'
```

- [ ] Set version in [`README.rst`](README.rst) (`master` → `vX.Y.Z`, except for [`https://pypi.python.org/pypi/dimgx/X.Y.Z`](https://pypi.python.org/pypi/dimgx/X.Y.Z))

- [ ] `git commit -a -m 'Update version and release vX.Y.Z.'`

- [ ] `git tag -s -f -m 'Release vX.Y.Z.' vX.Y.Z`

- [ ] `./setup.py sdist upload`

- [ ] Upload `dimgx.egg-info/PKG-INFO` to [`https://pypi.python.org/pypi?:action=submit_form&name=dimgx&version=X.Y.Z`](https://pypi.python.org/pypi?:action=submit_form&name=dimgx&version=X.Y.Z) (work-around)

- [ ] `git checkout master`

- [ ] `git branch -d X.Y.Z-release`
