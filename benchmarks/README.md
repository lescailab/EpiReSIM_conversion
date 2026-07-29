# Benchmarks

Performance claims are intentionally deferred. A benchmark release must record:

- source commit and package/dependency versions;
- exact command and seed;
- sample count, SNP count, interaction order, prevalence, and heritability;
- CPU model, architecture, operating system, and available memory;
- wall-clock time and peak resident memory; and
- whether compatibility or strict mode was used.

The initial benchmark matrix should cover 1,000, 2,000, and 4,000 output
samples; 1,000 SNPs; orders 2–5; prevalence-only and heritability-constrained
models; x86-64 and ARM64. Reference inputs must be redistributable and
anonymized.
