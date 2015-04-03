# saltstack-jenkins
A [salt](http://saltstack.com/community/) state module for Jenkins - currently supports downloading artifacts

# Installation
Copy `_states` to `salt/roots`.

# Usage
`jenkins.artifact_present` ensures an artifact from a Jenkins job exists on minion's filesystem. Options include:

* `name` - Exact name of artifact to download.
* `project_url` - URL to Jenkins job. e.g. "http://jenkins.local/job/build_debian_package".
* `job` - Job number to fetch artifacts from; Defaults to special value, `lastSuccessfullBuild`.
* `re_match` - Python regular expression; Matching artifacts will be downloaded; Overrides `name`.
* `cwd` - Path to download artifact to; Defaults to home directory of user running salt.
* `save_as` - Filename to save artifact as; Useful when saving artifacts containing versions that change regularly; Defaults to `name`'s value.

See [_states/jenkins.py](_states/jenkins.py)'s `artifact_present` function for more details.

# Examples
Download .deb package from last successful job and save as "/home/vagrant/custom-package.deb", then install:

```salt
custom-package.deb:
  jenkins.artifact_present:
    - project_url: http://jenkins.local/job/build_debian_package
    - re_match: custom-package.*\.deb

dpkg -i custom-package.deb:
  cmd.run
```

Download .deb package from job #100 and save as "/my_app/custom.deb", then install:

```salt
custom-package.deb:
  jenkins.artifact_present:
    - project_url: http://jenkins.local/job/build_debian_package
	- job: 100
    - re_match: custom-package.*\.deb
	- cwd: /my_app
	- save_as: custom.deb

dpkg -i custom.deb:
  cmd.run
```
