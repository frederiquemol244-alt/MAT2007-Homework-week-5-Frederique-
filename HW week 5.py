# MAT2007 - Week 5 - Homework exercises
# Frederique Mol I6391802

import os

import numpy as np
import matplotlib.pyplot as plt


#  Helper functions

# Full path of a file in the same folder as this script, so the data file is
# found and the plots are saved there also when the script is started from
# another folder
# Used in: main (data file) and finish_plot() (PNG files)
def path_in_script_folder(filename):
    script_folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_folder, filename)


# Print a title above the output of each exercise
# Used in: Homework 1 and 2
def print_header(title):
    print("\n=====", title, "=====")


# Read the pseudodata written in the week 4 homework (columns: month, cycle,
# sunspots) and return the three columns as arrays
# Used in: main, the data is read once and passed to both homeworks
def read_solar_data(data_file):
    data = np.loadtxt(data_file, skiprows=1)
    return data[:, 0], data[:, 1].astype(int), data[:, 2]


# Sub-sampling technique (week 4, slide 24): split one cycle into interleaved
# subsamples (every n-th month in the same subsample), value = average of the
# subsample means, uncertainty = their standard deviation
# Used in: cycle_averages(), once for every cycle
# This is the same calculation as subsample_mean() in my week 4 homework
# (ddof=1 gives the same standard deviation as sd() in R), so the averages
# and uncertainties here are the same numbers as in week 4
def subsample_mean(cycle_data, n_subsamples):
    subsamples = [cycle_data[i::n_subsamples] for i in range(n_subsamples)]
    means = np.array([s.mean() for s in subsamples])
    return means.mean(), means.std(ddof=1)


# Average number of sunspots and its statistical uncertainty for every cycle
# Helper functions used: subsample_mean()
# Used in: Homework 1 (the results are passed on to Homework 2)
def cycle_averages(cycle, sunspots, n_subsamples):
    cycle_numbers = np.unique(cycle)
    results = np.array([subsample_mean(sunspots[cycle == k], n_subsamples)
                        for k in cycle_numbers])
    return cycle_numbers, results[:, 0], results[:, 1]


# Year of the top of each cycle. The model is A sin(2*pi/P * (t - t0)) + C,
# which has its maximum at t = t0 + P/4 (+ one period for every next cycle)
# Used in: Homework 1, as the x values of the averages (the results are
# passed on to Homework 2)
def cycle_top_years(cycle_numbers, period_months, t0):
    top_months = t0 + period_months / 4 + (cycle_numbers - 1) * period_months
    return top_months / 12


# Axis labels, title, legend and grid, then save the plot as a PNG
# grid_axis="y" draws only the horizontal grid lines (used when the plot
# already has its own vertical lines), dpi=200 makes the PNG sharp enough to
# read the labels after uploading
# Helper functions used: path_in_script_folder()
# Used in: Homework 1 and 2
def finish_plot(xlabel, ylabel, title, filename, legend_loc="best",
                legend_ncol=1, grid_axis="both"):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc=legend_loc, ncol=legend_ncol)
    plt.grid(True, axis=grid_axis)
    path = path_in_script_folder(filename)
    plt.savefig(path, dpi=200)
    print("Saved plot to", path)


# Monthly data as a light scatter in the background, dashed lines on the
# start/end of every cycle and the ticks of the time axis on those lines
# Used in: Homework 1 (plot of the averages)
def draw_monthly_background(years, sunspots, cycle_edges):
    plt.scatter(years, sunspots, s=6, color="orange", alpha=0.4,
                label="Monthly number of sunspots")
    for k, edge in enumerate(cycle_edges):
        plt.axvline(edge, color="gray", linestyle="--", linewidth=0.8,
                    label="Start/end of a cycle" if k == 0 else None)
    plt.xticks(cycle_edges)


# Averages with the systematic uncertainty as grey boxes and the statistical
# uncertainty as error bars (like slide 29)
# The boxes are drawn first so the black points and error bars stay on top
# Used in: Homework 2
def draw_averages_with_syst(top_years, averages, stat_errors, syst_errors,
                            box_width):
    for i in range(len(top_years)):
        plt.fill_between([top_years[i] - box_width / 2,
                          top_years[i] + box_width / 2],
                         averages[i] - syst_errors[i],
                         averages[i] + syst_errors[i],
                         color="gray", alpha=0.5, zorder=2,
                         label="Syst. uncertainty (10%)" if i == 0 else None)
    plt.errorbar(top_years, averages, yerr=stat_errors, fmt="o",
                 color="black", capsize=5, zorder=3,
                 label="Average with stat. errors")


#  Exercise functions

