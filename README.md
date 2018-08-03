# DataDisplay
## A GUI Data Display using [the buildingEnergyAPI](https://github.com/navkal/buildingEnergyApi) to get and display live air data for Andover High School (AHS).

##### This project was written as a part of the Energize Andover program in 2018. For more information, check out my [blog documenting our day to day activities](https://danivenergy.weebly.com/).

In order to run this program, make sure your root directory is structured like so:

```
root-directory-name-here/
├──CSVs/
│   ├── ahs_air.csv
│   ├── ahs_air_data.csv (Optional, not included in repository but will be created after first run)
│   ├── default-data.csv (Optional, but strongly reccomended, as it improves performance)
├── DataDisplay.py
└── bacnet_gateway_requests.py
```

And then run **DataDisplay.py**
