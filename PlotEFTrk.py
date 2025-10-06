# Authors: Federica Piazza, Calla Hinderks

import ROOT
import math
from pathlib import Path
import click
import yaml

ROOT.gROOT.SetStyle("ATLAS")
ROOT.gROOT.SetBatch()


def isTEfficiency(obj, cfg):
    print(cfg["histo_path"], "is eff", "eff" in cfg["histo_path"]) 
    return "eff" in cfg["histo_path"]
    # return obj.InheritsFrom("TEfficiency")


def getLegend():

    leg = ROOT.TLegend(0.9, 0.7, 0.55, 0.9)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.05)
    leg.SetTextFont(42)
    leg.SetLineWidth(2)

    return leg


def getATLASLabel(args):

    sample = args["sample"]
    mu = args["mu"]
    subatlas = ROOT.TLatex(
        0.2,
        0.84,
        "#splitline{#bf{#it{ATLAS}} Simulation Internal}{#splitline{#sqrt{s} = 14 TeV, HL-LHC}{#splitline{ITk Layout: 03-00-01}{<#mu> = %s, %s}}}"
        % (mu, sample),
    )
    subatlas.SetNDC(1)
    subatlas.SetTextFont(42)
    subatlas.SetTextSize(0.05)
    return subatlas


def getCanvas(cfg):

    canv = ROOT.TCanvas("c", "c", 600, 600)
    canv.cd()
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.35, 1, 1)
    pad1.SetNumber(1)
    pad1.SetBottomMargin(0.05)
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(1.0 / 3.0)
    pad2.SetNumber(2)
    if cfg["log"] == "x":
        pad1.SetLogx()
        pad2.SetLogx()
    if cfg["log"] == "y":
        pad1.SetLogy()
    if cfg["log"] == "xy":
        pad1.SetLogx()
        pad2.SetLogx()
        pad1.SetLogy()
    pad1.Draw()
    pad2.Draw()

    return canv


def setStyle(h, cfg):
    print("set linecolor", cfg["linecolor"])
    h.SetLineColor(cfg["linecolor"])
    h.SetLineStyle(cfg["linestyle"])
    h.SetMarkerStyle(cfg["markstyle"])
    h.SetMarkerColor(cfg["markcolor"])
    h.SetMarkerSize(0.8)
    h.SetLineWidth(2)

    if isTEfficiency(h, cfg):
        ROOT.gPad.Update()
        if "efficiency" in cfg["histo"]:
            h.GetPaintedGraph().SetMaximum(1.2 if cfg["ymax"] == 0 else cfg["ymax"])
            h.GetPaintedGraph().SetMinimum(0.7 if cfg["ymin"] == 0 else cfg["ymin"])
        else:
            if "y" in str(cfg["log"]):
                h.GetPaintedGraph().SetMaximum(
                    10
                    * max(1, abs(math.log10(max(h.GetPaintedGraph().GetY()))))
                    * max(h.GetPaintedGraph().GetY())
                    if cfg["ymax"] == 0
                    else cfg["ymax"]
                )
                h.GetPaintedGraph().SetMinimum(
                    max(1e-10, min(h.GetPaintedGraph().GetY()) * (0.9))
                    if cfg["ymin"] == 0
                    else cfg["ymin"]
                )
            else:
                h.GetPaintedGraph().SetMaximum(
                    1.5 * float(max(h.GetPaintedGraph().GetY()))
                    if cfg["ymax"] == 0
                    else cfg["ymax"]
                )
                h.GetPaintedGraph().SetMinimum(0 if cfg["ymin"] == 0 else cfg["ymin"])
        h.GetPaintedGraph().GetXaxis().SetTitleSize(0)
        h.GetPaintedGraph().GetXaxis().SetLabelSize(0)
        h.GetPaintedGraph().GetYaxis().SetLabelSize(0.05)
        h.GetPaintedGraph().GetXaxis().SetTitleSize(0.05)

    else:
        if cfg["norm"]:
            h.SetMaximum(1.5 if cfg["ymax"] == 0 else cfg["ymax"])
            h.SetMinimum(0 if cfg["ymin"] == 0 else cfg["ymin"])
        else:
            if "y" in str(cfg["log"]):
                h.SetMaximum(
                    1.5
                    * max(1, max(1, abs(math.log10(h.GetMaximum()))))
                    * h.GetMaximum()
                    if cfg["ymax"] == 0
                    else cfg["ymax"]
                )
                h.SetMinimum(
                    max(1e-10, h.GetMinimum() * (0.9))
                    if cfg["ymin"] == 0
                    else cfg["ymin"]
                )
                if "avgNum" in cfg["histo"]:
                    h.SetMinimum(100 if cfg["ymin"] == 0 else cfg["ymin"])
            else:
                h.SetMaximum(1.4 * h.GetMaximum() if cfg["ymax"] == 0 else cfg["ymax"])
                h.SetMinimum(0 if cfg["ymin"] == 0 else cfg["ymin"])
        h.GetXaxis().SetTitleSize(0)
        h.GetXaxis().SetLabelSize(0)
        h.GetYaxis().SetLabelSize(0.05)
        h.GetYaxis().SetTitleSize(0.05)


