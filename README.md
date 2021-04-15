# romdrop-migration
Migrate romdrop from one definition / patched roms to the latest

### Setup

Create directories with your current metadata xmls, stock ROMs, and romdrop-patched stock ROMs.  All ROM files should have a .bin extension.  Modify the romdrop-migrate.ini with directory names, or use the defaults:

```
[directories]
input_definitions_dir = metadata_input
output_definitions_dir = metadata
input_patched_roms_dir = patched_roms_input
output_patched_roms_dir = patched_roms_output
user_roms_dir = user_roms
user_roms_output_dir = user_roms_output
stock_roms_dir = stock_roms
patch_dir = romdrop_patches
```
Next, run the upgrade script (OSX/Linux only, Windows PS / bat file TBD):

```bash upgrade.sh```

This will download the latest romdrop definitions and patches, patch your stock roms, and migrate all binaries in the `user_roms` directory.  Output files are placed in the `user_roms_output` directory.

That's all!  Any time new definitions are released, put your latest roms in the `user_roms` directory and run the upgrade script again.  The latest defs and patches will be downloaded and applied to your current tune.

During migration, output is shown concerning which definition files and patched ROMs are being used for each migration.  If there is a table that goes away or changes addresses such that it can't be located in the output context, an error message will be shown - you will need to manually copy that particular table.
