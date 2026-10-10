# A2 — ns-3 Setup Record

## Platform

- OS: Ubuntu 22.04.3 LTS (Jammy)
- Kernel: 6.8.0-136-generic
- Architecture: x86_64
- Compiler: GCC/G++ 11.4.0
- CMake: 3.22.1
- Python: 3.10.12
- RAM: approximately 8 GB

## ns-3 version

- ns-3.46.1
- Source: official `ns-3-dev` Git repository, tag `ns-3.46.1`
- Source directory: `/home/oaicn/henry/ns-3.46.1`

## Build

Configuration:

```text
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

Result: build completed successfully, 1947/1947 build targets.

## Verification

The official tutorial example ran successfully:

```text
./ns3 run first
```

The client and server exchanged a 1024-byte packet. The core smoke test also passed:

```text
./test.py --no-build --suite=core-example-simulator --nocolor
```

Result: 1 passed, 0 failed.

## Simple scenario source and run command

Source code:

- [`a2-traffic-model.cc`](../../../ns-3.46.1/scratch/a2-traffic-model.cc)

The scenario contains two nodes connected by a 100 Mbps point-to-point link
with 10 ms delay. Node 0 generates UDP packets and node 1 receives them with
`PacketSink`. The simulation runs for 10 seconds.

Run command:

```bash
cd /home/oaicn/henry/ns-3.46.1
./ns3 run 'a2-traffic-model --outputDir=/home/oaicn/henry/MWN-2026-M11502205-Henry/A2-ns3-setup/results'
```

## Traffic model

This is an application-level traffic model for the A2 experiment. It uses:

- Packet size: 200 B (10%), 800 B (30%), 1200 B (45%), 1500 B (15%).
- Inter-arrival time: exponential distribution with mean 20 ms and a 200 ms bound.
- Random seed: 7, run: 1.

The model records every generated packet in `packet_samples.csv`, including
packet ID, generation time, packet size, and inter-arrival time. These samples
are used to verify the empirical PDF/CDF plots.

### Relation to 3GPP TR 26.926

The assignment calls it TS 26.926, but the referenced document is a 3GPP
Technical Report (TR 26.926), *Traffic Models and Quality Evaluation Methods
for Media and XR Services in 5G Systems*. The report describes trace-based
models and emphasizes packet-size and packet-latency distributions. Its cloud
gaming example describes bursty traffic, commonly using 1500-byte packets,
an inter-burst period related to the frame rate, and a truncated-Gaussian burst
length. This submission uses a simpler, reproducible application-level model
with explicit packet-size and inter-arrival distributions; it is not claimed
to reproduce a complete XR trace model.

Reference: [ETSI/3GPP TR 26.926 V18.2.0](https://www.etsi.org/deliver/etsi_tr/126900_126999/126926/18.02.00_60/tr_126926v180200p.pdf).

## Result from my run

- Received bytes: 541,200 bytes
- Throughput: 0.437333 Mbps
- PCAP: [`a2-traffic-0-0.pcap`](results/a2-traffic-0-0.pcap)
- Raw samples: [`packet_samples.csv`](results/packet_samples.csv)
- Summary: [`summary.txt`](results/summary.txt)
- Packet-size PDF/CDF: [`packet_size_pdf_cdf.pdf`](results/packet_size_pdf_cdf.pdf)
- Inter-arrival PDF/CDF: [`inter_arrival_pdf_cdf.pdf`](results/inter_arrival_pdf_cdf.pdf)

The plotting command was:

```bash
cd /home/oaicn/henry/MWN-2026-M11502205-Henry/A2-ns3-setup
MPLCONFIGDIR=/tmp/matplotlib-a2 python3 plot_distributions.py \
  results/packet_samples.csv results
```

## Build/runtime issues encountered

1. `EventId::IsRunning()` does not exist in ns-3.46.1; it was changed to
   `EventId::IsPending()`.
2. The first run used an output directory that did not exist, so PCAP creation
   failed. Creating `results/` fixed it.
3. The first socket connection converted an `InetSocketAddress` incorrectly;
   connecting with the complete peer `Address` fixed the assertion.
