# ebayAuctionFinder
 Quickly search for multiple items on ebay and return a list of filtered auctions

This tool allows you to quickly search multiple items on ebay, and it will filter through active listings and highlight auctions that are (1) ending today, are (2) below the minimum listing price, and (3) have at least one bid. 

The logic behind the three filters is provided below. 
(1) So you can purchase the item today and physically have your item sooner. 
(2) If the auction price is below the minimum listing price, it should be the cheapest listing avialable. This is an indication that the auction is undervalued, and therefore is a good deal. 
(3) Having at least one bid helps filter out clickbait-y, unrelated, or uninteresting listings. The assumption that if an item has at least one bid, another ebay user has found the auction interesting, so might you. 

Filters (2) and (3) have been combined to find auctions that are below the minimum listing price, and have at least one bid. This is an indication that the auctions is both a good deal, and other ebay users think so as well and may be of interest to you.    

Requires 'keywords.csv' file to run properly. 
The first column contains the name of the item you want to search for. The second column consists of any applicable folders. An example .csv, keywords_sample.csv has been provided as a template.

The filtered listings for every item in the keywords.csv is saved in the DataFrame 'UniqueListings'. Unfiltered listings are found in the DataFrame 'AllListings'. In either DataFrame, you will find the name of the item, the current price and shipping cost of the item, the bid count, the acution end date, the auction URL, as well as the type of filter used for that paricular auction. 
