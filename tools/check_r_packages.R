# Package metadata only; does not install packages or run an analysis.
# Run from the repository root: Rscript tools/check_r_packages.R
repo <- normalizePath(Sys.getenv("SLC7A5_REPO_ROOT", unset = getwd()), mustWork = TRUE)
required <- read.delim(file.path(repo, "environment", "r-packages.tsv"), stringsAsFactors = FALSE)
installed <- installed.packages()
required$observed_version <- unname(installed[match(required$package, installed[, "Package"]), "Version"])
required$R_version <- as.character(getRversion())
write.table(required, stdout(), sep = "\t", row.names = FALSE, quote = FALSE, na = "MISSING")
quit(status = as.integer(anyNA(required$observed_version)))
