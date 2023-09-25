# CEST-tools
## Purpose
These are my personal tools for loading CEST data from 2dseq files (Bruker) and performing corrections and analysis on this data. It is still a WIP, but most features are working in some capacity. All image parameters are loaded from the method file and Lorentzian fitting is done with a two-step method.

For now, fitting only works on *in vivo* cardiac data. 

You can use **check_zspecs.py** to draw ROIs and check the average z-spectrum in that region.

## Instructions
### main.py
Run this file from the terminal using the command:
```
python3 main.py
```
This will walk you through the necessary selections and output fits to folders within the app directory (under /data/).

### resources
All of the required analysis files exist in this directory. They can be changed or modified for personal applications.

**Note:** This works well for my data and applications, but there is no guarantee it will work for other acquisition or data types. I have done my best to account for other use cases, but it is not comprehensive.

## Requirements
Required packages listed under requirements.txt file.

Install using pip by navigating to the directory and using the command:
```
pip install -r requirements.txt
```

## Citations
2dseq loading and image reorganizing for CEST_RARE sequence (Martinos) adapted from code by [Or Perlman](https://github.com/operlman).

Kim M, Gillen J, Landman BA, Zhou J, van Zijl PC. Water saturation shift referencing (WASSR) for chemical exchange saturation transfer (CEST) experiments. Magn Reson Med. 2009 Jun;61(6):1441-50. doi: 10.1002/mrm.21873. PMID: 19358232; PMCID: PMC2860191.

Zaiss M, Schmitt B, Bachert P. Quantitative separation of CEST effect from magnetization transfer and spillover effects by Lorentzian-line-fit analysis of z-spectra. J Magn Reson. 2011 Aug;211(2):149-55. doi: 10.1016/j.jmr.2011.05.001. Epub 2011 May 15. PMID: 21641247.
