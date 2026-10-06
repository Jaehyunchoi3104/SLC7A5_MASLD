# Run from the repository root: Rscript tools/render_rmd.R bulk_nosi
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Usage: Rscript tools/render_rmd.R <analysis_id>")
source("R/paths.R")
analyses <- jsonlite::fromJSON(file.path(slc_repo, "config", "analyses.json"), simplifyVector = FALSE)
analysis <- analyses[[args[[1]]]]
if (is.null(analysis) || !endsWith(analysis$script, ".Rmd")) stop("Choose an R Markdown analysis ID from config/analyses.json.")
invisible(lapply(analysis$inputs, slc_input))
if (!requireNamespace("rmarkdown", quietly = TRUE)) stop("Install rmarkdown before rendering.")
if (!rmarkdown::pandoc_available()) stop("Install Pandoc before rendering HTML reports.")
Sys.setenv(SLC7A5_REPO_ROOT = slc_repo)
report_dir <- slc_output_dir(file.path("reports", args[[1]]))
work_dir <- slc_output_dir(file.path("runs", args[[1]]))
knitr::opts_chunk$set(fig.path = paste0(report_dir, "/figures/"),
                      cache.path = paste0(work_dir, "/cache/"))
rmarkdown::render(
  input = file.path(slc_repo, analysis$script),
  output_dir = report_dir,
  intermediates_dir = work_dir,
  knit_root_dir = work_dir,
  envir = new.env(parent = globalenv()),
  clean = TRUE
)
writeLines(capture.output(sessionInfo()), file.path(report_dir, "sessionInfo.txt"))