def setRatioStyle(ratio, cfg, color, linestyle, markstyle, multigraph=False):

    ratio.GetXaxis().SetTitleOffset(1.5)
    ratio.GetYaxis().SetTitle("Ratio wrt reference")
    ratio.GetYaxis().SetTitleSize(0.05 * 65.0 / 35.0)
    ratio.GetYaxis().SetNdivisions(505)
    ratio.GetYaxis().SetTitleOffset(0.7)

    if cfg["ratioyrange"] == None:
        if "Efficiencies" in cfg["category"]:
            ratio.GetYaxis().SetRangeUser(0.7, 1.3)
        elif "Resolution" in cfg["category"]:
            ratio.GetYaxis().SetRangeUser(0.0, 2.0)
        elif "avgNum" in cfg["histo"]:
            ratio.GetYaxis().SetRangeUser(0.7, 1.3)
        else:
            if not multigraph:
                ratio.SetMaximum()
                ratio.SetMinimum()
                ratio.GetYaxis().SetRangeUser(
                    max(
                        0.0,
                        min(ratio.GetMinimum() - 0.1, abs(1.9 - ratio.GetMaximum())),
                    ),
                    max(ratio.GetMaximum() + 0.1, abs(2 - ratio.GetMinimum())),
                )
        # else: ratio.GetYaxis().SetRangeUser(0,10)
    else:
        ratio.GetYaxis().SetRangeUser(cfg["ratioyrange"][0], cfg["ratioyrange"][1])
    ratio.GetXaxis().SetLabelSize(0.05 * 65.0 / 35.0)
    ratio.GetXaxis().SetTitleSize(0.05 * 65.0 / 35.0)
    ratio.GetYaxis().SetLabelSize(0.05 * 65.0 / 35.0)
    ratio.GetYaxis().SetTitleSize(0.05 * 65.0 / 35.0)
    if not multigraph:
        ratio.SetLineColor(color)
        ratio.SetLineStyle(linestyle)
        ratio.SetMarkerStyle(markstyle)
        ratio.SetMarkerColor(color)
        ratio.SetMarkerSize(0.8)


def getTEfficiencyRatio(histos):

    xmin, xmax = (
        histos[0].GetPaintedGraph().GetXaxis().GetXmin(),
        histos[0].GetPaintedGraph().GetXaxis().GetXmax(),
    )
    g1 = ROOT.TGraphAsymmErrors(histos[0].GetPaintedGraph())
    g2 = ROOT.TGraphAsymmErrors(histos[1].GetPaintedGraph())
    title = g1.GetXaxis().GetTitle()

    ratio = ROOT.TGraphAsymmErrors()

    n, n_ref, n_test = max(g1.GetN(), g2.GetN()), g1.GetN(), g2.GetN()

    x_ref_arr, y_ref_arr = g1.GetX(), g1.GetY()
    x_test_arr, y_test_arr = g2.GetX(), g2.GetY()

    i_test, i_ref = 0, 0

    err_r_low = []
    err_r_high = []
    for i in range(n):
        if i_test < n_test and i_ref < n_ref:
            x_ref, y_ref = x_ref_arr[i_ref], y_ref_arr[i_ref]
            x_test, y_test = x_test_arr[i_test], y_test_arr[i_test]
            err_ref_low, err_ref_high = g1.GetErrorYlow(i_ref), g1.GetErrorYhigh(i_ref)
            err_test_low, err_test_high = g2.GetErrorYlow(i_test), g2.GetErrorYhigh(
                i_test
            )

            # Check points matching between test and reference
            if x_test == x_ref:
                y_ref, y_test = y_ref_arr[i_ref], y_test_arr[i_test]
                i_test += 1
                i_ref += 1
            if x_ref > x_test:
                x_ref = x_test
                y_ref, y_test = 0, y_test_arr[i_test]
                i_test += 1
            if x_test > x_ref:
                x_test = x_ref
                y_test, y_ref = 0, y_ref_arr[i_ref]
                i_ref += 1

            r = y_test / y_ref if y_ref != 0 else 1000
            if y_test == 0 and y_ref == 0:
                r = 1
            err_r_low.append(
                r * math.sqrt((err_ref_low / y_ref) ** 2 + (err_test_low / y_test) ** 2)
                if y_ref > 0 and y_test > 0
                else 0
            )
            err_r_high.append(
                r
                * math.sqrt((err_ref_high / y_ref) ** 2 + (err_test_high / y_test) ** 2)
                if y_ref > 0 and y_test > 0
                else 0
            )
            ratio.SetPoint(i, x_ref, r)
            ratio.GetXaxis().SetTitle(title)

    # Set errors and final x axis range
    for i in range(ratio.GetN()):
        width = (
            ratio.GetPointX(i + 1) - ratio.GetPointX(i)
            if i < ratio.GetN() - 1
            else ratio.GetPointX(i) - ratio.GetPointX(i - 1)
        )
        ratio.SetPointError(i, width / 2.0, width / 2.0, err_r_low[i], err_r_high[i])
    ratio.GetXaxis().SetLimits(xmin, xmax)

    return ratio


