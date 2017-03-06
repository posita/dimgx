<!--- -*- encoding: utf-8; grammar-ext: md; mode: markdown -*-
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  Please keep each sentence on its own unwrapped line.
  It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
  Thank you! -->

Copyright and other protections apply.
Please see the accompanying [`LICENSE`](../LICENSE) and [`CREDITS`](../CREDITS) file(s) for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If those files are missing or appear to be modified from their originals, then please contact the author before viewing or using this software in any capacity.

- [ ] If necessary, update copyright in [`LICENSE`](../LICENSE) and [`doc/conf.py`](../doc/conf.py)

- [ ] [`./release.sh`](../release.sh)

- [ ] `git push --tags`

- [ ] `python setup.py sdist upload`

- [ ] Upload `dimgx.egg-info/PKG-INFO` to [`https://pypi.python.org/pypi?:action=submit_form&name=dimgx&version=X.Y.Z`](https://pypi.python.org/pypi?:action=submit_form&name=dimgx&version=X.Y.Z), if necessary (work-around)

- [ ] `git checkout master`

- [ ] `git branch --delete X.Y.Z-release`
