from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).parent
R = ROOT / "results"
OUT = ROOT / "A2_ns3_built_in_model.pptx"
NAVY = RGBColor(15, 23, 42); PANEL = RGBColor(30, 41, 59)
WHITE = RGBColor(248, 250, 252); MUTED = RGBColor(148, 163, 184)
CYAN = RGBColor(34, 211, 238); ORANGE = RGBColor(249, 115, 22)

prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

def tx(s, x, y, w, h, text, size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT, mono=False):
    b = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); f = b.text_frame; f.clear(); f.word_wrap = True
    p = f.paragraphs[0]; p.alignment = align; r = p.add_run(); r.text = text
    r.font.name = "DejaVu Sans Mono" if mono else "Aptos"; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return b

def bg(s):
    s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY

def box(s, x, y, w, h):
    q = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    q.fill.solid(); q.fill.fore_color.rgb = PANEL; q.line.color.rgb = RGBColor(51,65,85); return q

def head(s, title, sub=""):
    tx(s, .6, .3, 12, .5, title, 28, WHITE, True)
    q = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.62), Inches(.92), Inches(1.3), Inches(.05)); q.fill.solid(); q.fill.fore_color.rgb = CYAN; q.line.fill.background()
    if sub: tx(s, .62, 1.05, 12, .3, sub, 12, MUTED)

def bullets(s, x, y, w, h, items, size=17):
    b = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); f = b.text_frame; f.clear(); f.word_wrap = True
    for i, item in enumerate(items):
        p = f.paragraphs[0] if i == 0 else f.add_paragraph(); p.text = item; p.bullet = True; p.space_after = Pt(7); p.font.name = "Aptos"; p.font.size = Pt(size); p.font.color.rgb = WHITE

def foot(s, n): tx(s, 11.8, 7.1, .8, .2, f"A2 | {n}", 9, MUTED, align=PP_ALIGN.RIGHT)

# 1
s=prs.slides.add_slide(blank); bg(s); tx(s,.75,1.1,11.8,.7,"A2 — ns-3 Built-in Traffic Model",35,WHITE,True); tx(s,.78,2.0,11,.4,"Using ThreeGppHttpClient / ThreeGppHttpServer",21,CYAN); box(s,.8,3.1,5.4,1.7); tx(s,1.1,3.45,4.8,.35,"Henry | M11502205",19,WHITE,True); tx(s,1.1,3.95,4.8,.55,"ns-3.46.1 • Ubuntu 22.04\n60-second simulation",16,MUTED); tx(s,.8,6.7,11.5,.3,"Goal: run a built-in model and prove it with measured traffic.",14,MUTED); foot(s,1)

# 2
s=prs.slides.add_slide(blank); bg(s); head(s,"Why use the built-in model","The assignment explicitly allows an ns-3 built-in traffic model."); box(s,.8,1.7,5.7,4.8); tx(s,1.1,2.05,5,.35,"ThreeGppHttpClient",21,CYAN,True); bullets(s,1.1,2.7,4.9,2.4,["Requests a main web object","Requests embedded objects","Waits for reading time","Repeats the browsing cycle"]); box(s,6.8,1.7,5.7,4.8); tx(s,7.1,2.05,5,.35,"ThreeGppHttpServer",21,ORANGE,True); bullets(s,7.1,2.7,4.9,2.4,["Accepts the HTTP connection","Generates object sizes with ThreeGppHttpVariables","Segments objects into packets","Returns content to the client"]); foot(s,2)

# 3
s=prs.slides.add_slide(blank); bg(s); head(s,"Simulation topology","A controlled two-node path isolates application traffic."); box(s,.8,1.7,11.8,4.8); tx(s,1.2,2.15,2,.3,"Node 0",21,CYAN,True,PP_ALIGN.CENTER); tx(s,1.2,2.55,2,.3,"HTTP client",16,WHITE,align=PP_ALIGN.CENTER); tx(s,10.1,2.15,2,.3,"Node 1",21,ORANGE,True,PP_ALIGN.CENTER); tx(s,10.1,2.55,2,.3,"HTTP server",16,WHITE,align=PP_ALIGN.CENTER); line=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(3.3),Inches(2.65),Inches(6.4),Inches(.1)); line.fill.solid(); line.fill.fore_color.rgb=WHITE; line.line.fill.background(); tx(s,4.3,2.05,4.5,.3,"Point-to-point channel",18,WHITE,True,PP_ALIGN.CENTER); tx(s,4.1,3.2,5,.3,"100 Mbps | 10 ms delay | IPv4",16,MUTED,align=PP_ALIGN.CENTER); tx(s,1.3,4.7,10.5,.5,"simulation time = 60 s   •   start client at 0.1 s   •   random seed = 7",19,CYAN,True,PP_ALIGN.CENTER); foot(s,3)