def draw(args, configs, tails=False):
    canv = getCanvas(configs[0])
    ATLASLabel = getATLASLabel(args)
    legend = getLegend()
    doComparison = len(configs) > 1
    isTEfficiencyObj = False
    histos = []
    canv.cd(1)

    # loop over the trkAnalysis to be compared (if single plot, there will be only 1 trkAnalysis)
    for i, cfg in enumerate(configs):
        h = cfg["histo"]
        isTEfficiencyObj = isTEfficiency(h, cfg)
        histos.append(h)
        h.Draw("same" if i != 0 else "")

        setStyle(h, cfg)

        if doComparison:
            draw_option = "lp"
            legend.AddEntry(h, cfg["legend"], draw_option)
            legend.Draw()

    ATLASLabel.Draw()

    canv.cd(2)

    ratios = []
    multigraph = ROOT.TMultiGraph()

    for i in range(len(configs) - 1):
        ratio_histos = [histos[0], histos[i + 1]]
        if isTEfficiencyObj:
            ratios.append(getTEfficiencyRatio(ratio_histos))
        else:
            ratio = (
                ratio_histos[1].ProjectionX().Clone()
                if "avgNum" in ratio_histos[0].GetName()
                else ratio_histos[1].Clone()
            )
            ratio.Divide(ratio_histos[0])
            ratios.append(ratio)

    for i, ratio in enumerate(ratios):
        color = configs[i + 1]["linecolor"] if len(configs) > 2 else ROOT.kBlack
        linestyle = configs[i + 1]["linestyle"] if len(configs) > 2 else 1
        markstyle = configs[i + 1]["markstyle"] if len(configs) > 2 else 20
        setRatioStyle(ratio, configs[i], color, linestyle, markstyle)
        if isTEfficiencyObj:
            multigraph.Add(ratio, "p")
        else:
            ratio.Draw("same")
    if isTEfficiencyObj:
        xmin, xmax = ratios[0].GetXaxis().GetXmin(), ratios[0].GetXaxis().GetXmax()
        title = multigraph.GetXaxis().SetTitle(ratios[0].GetXaxis().GetTitle())
        setRatioStyle(
            multigraph, configs[i], color, linestyle, markstyle, multigraph=True
        )

        markers = []
        multigraph.Draw("a")
        outliers_index = 0
        for j, g in enumerate(multigraph.GetListOfGraphs()):
            ROOT.gPad.Update()
            ymin = ROOT.gPad.GetFrame().GetY1()
            ymax = ROOT.gPad.GetFrame().GetY2()
            for i in range(g.GetN()):
                if g.GetPointY(i) > ymax:
                    markers.append(
                        ROOT.TMarker(
                            g.GetPointX(i), ymax - (ymax - ymin) * 0.05, 26
                        )
                    )
                    markers[outliers_index].SetMarkerColor(
                        configs[j + 1]["linecolor"]
                    )
                    markers[outliers_index].SetMarkerSize(1.2)
                    markers[outliers_index].Draw("same")
                    outliers_index += 1
                if g.GetPointY(i) < ymin and g.GetPointY(i) > 0:
                    markers.append(
                        ROOT.TMarker(
                            g.GetPointX(i), ymin + (ymax - ymin) * 0.05, 32
                        )
                    )
                    markers[outliers_index].SetMarkerColor(
                        configs[j + 1]["linecolor"]
                    )
                    markers[outliers_index].SetMarkerSize(1.2)
                    markers[outliers_index].Draw("same")
                    outliers_index += 1

        multigraph.GetXaxis().SetLimits(xmin, xmax)
    else:

        markers = []
        outliers_index = 0
        for j, ratio in enumerate(ratios):
            ROOT.gPad.Update()
            ymin = ROOT.gPad.GetFrame().GetY1()
            ymax = ROOT.gPad.GetFrame().GetY2()
            for i in range(ratio.GetNbinsX()):
                if ratio.GetBinContent(i) > ymax:
                    markers.append(
                        ROOT.TMarker(
                            ratio.GetXaxis().GetBinCenter(i),
                            ymax - (ymax - ymin) * 0.05,
                            26,
                        )
                    )
                    markers[outliers_index].SetMarkerColor(
                        configs[j + 1]["linecolor"]
                    )
                    markers[outliers_index].SetMarkerSize(1.2)
                    markers[outliers_index].Draw("same")
                    outliers_index += 1
                if ratio.GetBinContent(i) < ymin and ratio.GetBinContent(i) > 0:
                    markers.append(
                        ROOT.TMarker(
                            ratio.GetXaxis().GetBinCenter(i),
                            ymin + (ymax - ymin) * 0.05,
                            32,
                        )
                    )
                    markers[outliers_index].SetMarkerColor(
                        configs[j + 1]["linecolor"]
                    )
                    markers[outliers_index].SetMarkerSize(1.2)
                    markers[outliers_index].Draw("same")
                    outliers_index += 1

    refline = ROOT.TLine(
        ratios[0].GetXaxis().GetXmin(), 1, ratios[0].GetXaxis().GetXmax(), 1
    )
    refline.SetLineStyle(2)
    refline.SetLineColor(ROOT.kBlack)
    refline.SetLineWidth(1)
    refline.Draw("same")

    filename = args["output"] / (Path(cfg["histo_path"]).name + ".pdf")
    canv.SaveAs(str(filename))


