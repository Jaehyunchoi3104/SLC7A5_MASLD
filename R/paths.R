# Portable paths for manuscript R Markdown analyses. Requires jsonlite.
slc_find_repo <- function(start = getwd()) {
  explicit <- Sys.getenv("SLC7A5_REPO_ROOT", unset = "")
  p <- normalizePath(if (nzchar(explicit)) explicit else start, mustWork = TRUE)
  repeat {
    if (file.exists(file.path(p, "config", "paths.json")) &&
        file.exists(file.path(p, "R", "paths.R"))) return(p)
    parent <- dirname(p)
    if (identical(parent, p)) stop("Start inside the git repository or set SLC7A5_REPO_ROOT.")
    p <- parent
  }
}

slc_repo <- slc_find_repo()
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Install jsonlite before running this analysis.")
slc_config <- jsonlite::fromJSON(file.path(slc_repo, "config", "paths.json"), simplifyVector = FALSE)
local_config <- file.path(slc_repo, "config", "paths.local.json")
if (file.exists(local_config)) {
  local_values <- jsonlite::fromJSON(local_config, simplifyVector = FALSE)
  for (key in names(local_values)) slc_config[[key]] <- local_values[[key]]
}
slc_catalog <- jsonlite::fromJSON(file.path(slc_repo, "config", "inputs.json"), simplifyVector = FALSE)
unknown_inputs <- setdiff(names(slc_config$input_overrides), names(slc_catalog))
if (length(unknown_inputs)) stop("Unknown input overrides: ", paste(unknown_inputs, collapse = ", "))

slc_absolute <- function(path) {
  path <- path.expand(path)
  if (!grepl("^(/|[A-Za-z]:[/\\\\])", path)) path <- file.path(slc_repo, path)
  normalizePath(path, winslash = "/", mustWork = FALSE)
}
slc_data_root <- slc_absolute(Sys.getenv("SLC7A5_DATA_ROOT", unset = slc_config$data_root))
slc_results_root <- file.path(slc_repo, "results")
if (dir.exists(slc_results_root) &&
    !identical(normalizePath(slc_results_root, winslash = "/", mustWork = TRUE), slc_results_root)) {
  stop("results/ must be a real repository directory, not a symlink to another location.")
}

slc_relative <- function(path) {
  if (length(path) != 1L || !nzchar(path) || grepl("^(/|[A-Za-z]:)", path) ||
      any(strsplit(gsub("\\\\", "/", path), "/", fixed = TRUE)[[1]] == "..")) {
    stop("Expected a non-empty project-relative path: ", path)
  }
  path
}

slc_output <- function(relative, directory = FALSE, create = TRUE) {
  relative <- slc_relative(relative)
  path <- file.path(slc_results_root, relative)
  parent <- if (directory) path else dirname(path)
  # Check existing ancestors before creating directories, including symlinks.
  existing <- parent
  while (!dir.exists(existing) && !file.exists(existing)) existing <- dirname(existing)
  actual <- normalizePath(existing, winslash = "/", mustWork = TRUE)
  expected <- normalizePath(slc_repo, winslash = "/", mustWork = TRUE)
  if (!(identical(actual, expected) || identical(actual, paste0(expected, "/results")) ||
        startsWith(actual, paste0(expected, "/results/")))) {
    stop("Output path escapes repository results/ (check symlinks): ", path)
  }
  if (file.exists(path)) {
    actual_target <- normalizePath(path, winslash = "/", mustWork = TRUE)
    if (!startsWith(actual_target, paste0(expected, "/results/"))) stop("Output target escapes results/.")
  }
  if (create) dir.create(parent, recursive = TRUE, showWarnings = FALSE)
  path
}
slc_output_dir <- function(relative) slc_output(relative, directory = TRUE)

slc_input_path <- function(relative, required = TRUE) {
  relative <- slc_relative(relative)
  ids <- names(Filter(function(x) identical(x$path, relative), slc_catalog))
  override <- if (length(ids)) slc_config$input_overrides[[ids[[1]]]] else NULL
  path <- if (!is.null(override)) slc_absolute(override) else file.path(slc_data_root, relative)
  if (required && !file.exists(path)) stop("Missing input: ", path, "\nSee config/paths.local.json and docs/data_requirements.md.")
  path
}

slc_artifact <- function(relative, required = TRUE) {
  result <- slc_output(relative, create = FALSE)
  if (file.exists(result)) result else slc_input_path(relative, required)
}

slc_input <- function(id, required = TRUE) {
  entry <- slc_catalog[[id]]
  if (is.null(entry)) stop("Unknown input ID: ", id)
  if (!is.null(slc_config$input_overrides[[id]])) return(slc_input_path(entry$path, required))
  if (isTRUE(entry$generated)) slc_artifact(entry$path, required) else slc_input_path(entry$path, required)
}

slc_setup <- function(analysis_id) {
  workdir <- slc_output_dir(file.path("runs", analysis_id))
  set.seed(slc_config$seed)
  if (requireNamespace("knitr", quietly = TRUE)) knitr::opts_knit$set(root.dir = workdir)
  setwd(workdir)
  invisible(workdir)
}

slc_sample_info <- function(sample_names) {
  info <- read.delim(file.path(slc_repo, "config", "bulk_samples.tsv"), stringsAsFactors = FALSE,
                     check.names = FALSE)
  if (anyDuplicated(info$sample) || anyDuplicated(sample_names)) stop("Duplicate sample IDs.")
  missing <- setdiff(sample_names, info$sample)
  if (length(missing)) stop("Samples missing from config/bulk_samples.tsv: ", paste(missing, collapse = ", "))
  info <- info[match(sample_names, info$sample), , drop = FALSE]
  info$group <- factor(info$group, levels = c("siCon", "siCon_LPS", "siSLC_LPS5"))
  if (anyNA(info$group)) stop("Unknown bulk experimental group.")
  rownames(info) <- info$sample
  info
}
