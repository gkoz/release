Checking out the crates configured in `crates.txt` into the `build` directory:

```bash
> ./crates.py checkout crates.txt build
```

Updating the config to current `master` (`pending` for `examples`) heads:

```bash
> ./crates.py update crates.txt build
```

Replace urls by `crates.io` version:

```bash
./cargo-crates-io-deps-only.py
```