@click.command()
@click.argument("config")
def main(config):
    colors = [
        ROOT.kRed,
        ROOT.kBlue,
        ROOT.kGreen + 2,
        ROOT.kOrange + 7,
        ROOT.kMagenta,
        ROOT.kCyan + 1,
        ROOT.kViolet,
        ROOT.kTeal + 2,
        ROOT.kPink + 6,
        ROOT.kAzure + 1,
    ]
    linestyles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    markstyles = [20, 21, 22, 23, 24, 25, 26, 27, 28, 30]

    # Read fixed config from yaml
    with open(config, "r") as f:
        full_loaded = yaml.safe_load(f)
    
    assert len(full_loaded["files"]) >= 1
    assert len(full_loaded["plots"]) >= 1
    
    args = {}
    common_loaded = full_loaded["common"] if "common" in full_loaded else {}
    args["sample"] = common_loaded.get("sample", "ttbar")
    args["mu"] = common_loaded.get("mu", "200")
    args["output"] = Path(common_loaded.get("output", "."))

    open_files = []
    for fdesc in full_loaded["files"]:
        fname = fdesc["filename"]
        assert Path(fname).exists(), f"{fname} does not exist"
        open_files.append({
            "file": ROOT.TFile.Open(fname, "READ"),
            "filename": fname,
            "legend": fdesc["legend"]
        })
        print(f"Process file {fdesc['filename']}")

    args["output"].mkdir(parents=True, exist_ok=True)

    for loaded in full_loaded["plots"]:
        fixed_config = {}

        fixed_config["histo_path"] = loaded["histo_path"]
        fixed_config["log"] = loaded.get("log", False)
        fixed_config["ymax"] = loaded.get("ymax", 1.0)
        fixed_config["ymin"] = loaded.get("ymin", 0.0)
        fixed_config["ratioyrange"] = loaded.get("ratioyrange", [0.9, 1.1])
        fixed_config["norm"] = loaded.get("norm", False)

        print("Do", fixed_config["histo_path"])
        configs = []

        for i, fdesc in enumerate(open_files):
            h = fdesc["file"].Get(fixed_config["histo_path"])
            if "ntracks_vs_" in fixed_config["histo_path"]:
                hh = h.ProfileX(fdesc["filename"]+"+"+fixed_config["histo_path"])
                hh.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
            else:
                hh = h
            
            configs.append({
                **fixed_config,
                "input": fdesc["filename"],
                "histo": hh,
                "legend": fdesc["legend"],
                "linestyle": linestyles[i],
                "linecolor": colors[i],
                "markstyle": markstyles[i],
                "markcolor": colors[i],
                "tmp": h,
            })


        draw(args, configs)


if __name__ == "__main__":
    main()