# Homework 1: the solar cycle as a function of time (all months), and the
# average number of sunspots per cycle with its statistical uncertainty as a
# function of the year of the cycle top
# Helper functions used: print_header(), cycle_averages(), cycle_top_years(),
# draw_monthly_background(), finish_plot()
# I made two plots: the first shows only the monthly data, so the sine shape
# of the cycle is easy to see. In the second, all monthly data points are
# drawn as a light scatter in the background, so you can see which data each
# average and uncertainty is calculated from. The dashed lines mark where
# each cycle of 11 years starts and ends
# In both plots the ticks of the time axis are on the start/end of the
# cycles (0, 11, 22, ...), so one step on the axis is exactly one cycle
def homework_1(years, cycle, sunspots, cycle_edges, period_months, t0,
               n_subsamples):
    print_header("Homework 1: Plotting the Solar Cycle")

    plt.figure(figsize=(10, 5))
    plt.plot(years, sunspots, color="orange", linewidth=0.8,
             label="Monthly number of sunspots")
    plt.xticks(cycle_edges)
    finish_plot("Time [years]", "Number of sunspots",
                "Simulated solar cycle", "hw1_solar_cycle.png")

    cycle_numbers, averages, stat_errors = cycle_averages(cycle, sunspots,
                                                          n_subsamples)
    top_years = cycle_top_years(cycle_numbers, period_months, t0)
    for k, year, avg, err in zip(cycle_numbers, top_years, averages,
                                 stat_errors):
        print(f"Cycle {k:2d}: top at year {year:6.2f}, average = "
              f"{avg:7.3f} +/- {err:.3f} (stat.)")

    plt.figure(figsize=(10, 5))
    draw_monthly_background(years, sunspots, cycle_edges)
    plt.errorbar(top_years, averages, yerr=stat_errors, fmt="o",
                 color="black", capsize=5, zorder=3,
                 label="Average with stat. errors")
    plt.ylim(40, 175)          # room above the data for the legend
    finish_plot("Time [years] (averages drawn at the year of the cycle top)",
                "Number of sunspots",
                "Average number of sunspots per cycle",
                "hw1_cycle_averages.png", legend_loc="upper center",
                legend_ncol=3, grid_axis="y")
    return top_years, averages, stat_errors


# Homework 2: the same averages, now with a systematic uncertainty of 10% of
# the average of each cycle drawn as a grey box (like slide 29)
# Helper functions used: print_header(), draw_averages_with_syst(),
# finish_plot()
# The plot is zoomed in on the averages, so the two kinds of uncertainty are
# easy to compare
def homework_2(top_years, averages, stat_errors, syst_fraction, box_width):
    print_header("Homework 2: Plotting with Systematic Uncertainty")
    syst_errors = syst_fraction * averages
    for year, avg, stat, syst in zip(top_years, averages, stat_errors,
                                     syst_errors):
        print(f"Year {year:6.2f}: {avg:7.3f} +/- {stat:.3f} (stat.) "
              f"+/- {syst:.3f} (syst.)")

    plt.figure(figsize=(10, 5))
    draw_averages_with_syst(top_years, averages, stat_errors, syst_errors,
                            box_width)
    plt.ylim(80, 125)          # leave room above the boxes for the legend
    finish_plot("Time of the cycle top [years]", "Average number of sunspots",
                "Average number of sunspots per cycle with stat. and "
                "syst. uncertainties", "hw2_systematic.png")


# Main

# Helper functions used: path_in_script_folder(), read_solar_data()
def main():
    # Same settings as the model used to make the data in week 4
    period_months = 11 * 12    # 11 years in months
    t0 = 0
    n_subsamples = 11          # 132 / 11 = 12 months per subsample
    data_file = path_in_script_folder("solar_cycle.txt")

    month, cycle, sunspots = read_solar_data(data_file)
    years = month / 12
    n_cycles = len(np.unique(cycle))
    cycle_edges = (t0 + np.arange(n_cycles + 1) * period_months) / 12

    # Homework 1
    top_years, averages, stat_errors = homework_1(years, cycle, sunspots,
                                                  cycle_edges, period_months,
                                                  t0, n_subsamples)

    # Homework 2
    homework_2(top_years, averages, stat_errors, syst_fraction=0.10,
               box_width=2)

    plt.show()


main()


# Interpretation
# - Homework 1: 10 cycles of 11 years. All averages are close to 100
#   (99.2 to 101.3) with statistical uncertainties of 2.2 to 4.2, so there
#   is no trend between the cycles.
# - Homework 2: the systematic uncertainty (~10) is three to four times
#   larger than the statistical one (~3), so it dominates.

# The improvements to the plots were made with the help of Claude Code AI
