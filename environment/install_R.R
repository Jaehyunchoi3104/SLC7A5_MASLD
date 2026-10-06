# Optional installation helper. This is not a version lock and was not run
# during repository preparation. Use a separate R library/environment.
repo <- normalizePath(Sys.getenv("SLC7A5_REPO_ROOT", unset = getwd()), mustWork = TRUE)
required <- read.delim(file.path(repo, "environment", "r-packages.tsv"), stringsAsFactors = FALSE)
options(repos = c(CRAN = "https://cloud.r-project.org"))
missing <- setdiff(required$package, rownames(installed.packages()))
cran <- intersect(missing, required$package[required$source == "CRAN"])
bioc <- intersect(missing, required$package[required$source == "Bioconductor"])
if (length(cran)) install.packages(cran)
if (length(bioc)) {
  if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
  BiocManager::install(bioc, ask = FALSE, update = FALSE)
}
