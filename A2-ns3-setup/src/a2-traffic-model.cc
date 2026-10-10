/*
 * A2 traffic model demonstration.
 *
 * The generator uses a small discrete packet-size distribution and an
 * exponential inter-arrival-time distribution.  Every generated sample is
 * written to CSV so that the empirical PDF/CDF can be plotted later.
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

NS_LOG_COMPONENT_DEFINE("A2TrafficModel");

class A2TrafficGenerator : public Application
{
  public:
    static TypeId GetTypeId();
    void Configure(Address peer, uint16_t port, std::string csvPath, Time stopTime);

  private:
    void StartApplication() override;
    void StopApplication() override;
    void SendPacket();
    uint32_t DrawPacketSize();

    Ptr<Socket> m_socket;
    Address m_peer;
    uint16_t m_port{0};
    std::string m_csvPath;
    Time m_stopTime{Seconds(0)};
    EventId m_sendEvent;
    Ptr<UniformRandomVariable> m_choice;
    Ptr<ExponentialRandomVariable> m_interArrival;
    uint64_t m_packetId{0};
    Time m_lastSend{Seconds(0)};
    std::ofstream m_csv;
};

TypeId
A2TrafficGenerator::GetTypeId()
{
    static TypeId tid = TypeId("ns3::A2TrafficGenerator")
                            .SetParent<Application>()
                            .SetGroupName("Applications")
                            .AddConstructor<A2TrafficGenerator>();
    return tid;
}

void
A2TrafficGenerator::Configure(Address peer, uint16_t port, std::string csvPath, Time stopTime)
{
    m_peer = peer;
    m_port = port;
    m_csvPath = std::move(csvPath);
    m_stopTime = stopTime;
}

void
A2TrafficGenerator::StartApplication()
{
    m_socket = Socket::CreateSocket(GetNode(), UdpSocketFactory::GetTypeId());
    m_socket->Connect(m_peer);

    m_choice = CreateObject<UniformRandomVariable>();
    m_interArrival = CreateObject<ExponentialRandomVariable>();
    m_interArrival->SetAttribute("Mean", DoubleValue(0.020));
    m_interArrival->SetAttribute("Bound", DoubleValue(0.200));

    m_csv.open(m_csvPath);
    m_csv << "packet_id,time_s,size_bytes,inter_arrival_s\n";
    SendPacket();
}

void
A2TrafficGenerator::StopApplication()
{
    if (m_sendEvent.IsPending())
    {
        Simulator::Cancel(m_sendEvent);
    }
    if (m_socket)
    {
        m_socket->Close();
    }
    if (m_csv.is_open())
    {
        m_csv.close();
    }
}

uint32_t
A2TrafficGenerator::DrawPacketSize()
{
    // Empirical application payload distribution used for this experiment:
    // 200 B (10%), 800 B (30%), 1200 B (45%), 1500 B (15%).
    const double u = m_choice->GetValue(0.0, 1.0);
    if (u < 0.10)
    {
        return 200;
    }
    if (u < 0.40)
    {
        return 800;
    }
    if (u < 0.85)
    {
        return 1200;
    }
    return 1500;
}

void
A2TrafficGenerator::SendPacket()
{
    if (Simulator::Now() >= m_stopTime)
    {
        return;
    }

    const uint32_t size = DrawPacketSize();
    m_socket->Send(Create<Packet>(size));

    const Time now = Simulator::Now();
    const double interArrival = (m_packetId == 0) ? 0.0 : (now - m_lastSend).GetSeconds();
    m_csv << m_packetId << "," << std::fixed << std::setprecision(9) << now.GetSeconds() << ","
          << size << "," << interArrival << "\n";
    ++m_packetId;
    m_lastSend = now;

    const Time next = Seconds(m_interArrival->GetValue());
    if (now + next < m_stopTime)
    {
        m_sendEvent = Simulator::Schedule(next, &A2TrafficGenerator::SendPacket, this);
    }
}

int
main(int argc, char* argv[])
{
    std::string outputDir = ".";
    double simulationTime = 10.0;
    uint32_t seed = 7;

    CommandLine cmd(__FILE__);
    cmd.AddValue("outputDir", "Directory for CSV, summary and PCAP outputs", outputDir);
    cmd.AddValue("simulationTime", "Simulation duration in seconds", simulationTime);
    cmd.AddValue("seed", "Random seed", seed);
    cmd.Parse(argc, argv);

    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(1);

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

    const uint16_t port = 5000;
    PacketSinkHelper sinkHelper("ns3::UdpSocketFactory",
                               InetSocketAddress(Ipv4Address::GetAny(), port));
    ApplicationContainer sinkApps = sinkHelper.Install(nodes.Get(1));
    sinkApps.Start(Seconds(0.0));
    sinkApps.Stop(Seconds(simulationTime));

    Ptr<A2TrafficGenerator> generator = CreateObject<A2TrafficGenerator>();
    generator->Configure(InetSocketAddress(interfaces.GetAddress(1), port),
                         port,
                         outputDir + "/packet_samples.csv",
                         Seconds(simulationTime));
    nodes.Get(0)->AddApplication(generator);
    generator->SetStartTime(Seconds(0.1));
    generator->SetStopTime(Seconds(simulationTime));

    p2p.EnablePcap(outputDir + "/a2-traffic", devices.Get(0), true);

    Simulator::Stop(Seconds(simulationTime));
    Simulator::Run();

    Ptr<PacketSink> sink = DynamicCast<PacketSink>(sinkApps.Get(0));
    const uint64_t receivedBytes = sink->GetTotalRx();
    const double activeTime = simulationTime - 0.1;
    const double throughputMbps = (receivedBytes * 8.0) / activeTime / 1e6;

    std::ofstream summary(outputDir + "/summary.txt");
    summary << "ns-3 version: 3.46.1\n";
    summary << "seed: " << seed << "\n";
    summary << "simulation_time_s: " << simulationTime << "\n";
    summary << "received_bytes: " << receivedBytes << "\n";
    summary << "throughput_Mbps: " << throughputMbps << "\n";
    summary.close();

    std::cout << "A2 traffic simulation complete\n"
              << "received_bytes=" << receivedBytes << "\n"
              << "throughput_Mbps=" << throughputMbps << "\n";

    Simulator::Destroy();
    return 0;
}
