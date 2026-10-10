#!/usr/bin/env python3
"""Plot empirical PDF and CDF for the A2 traffic samples."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def empirical_cdf(values):
    x = np.sort(np.asarray(values, dtype=float))
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y


def make_plot(values, title, xlabel, output_path, bins=30):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    values = values[values > 0]
    x, cdf = empirical_cdf(values)

    fig, (ax_pdf, ax_cdf) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax_pdf.hist(values, bins=bins, density=True, alpha=0.78, color="#2563eb", edgecolor="white")
    ax_pdf.set_title("Empirical PDF")
    ax_pdf.set_xlabel(xlabel)
    ax_pdf.set_ylabel("Density")
    ax_pdf.grid(alpha=0.25)

    ax_cdf.step(x, cdf, where="post", color="#dc2626", linewidth=1.8)
    ax_cdf.set_title("Empirical CDF")
    ax_cdf.set_xlabel(xlabel)
    ax_cdf.set_ylabel("Probability")
    ax_cdf.set_ylim(0, 1.02)
    ax_cdf.grid(alpha=0.25)

    fig.suptitle(f"{title} (n={len(values)})")
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    packet_sizes = []
    inter_arrivals = []
    with args.csv.open(newline="") as f:
        for row in csv.DictReader(f):
            packet_sizes.append(float(row["size_bytes"]))
            inter_arrivals.append(float(row["inter_arrival_s"]))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    make_plot(
        packet_sizes,
        "A2 Packet Size Distribution",
        "Packet size (bytes)",
        args.output_dir / "packet_size_pdf_cdf.pdf",
        bins=[0, 400, 1000, 1350, 1700],
    )
    make_plot(
        inter_arrivals,
        "A2 Inter-arrival Time Distribution",
        "Inter-arrival time (s)",
        args.output_dir / "inter_arrival_pdf_cdf.pdf",
        bins=30,
    )


if __name__ == "__main__":
    main()
