# stocks2sql
 A tool for storing historical financial data in an SQL database.

This an extract, transform, load data warehousing program to pull financial equity metrics to a user defined SQL database. It first screens stocks by sector and web scrapes financial data from Yahoo Finance corresponding to each stock in a sector. These results are then stored in a database defined by the user via the GUI, or saved to a csv file if no database credentials are provided.
To begin, simply run the script by calling `stocks2sql.py' and a GUI will appear, input SQL credentials into the proper fields, and select the stock sectors to screen. This can take some time, and is more focused for amassing historical data on financial equities of a certain sector every quarter.
To install:
1. Ensure that miniconda or anaconda is installed
2. Download the stocks2sql.yaml file, unzip it, and store it somewhere on your computer.
3. Using command prompt (windows) or terminal (mac) avigate to the directory where the unzipped file is stored. Be sure that it is running a conda base environment (it should be if conda is installed correctly). This is signified by "(base)" appearing at the beginning of the command prompt.
4. `cd ~/folder_holding_unzipped_yaml`
5. `conda env create -f stocks2sql.yaml -n stocks2sql`
The last one will create an environment to run this program, plus install the program within it.

# TODO:
Add functionality to append a column to the data set stating the sector each stock is in for easier sorting.
Add csv output functionality

# DISCLAIMER
I am a biologist. This is not financial advice in any way, this was just a fun way for me to practice my data collection skills in python on a large scale.
