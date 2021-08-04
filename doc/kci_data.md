---
title: "kci_data"
date: 2021-08-04
draft: false
description: "Command line tool to handle KernelCI data"
---

The [`kci_data`](https://github.com/kernelci/kernelci-core/blob/main/kci_data)
tool is mainly used to submit kernel build meta-data and test results to the
KernelCI backend.  It is still a work in progress, as the majority of native
test results are being sent via the LAVA callback mechanism which bypasses
kci_data with the current implementation.

The
[`db-configs.yaml`](https://github.com/kernelci/kernelci-core/blob/main/config/core/db-configs.yaml)
file contains configuration for all the KernelCI databases that may be used
with `kci_data`.  They all have an API type, currently only `kernelci_backend`
is supported but this may change as new ones get added.  In particular, KCIDB
may be added there as a consolidation with the
[`kcidb`](https://github.com/kernelci/kcidb) command line tools.  The backend
used with native tests is also planned to get redesigned from scratch as the
project keeps evolving, so that would be a new API type too.

## Settings

Typically, database APIs require some authentication token.  The ideal way to
handle this is to use the [settings file](../settings) with an entry for each
`db` config to use.  While the `db-configs.yaml` configuration will include
general configuration information, the settings file is user-specific.  For
example, when using a `kernelci_backend` instance locally, the token can be
stored as such in the settings file:

```ini
[db:localhost]
db_token: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
api: http://192.168.122.1:5001
```

Note: At the moment, the `api` setting (or `--api` command line argument) also
needs to be provided even though it's effectively the same thing as the `url`
parameter in `db-configs.yaml`.  This is a legacy from before `kci_data` was
created, and it will eventually be dropped.  In the meantime, both need to be
provided with the same API URL.

## Submitting build meta-data

One common `kci_data` use-case is to submit the meta-data associated with a
kernel build.  This includes all the JSON files created by `kci_build`.  It
requires either the `kdir` argument for a local build to find the JSON
meta-data in the default `_install_` directory, or `output` if the files were
stored elsewhere.  With the database API token and URL stored in the settings
file as explained in the previous section, here's a typical command line:

```
./kci_data submit_build --db-config=localhost --kdir=linux
```

See also the [example in the `kci_build`
documentation](../kci_build/#5-optional-push-and-publish-the-kernel-build).

## Submitting test results
