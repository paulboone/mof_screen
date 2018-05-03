
# _naive_ procedure to get slope of MSD for diffusivity constant
# should use block averaging or a more sophisticated method.
lmp_avgs_to_tsv.py gasMSD.txt | tsv_plot_cols_vs_time.py -c 3 D --show-fit
