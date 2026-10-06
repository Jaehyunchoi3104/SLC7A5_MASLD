# Export selected donors from an R dgCMatrix without creating a dense matrix.
# Called by HwangBJ_analysis.ipynb; original RDS files are read only.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4L) stop("Usage: counts.rds metadata.rds output_dir donor1,donor2,...")
suppressPackageStartupMessages(library(Matrix))
counts <- readRDS(args[1])
metadata <- readRDS(args[2])
donors <- strsplit(args[4], ",", fixed = TRUE)[[1]]
if (!inherits(counts, "dgCMatrix")) stop("Expected a dgCMatrix")
if (!all(c("Genotype_ID", "Condition") %in% names(metadata))) stop("Missing donor metadata")
if (anyDuplicated(colnames(counts)) || anyDuplicated(rownames(metadata))) stop("Duplicate cell IDs")
if (!setequal(colnames(counts), rownames(metadata))) stop("Counts/metadata barcodes differ")
metadata <- metadata[colnames(counts), , drop = FALSE]
if (!all(donors %in% metadata$Genotype_ID)) stop("Requested donors missing")
keep <- metadata$Genotype_ID %in% donors
counts <- counts[, keep, drop = FALSE]
metadata <- metadata[keep, , drop = FALSE]
if (any(!is.finite(counts@x)) || any(counts@x < 0) || any(counts@x != floor(counts@x))) {
  stop("Counts are not finite non-negative integers")
}
dir.create(args[3], recursive = TRUE, showWarnings = FALSE)
write_binary <- function(values, name, size) {
  con <- file(file.path(args[3], name), "wb")
  on.exit(close(con))
  writeBin(values, con, size = size, endian = "little")
}
write_binary(counts@i, "indices.i32", 4L)
write_binary(counts@p, "indptr.i32", 4L)
write_binary(counts@x, "values.f64", 8L)
writeLines(as.character(dim(counts)), file.path(args[3], "shape.txt"))
writeLines(rownames(counts), file.path(args[3], "genes.txt"))
metadata <- cbind(cell_barcode = rownames(metadata), metadata)
write.csv(metadata, file.path(args[3], "metadata.csv"), row.names = FALSE)
cat("Exported", nrow(counts), "genes and", ncol(counts), "cells/nuclei\n")
print(table(metadata$Genotype_ID))
