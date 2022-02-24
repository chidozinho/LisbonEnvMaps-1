![tempsnip](https://user-images.githubusercontent.com/99036519/154965295-c1aac7d9-bcbe-4c07-af10-b0ff46810e8c.png)

# Introduction
Air quality monitoring is extremely important in today’s world as it has a direct impact on human health. The monitoring of atmosphere is extremely important as the air quality is an important problem for large communities. The main requirements for analytical devices used for monitoring air quality include a long period of autonomic operation and portability.
           This application is designed based of python repository which aims to help various users access and analytical report of certain environmental variables within the Lisbon municipality. It collects data about HUMDITY, TEMPERATURE and NOISE within a particular time interval, processes it and produce an IDW map of the variable in the form of an analytical report.
# Objectives
This project is aimed at producing a pdf report which will show the behavior of some environmental variables in Lisbon. The pdf reports will contain maps for temperature, precipitation, and noise in Lisbon, based on the data from 80 stations, maps will be generated using IDW as interpolation method, and using points for locating the stations.
The main objective is to use several open-source resources to build a solution aimed at producing a pdf report which will show the behavior of some environmental variables in Lisbon. This is done by performing the following operations:
* Extract data from online repository from ***Camara de Lisboa*
* Transform the original data by doing some cleaning and spatial operations in order to get a new perspective of the original data.
* Load the data into a database.
* Query data using dates as an interval for retrieving data from the database
* Aggregate values for each station for the period interval selected
* Create an IDW (Inverse Distance Weighting) raster surfaces using each of the chosen variable based on the various sensor points to map and see the distribution of noise in the
* Display the values for each variable using a plotted raster surface color ramp
* Create a pdf report with the plots for each environmental variable.
* Grant users access to retrieve data from the database connection using API.
* Generate a GUI interface where the user executes the program.
___________________________________________________________________________________________
# Data /Database 
The data comes from “camera municipal de Lisboa” “lisboa-aberta” (http://lisboaaberta.cmlisboa.pt/index.php/pt/dados/conjuntos-de-dados) with sensors deployed in 80 locations for monitoring the environmental parameters across Lisbon municipality which were aggregated on a daily basis.The database contains variables populated through the Python code and then stored in a table within a SQL database. The first table contains information about the environmental variables, such as their full name, ID and date. In the same database, there is another table that defines the environmental variables, such as their full name, ID and date as well as the sensor ID freguesia and address, which is the user interface. The database is updated every day by a schedular that runs every six (6) hours initiated by the ETL process.

# System Requirements 
• Python 3.10.2 or later.
• Postgres database.
• Text editor or ide for coding recommended VisualStudio Code.
• python packages listed in the requirements.txt file


# Project Structure

The project has four main elements:
• **ETL module:** in charge of extracting information from the source, transform and clean data, and the load operation, storaging into postgresql database
• **Report module:** composed of 2 python scripts which are in charge of retrieving data from the database, perform the geographic operations for interpolation, plotting maps and creating the pdf document.
• **User Module:** Very small frontend point where users select the dates of their interest to create the report. This module is composed of a python script, html template and css style file.
• **API Module:** end points where users can get information from the database. The module is composed of one python script ( the same used to create the web page).

# Workflow Explanation

The data comes from the **CAMERA DE LISBOA**, they have in their website values that monitor the envoronment in Lisbon city. They have almost 80 sensors across the city.

![image](https://user-images.githubusercontent.com/38009811/155448892-0ef72785-3505-460a-8128-0f76debf86a7.png)

The have a url endpoint where community can access to the almost real time data its updated each hour.

![image](https://user-images.githubusercontent.com/38009811/155449369-8db96a01-2ff5-4102-bce8-daa491a310a4.png)

Using the ETL module we storage information that we extract from that url in a table in a postgres database.

Once the data in in the table, there is a Trigger which runs a database function that performs a spatial intersection in order capture the Fragesia's name and station's address from two spatial tables in the same database.

![image](https://user-images.githubusercontent.com/38009811/155449985-908aa5b5-db96-4704-b44e-064c153309cb.png)

The ETL module runs automatically every day without user supervision, using the task scheduler tool in windows. The lisbon.bat file has the configuration to run the ETL module

Using a webpage users run the scripts in the backend in charge to create the pdf file with the information about the average values for Temprature, Noise and Humidity in Lisbon.
the first part has a map with idw interpolation values for the time period selected and the second part is a bar graph with the average for whole lisbon in each day during the time period selected.

![image](https://user-images.githubusercontent.com/38009811/155451369-7db1a8f2-06b8-437a-9212-0fe8d40ecbfe.png)

The process in the backend runs a query to get data from the database, convert that data in a pandas dataframe, then dataframe is merge with geojson file of stations or sensors.
Using those point features the interpolation operation using IDW method is perfomed and the results go to a temporal folder as tif files. Afterwards a plot from the tif file is created setting the color ramp for legend and countours from the pixel values, those plots are saved as png files.
The last step is to put the plots in the pdf file and the text which tells to the user what is each image about.

 # Running the application
• The ETL runs automatically, using task scheduller in windows, the task runs a bat file called lisbon.
• The project's main result is the pdf report, webpage runs locally in http://localhost:5001/, the script which launchs the webpage is **webapp.py**

**Note:** Users interested in running this project in their machines can clone the repository or download the zip file repository. Before to run the scripts users will need to install the python packages listed in requeriments.txt

# Output and Visualization.
Using the Python based end-user data retrieval file, the analytical report is presented on a map in pdf format together with the average values recorded by the various sensors

![hum map](https://user-images.githubusercontent.com/99036519/155208685-308f501f-bc61-4aef-a4a2-c7212cc85b5d.JPG)







