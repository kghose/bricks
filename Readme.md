# Simple scripts for manipulating LEGO part lists

```
./bricks.py -h

./bricks.py from_owl brickowl_order_items.csv
./bricks.py to_bl brickowl_order_items.bricks
```

## Operations
1. Save BrickOwl or BrickLink purchases to an inventory of parts I have.
1. Convert a BrickOwl wishlist to a BrickLink wishlist.
1. Create a Stud.io palette from an inventory.
1. Subtract out parts used up in a build from inventory
1. Create a wishlist of low stock parts 


## Standardized CSV format

```
part,color,quantity
```

For internal manipulations I use a standardized CSV format with these columns
which matches the format that ReBrickable can import. The color code is what
ReBrickable uses which is the same as BrickLink.

A given file can stand for my inventory or the quantity needed for a model and
can be used to do subtractions and additions. 

## Naming convention

The program uses file names as metadata. The basename part of the file name is
kept fixed while the trailing part is altered based on what format it is in.

```
<prefix>.csv - BO export
<prefix>.brick - standard format, also readable by rebrickable
<prefix>.xml - Importable into Stud.io and BrickLink
```

## Appendix I

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


### Part registry

The parts list ([rebrickable-parts.csv](rebrickable-parts.csv)) is obtained from
the [Rebrickable downloads section](https://rebrickable.com/downloads/)
(parts.csv.gz). 

Some parts numbers are either missing from `parts.csv,gz` or BrickLink Stud.io uses a
different part number than what is found in that file. These parts are mapped by
hand in [missing-parts.csv](missing-parts.csv)

### Color mapping

For the BO vs BL color name/id, [this page](https://rebrickable.com/colors/) is
useful. I used Google Sheets `importhtml` function
(`importhtml("https://rebrickable.com/colors/", "table")`) to create a
spreadsheet and then a CSV with the relevant mapping. Thanks to the tip
[here](https://stackoverflow.com/questions/259091/how-can-i-scrape-an-html-table-to-csv/28083469#28083469) 
This table is stored [rebrickable-colormapping.csv](rebrickable-colormapping.csv)

## Appendix II

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

