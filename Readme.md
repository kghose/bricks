# Simple scripts for manipulating LEGO part lists

## owl2link

`./owl2link.py brickowl_order_items.csv bricklink_studio.xml`

My primary goal is to take a BrickOwl list exported as CSV and turn it into a
BrickLink XML that can be imported into Stud.io. This way I can keep track of
what I can build with the parts that I have.

This XML can also be imported into BrickLink, allowing for price comparisons
etc. 

The challenges in the conversion are 
1. Parsing the part ID from the name, which is a freefrom string
1. When there are multiple part IDs, figuring out which part ID BrickLink
   Stud.io recognizes 
1. Converting the BO color name to a code BrickLink Stud.io understands


For the BO vs BL color name/id, [this page](https://rebrickable.com/colors/) is
useful. I used Google Sheets `importhtml` function
(`importhtml("https://rebrickable.com/colors/", "table")`) to create a
spreadsheet and then a CSV with the relevant mapping. Thanks to the tip
[here](https://stackoverflow.com/questions/259091/how-can-i-scrape-an-html-table-to-csv/28083469#28083469) 


## Appendix

BrickOwl CSV format:
```
"Order Id",Name,Type,"Color Name",Boid,"Lot Id",Condition,"Ordered Quantity","Public Note","Base Price"
3351561,"LEGO Medium Stone Gray Axle 7 (44294)",Part,"Medium Stone Gray",29003-64,71762615,New,2,,0.053
3351561,"LEGO Dark Stone Gray Angle Connector #2 (180º) (32034 / 42134)",Part,"Dark Stone Gray",589908-50,33583825,New,4,,0.239
```

BrickLink XML format (https://www.bricklink.com/help.asp?helpID=207):
```
<INVENTORY>
  <ITEM>
    <ITEMTYPE>P</ITEMTYPE>
    <ITEMID>3622</ITEMID>
    <COLOR>11</COLOR>
    <QTYFILLED>4</QTYFILLED>
  </ITEM>
  <ITEM>
    <ITEMTYPE>P</ITEMTYPE>
    <ITEMID>3039</ITEMID>
  </ITEM>
  <ITEM>
    <ITEMTYPE>P</ITEMTYPE>
    <ITEMID>3001</ITEMID>
    <COLOR>5</COLOR>
    <MAXPRICE>1.00</MAXPRICE>
    <MINQTY>100</MINQTY>
    <CONDITION>N</CONDITION>
    <REMARKS>for MOC AB154A</REMARKS>
    <NOTIFY>N</NOTIFY>
  </ITEM>
</INVENTORY>
```