# 4
s=prs.slides.add_slide(blank); bg(s); head(s,"What the source code does","The scenario is mostly ns-3 built-in helpers and trace callbacks."); box(s,.8,1.7,12,4.9); tx(s,1.1,2.05,10.8,2.8,"ThreeGppHttpServerHelper serverHelper(serverAddress);\nserverHelper.Install(nodes.Get(1));\n\nThreeGppHttpClientHelper clientHelper(serverAddress);\nclientHelper.Install(nodes.Get(0));\n\nhttpClient->TraceConnectWithoutContext(\"Rx\", MakeCallback(&ClientRx));",16,WHITE,mono=True); tx(s,1.1,5.55,10.8,.45,"The callback records packet size, arrival time, and inter-arrival time into CSV.",17,CYAN,True); foot(s,4)

# 5
s=prs.slides.add_slide(blank); bg(s); head(s,"Built-in variables and outputs","The model generates browsing behavior instead of a hand-written packet loop."); box(s,.8,1.7,5.8,4.8); tx(s,1.1,2.05,5,.35,"ThreeGppHttpVariables",20,CYAN,True); bullets(s,1.1,2.65,4.9,2.3,["Main object size mean = 102,400 B","Main object size std. dev. = 40,960 B","Embedded-object count and reading time are built in","HTTP request/response behavior is built in"],16); box(s,6.9,1.7,5.6,4.8); tx(s,7.2,2.05,4.8,.35,"Evidence files",20,ORANGE,True); bullets(s,7.2,2.65,4.8,2.5,["built_in_packet_samples.csv","built_in_pages.csv","built_in_summary.txt","a2-built-in-http-0-0.pcap"],16); foot(s,5)

# 6
s=prs.slides.add_slide(blank); bg(s); head(s,"Result from the built-in run","The built-in application generated measurable HTTP traffic.");
for x,val,label,col in [(.9,"441,503","received bytes",CYAN),(4.6,"307","received packets",ORANGE),(8.3,"0.0589653","throughput (Mbps)",CYAN)]:
    box(s,x,1.8,3.2,1.75); tx(s,x+.15,2.15,2.9,.5,val,27,col,True,PP_ALIGN.CENTER); tx(s,x+.15,2.85,2.9,.25,label,14,MUTED,align=PP_ALIGN.CENTER)
box(s,.9,4.15,10.9,1.4); tx(s,1.2,4.45,10,.3,"Run command",17,WHITE,True); tx(s,1.2,4.9,10,.3,"./ns3 run 'a2-traffic-model-built-in --outputDir=.../results'",14,CYAN,mono=True); foot(s,6)

# 7
s=prs.slides.add_slide(blank); bg(s); head(s,"Distribution evidence","The plots are empirical distributions measured from built-in model packets."); s.shapes.add_picture(str(R/"built-in-plots"/"packet_size_pdf_cdf.png"), Inches(.7), Inches(1.55), width=Inches(5.95)); s.shapes.add_picture(str(R/"built-in-plots"/"inter_arrival_pdf_cdf.png"), Inches(6.7), Inches(1.55), width=Inches(5.95)); tx(s,.9,6.48,5.5,.3,"Packet sizes come from HTTP object segmentation.",14,CYAN,True,PP_ALIGN.CENTER); tx(s,6.9,6.48,5.5,.3,"Inter-arrival times come from received packets.",14,ORANGE,True,PP_ALIGN.CENTER); foot(s,7)

# 8
s=prs.slides.add_slide(blank); bg(s); head(s,"Submission checklist","What to show during the 10-minute presentation."); box(s,.8,1.7,5.7,4.8); tx(s,1.1,2.05,4.9,.35,"Three required items",21,CYAN,True); bullets(s,1.1,2.7,4.9,2.2,["study_note.md — setup and model","a2-traffic-model-built-in.cc — source and run command","results — numbers, plots, and PCAP"],17); box(s,6.8,1.7,5.7,4.8); tx(s,7.1,2.05,4.9,.35,"One-sentence conclusion",21,ORANGE,True); tx(s,7.1,2.8,4.8,1.7,"The ns-3 built-in ThreeGppHttp model successfully generated web-browsing traffic, and the measured throughput, distributions, and PCAP prove that the simulation ran.",18,WHITE); tx(s,7.1,5.35,4.8,.35,"Next: show the PCAP in Wireshark.",16,CYAN,True); foot(s,8)

prs.save(OUT); print(OUT)
