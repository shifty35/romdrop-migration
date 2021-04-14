# romdrop-migration
Migrate romdrop from one definition / patched roms to the latest

### Setup

Create directories with your current metadata xmls, stock ROMs, and romdrop-patched stock ROMs.  All ROM files should have a .bin extension.  These directories should be called:

metadata_input
patched_roms_input
stock_roms

Next, run the upgrade script (OSX/Linux only, Windows PS / bat file TBD):

```bash upgrade.sh```

This will download the latest romdrop definitions and patches, patch your stock roms, and migrate all binaries in the local directory.  Output files are placed in the `output` directory.

That's all!  Any time new definitions are released, put your latest rom in the root directory and run the upgrade script again.  The latest defs and patches will be downloaded and applied to your current tune.

During migration, output is shown concerning which definition files and patched ROMs are being used for each migration.  If there is a table that goes away or changes addresses such that it can't be located in the output context, an error message will be shown - you will need to manually copy that particular table.
