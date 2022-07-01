# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 14:55:40 2022

@author: micha
"""

{"town":"Holyoke"
    "parcels": [
        {"parcel_id": "1234", #Town Parcel ID
        "parcel_gis": "F_1234", #state GIS ID 
        "EJ Block Group Type": E/I/M/EI/EM/IM/EIM, #generated from state EJ GIS
        "buildings":[ #Discuss and review, we may want to flatten this into the parcel
                     
            {
            "building_id":"XXXX", #To be defined
            "Floorspace": 1234, #number in square feet, FLA 
            "year_built": XXXX, #YEAR BLT
            "Sector": "Commercial"/"Residential"/"Industrial", #from mapping  
            "BuildingType": "Single-Pre1950"/"Small MultiFamily-Pre1950", #from mapping mix of building use type and vintange
            "Shell":????
            "Gas Service":[ #list to track current and future gas service 
                {
                "id": "XXXX", #utility ID
                "parentid": "XXXX", #id of connected main
                "type": 0, 1 # 0 for legacy, 1 for replacement 
                "Operation": [binary vector] #analytical time horizon vector  
                "Install Year": XXXX,
                "Install Cost" 1234, #cost in install year 
                "Length": 99, #in feet
                "Diameter": 1, #inches
                "Material": "CI", #material code: CI-cast iron, PL-plastic, etc
                "Saftey Rating": TBD #possibly an integer based upon material type and age
                "Leak Rate": CH4 per , #reference JK's data
                "End of Life Yearr": 40 + Install year? #TO DEFINE
                }],
            "Electric Service":[ #list to track current and future gas service 
                {
                "id": "XXXX", #utility ID
                "parentid": "XXXX", #id of connected main
                "type": 0, 1 # 0 for legacy, 1 for replacement 
                "Operation": [binary vector] #analytical time horizon vector  
                "Install Year": XXXX,
                "Install Cost" 1234, #cost in install year 
                "Length": 99, #in feet
                #Need to ID elec service attributes that need to be tracked
                "End of Life Year": 40 + Install year? #TO DEFINE
                }],
            "units":[
                {"unit ID": "XXXX", #TBD
                 "Gas Meter":[ #list as gas meters will regualrly be replaced throghout gas service
                     {
                     "Operation": [binary vector] #analytical time horizon vector  
                     "ID": "XXXX", #UtilityID
                     "Meter Install Year": 20XX,
                     "Meter Install Cost": 1234,
                     "Meter Asset Value": FUNCTION #function of year and install cost,
                     "Meter Removal Cost": 234,
                     "Meter Replacement Cost": 345,
                     "Meter Leak Rate": CH4/meter,
                     "Meter Deprecation Schedule": depschedule,}
                    }],
                 "Electric Meter":[ #list as electric meters may be replaced throughout service, this might be on a longer time horizon than gas
                     {
                     "Operation": [binary vector] #analytical time horizon vector  
                     "ID": "XXXX", #UtilityID
                     "Meter Install Year": 20XX,
                     "Meter Install Cost": 1234,
                     "Meter Asset Value": FUNCTION #function of year and install cost,
                     "Meter Removal Cost": 234,
                     "Meter Replacement Cost": 345,
                     "Meter Deprecation Schedule": depschedule,
                     }
                     ],
                 "Kitchen/Ranges":[
                     {"kitchen_id":1, #Track number of kitchens in unit
                      "assets": [
                          {
                          "Operation": [binary vector] #analytical time horizon vector                        
                          "Install Year": 20XX,
                          "Install Cost": 123,
                          "Fuel":building fuel,
                          "AssetValue": function of install cost and year],
                              }
                              ]
                    
                    ]
                              
            }
                
           
            }
            
            ]
        }]
    
    }