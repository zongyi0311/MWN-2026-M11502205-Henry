/*
 * A2 scenario using ns-3's built-in ThreeGppHttpClient/Server model.
 * The model simulates web browsing: clients request pages, and servers
 * return main and embedded objects with built-in 3GPP-style variables.
 */

#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"

#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>

using namespace ns3;

namespace
{
std::ofstream g_packetCsv;
std::ofstream g_pageCsv;
uint64_t g_receivedBytes = 0;
uint64_t g_packetId = 0;
Time g_lastPacketTime = Seconds(0);

void
ClientRx(Ptr<const Packet> packet, const Address&)
{
    const Time now = Simulator::Now();
    const double iat = (g_packetId == 0) ? 0.0 : (now - g_lastPacketTime).GetSeconds();
    g_packetCsv << g_packetId << "," << std::fixed << std::setprecision(9)
                << now.GetSeconds() << "," << packet->GetSize() << "," << iat << "\n";
    ++g_packetId;
    g_lastPacketTime = now;
    g_receivedBytes += packet->GetSize();
}

void
ClientPageReceived(Ptr<const ThreeGppHttpClient>,
                   const Time& loadTime,
                   uint32_t objects,
                   uint32_t bytes)
{
    g_pageCsv << std::fixed << std::setprecision(9) << Simulator::Now().GetSeconds() << ","
              << loadTime.GetSeconds() << "," << objects << "," << bytes << "\n";
}
} // namespace

int
main(int argc, char* argv[])
{
    double simulationTime = 60.0;
    std::string outputDir = ".";
    uint32_t seed = 7;

    CommandLine cmd(__FILE__);
    cmd.AddValue("simulationTime", "Simulation duration in seconds", simulationTime);
    cmd.AddValue("outputDir", "Directory for CSV, summary and PCAP outputs", outputDir);
    cmd.AddValue("seed", "Random seed", seed);
    cmd.Parse(argc, argv);

    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(1);

    g_packetCsv.open(outputDir + "/built_in_packet_samples.csv");
    g_packetCsv << "packet_id,time_s,size_bytes,inter_arrival_s\n";
    g_pageCsv.open(outputDir + "/built_in_pages.csv");
    g_pageCsv << "time_s,page_load_time_s,objects,bytes\n";

    NodeContainer nodes;
    nodes.Create(2);

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("100Mbps"));
    p2p.SetChannelAttribute("Delay", StringValue("10ms"));
    NetDeviceContainer devices = p2p.Install(nodes);

    InternetStackHelper internet;
    internet.Install(nodes);

    Ipv4AddressHelper addresses;
    addresses.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = addresses.Assign(devices);
    Ipv4Address serverAddress = interfaces.GetAddress(1);

    ThreeGppHttpServerHelper serverHelper(serverAddress);
    ApplicationContainer serverApps = serverHelper.Install(nodes.Get(1));
    Ptr<ThreeGppHttpServer> httpServer = serverApps.Get(0)->GetObject<ThreeGppHttpServer>();

    PointerValue variablePointer;
    httpServer->GetAttribute("Variables", variablePointer);
    Ptr<ThreeGppHttpVariables> variables = variablePointer.Get<ThreeGppHttpVariables>();
    variables->SetMainObjectSizeMean(102400);
    variables->SetMainObjectSizeStdDev(40960);

    ThreeGppHttpClientHelper clientHelper(serverAddress);
    ApplicationContainer clientApps = clientHelper.Install(nodes.Get(0));
    Ptr<ThreeGppHttpClient> httpClient = clientApps.Get(0)->GetObject<ThreeGppHttpClient>();
    httpClient->TraceConnectWithoutContext("Rx", MakeCallback(&ClientRx));
    httpClient->TraceConnectWithoutContext("RxPage", MakeCallback(&ClientPageReceived));

    serverApps.Start(Seconds(0.0));
    clientApps.Start(Seconds(0.1));
    serverApps.Stop(Seconds(simulationTime));
    clientApps.Stop(Seconds(simulationTime));

    p2p.EnablePcap(outputDir + "/a2-built-in-http", devices.Get(0), true);

    Simulator::Stop(Seconds(simulationTime));
    Simulator::Run();

    const double activeTime = simulationTime - 0.1;
    const double throughputMbps = (g_receivedBytes * 8.0) / activeTime / 1e6;
    std::ofstream summary(outputDir + "/built_in_summary.txt");
    summary << "model: ns-3 built-in ThreeGppHttpClient/ThreeGppHttpServer\n";
    summary << "ns-3 version: 3.46.1\n";
    summary << "seed: " << seed << "\n";
    summary << "simulation_time_s: " << simulationTime << "\n";
    summary << "received_bytes: " << g_receivedBytes << "\n";
    summary << "received_packets: " << g_packetId << "\n";
    summary << "throughput_Mbps: " << throughputMbps << "\n";
    summary.close();

    g_packetCsv.close();
    g_pageCsv.close();
    std::cout << "Built-in ThreeGppHttp simulation complete\n"
              << "received_bytes=" << g_receivedBytes << "\n"
              << "received_packets=" << g_packetId << "\n"
              << "throughput_Mbps=" << throughputMbps << "\n";

    Simulator::Destroy();
    return 0;
}
