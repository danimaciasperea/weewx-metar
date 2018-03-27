#
# Copyright (c) 2017-2018  Daniel Macías Perea <dani.macias.perea@gmail.com>
#
# Distributed under the terms of the GNU GENERAL PUBLIC LICENSE
#
"""Extends the Cheetah generator search list to add metar data tables.
To use it, add this generator to search_list_extensions in skin.conf:

[CheetahGenerator]
    search_list_extensions = user.metargenerator.MyMetarSearch

############################################################################################
#
# HTML Metar obtained from aviationweather.gov
#
[MetarReport]
    
    # Metar Airports to generate
    refresh_interval = 5

    [[lemd]]                           # Create a new Cheetah tag which will have a _metar suffix: $lemd_metar
    [[eddg]] 

"""

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from datetime import datetime
import time
import os.path
import weeutil.weeutil
import urllib
import syslog

class MyMetarSearch(SearchList):
    def __init__(self, generator):
        
        SearchList.__init__(self, generator)
        self.metar_dict = generator.skin_dict['MetarReport']
        
        self.refresh_interval = int(self.metar_dict.get('refresh_interval', 5))
        self.cache_time = 0      
    
        self.search_list_extension = {}        

    def get_extension_list(self, valid_timespan, db_lookup):
        """For weewx V3.x extensions. Should return a list
        of objects whose attributes or keys define the extension.

        valid_timespan:  An instance of weeutil.weeutil.TimeSpan. This will hold the
        start and stop times of the domain of valid times.

        db_lookup: A function with call signature db_lookup(data_binding), which
        returns a database manager and where data_binding is an optional binding
        name. If not given, then a default binding will be used.
        """	
        # Time to recalculate?
        if (time.time() - (self.refresh_interval * 60)) > self.cache_time:
            self.cache_time = time.time()
            
            t1 = time.time()
            ngen = 0
            for airport in self.metar_dict.sections:
                metar_name = airport + '_metar'              
                
                try:
                    self.search_list_extension[metar_name] = self.statsHTMLTable(airport)
                    ngen += 1
                except:
                    syslog.syslog(syslog.LOG_INFO, "%s: error: Cannot get Metar Report. Recovering the last file saved." % os.path.basename(__file__))                                    
                    # try to get last metar file saved
                    try:
                        with open(destination_dir + airport + ".metar", 'r') as f:
                            self.search_list_extension[metar_name] = f.read()
                    except:
                        syslog.syslog(syslog.LOG_INFO, "%s: error: There could not be found an older Metar Report. Skipping!" % os.path.basename(__file__))
                        self.search_list_extension[metar_name] = "Error - No METAR available"
                    
            t2 = time.time()

            syslog.syslog(syslog.LOG_INFO, "%s: Generated %d metar tables in %.2f seconds" %
                         (os.path.basename(__file__), ngen, t2 - t1))

        return [self.search_list_extension]

    def statsHTMLTable(self, airport):
        """
        airport: ICAO Code of Airport to generate metar
        """
        url = "https://www.aviationweather.gov/adds/metars?station_ids=%s+&std_trans=translated&chk_metars=on&hoursStr=most+recent+only&chk_tafs=on&submitmet=Get+Weather" % (airport)
        f = urllib.urlopen(url)
        myfile = f.read()
        lines = myfile.split("<TR VALIGN=")
        
        # Obtain the new METAR information and replace the airport file
        if lines[0].find("Output produced by METARs form") != -1:
            htmlText = "<TABLE style=\"border-spacing: 5px;border-collapse: inherit;line-height: 1.3;\">"
            
            for i in range(len(lines)):
                if i > 1:
                    htmlText += "<TR VALIGN=%s" % lines[i]
            
            with open(destination_dir + airport + ".metar", 'w') as f:
                f.write(htmlText)
        
        return htmlText

