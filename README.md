# metar
Augment Weewx station data with Metar reports obtained from aviationweather.gov

Extends the Cheetah generator search list to add metar data tables.
To use it, add this generator to search_list_extensions in skin.conf:


	[CheetahGenerator]
		search_list_extensions = ...,user.metargenerator.MyMetarSearch
		
And include the following section with the list of airports in which you are interested

	[MetarReport]  
		refresh_interval = 5	# Obtain every X minutes	
		# Metar Airports to generate			
			[[eddg]]	# Create a new Cheetah tag which will have a _metar suffix: $lemd_eddg
			[[lemd]]			
