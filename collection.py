#!/usr/bin/python
import sys
import xlwt as pycel
import datetime

sheet_metadata = {
    'resource' : {'title': 'Resource Page Views', },
    'asset'    : {'title': 'Asset Views', },
    'download' : {'title': 'Downloads', },
}

sheet_list = sheet_metadata.keys()

STYLE_FACTORY = {}
FONT_FACTORY = {}

# The style dictionary is cumbersome.   Ideally I should build a library
# of individual traits that are joined together in the style entry.
# For now this'll do
fmt = {
    "int_regular" : {"font": (("height",200),), "format":"##,##0"},
    "int_bold" : {"font": (("height",200),("bold",True)), "format":"##,##0"},
    "percent" : {"font":(("height",200),),"format":"0.0%"},
    "percent_bold" : {"font":(("height",200),("bold",True)),"format":"0.0%"},
    "big_bold" : {"font":(("height",280),("bold",True))},
    "little_italic" : {"font":(("height",200),("italic",True))},
    "text" : {"font":(("height",200),)},
    "text_right" : {"font":(("height",200),), "alignment":(("wrap", pycel.Alignment.WRAP_AT_RIGHT,),("horz", pycel.Alignment.HORZ_RIGHT,))},
    "text_bold" : {"font":(("height",240),("bold",True))},
    'header' : { "font":(("height",240),("bold", True)), "alignment":(("wrap", pycel.Alignment.WRAP_AT_RIGHT,),("horz", pycel.Alignment.HORZ_CENTER,))},
    'rjus_bold' : { "font":(("height",240),("bold", True)), "alignment":(("wrap", pycel.Alignment.WRAP_AT_RIGHT,),("horz", pycel.Alignment.HORZ_RIGHT,))},
}

######## XLRT support functions ########
def write(ws, row, col, data, style=None):
    """
    Write data to row, col of worksheet (ws) using the style
    information.
    Again, I'm wrapping this because you'll have to do it if you
    create large amounts of formatted entries in your spreadsheet
    (else Excel, but probably not OOo will crash).
    """
# If you make changes and you get a runtime error where you're trying
# to write to the same cell twice, uncomment this to see the flow of positions.
#    print "AT: ROW ", row, " COL ", col
    if style:
        s = get_style(style)
        ws.write(row, col, data, s)
    else:
        ws.write(row, col, data)


# Actually I wrote this one myself.
def write_merged(ws, start_row, end_row, start_col, end_col, data, style=None):
    """
    Do merged cell writing.   Allows inflation in both rows and columns.
    """
#    print "AT: ROW ", start_row, " COL ", start_col
    if style:
        s = get_style(style)
        ws.write_merge(start_row, end_row, start_col, end_col, data, s)
    else:
        ws.write_merge(start_row, end_row, start_col, end_col, data)


def get_style(style):
    """
    Style is a dict maping key to values.
    Valid keys are: background, format, alignment, border
    The values for keys are lists of tuples containing (attribute,
    value) pairs to set on model instances...
    """
    style_key = tuple(style.items())
    s = STYLE_FACTORY.get(style_key, None)
    if s is None:
        s = pycel.XFStyle()    
        for key, values in style.items():
            if key == "background":
                p = pycel.Pattern()
                for attr, value in values:
                    p.__setattr__(attr, value)
                s.pattern = p
            elif key == "format":
                s.num_format_str = values
            elif key == "alignment":
                a = pycel.Alignment()
                for attr, value in values:
                    a.__setattr__(attr, value)
                s.alignment = a
            elif key == "border":
                b = pycel.Formatting.Borders()
                for attr, value in values:
                    b.__setattr__(attr, value)
                s.borders = b
            elif key == "font":
                f = get_font(values)
                s.font = f
        STYLE_FACTORY[style_key] = s
    return s


def get_font(values):
    """
    'height' 10pt = 200, 8pt = 160
    """
    font_key = values
    f = FONT_FACTORY.get(font_key, None)
    if f is None:
        f = pycel.Font()
        for attr, value in values:
            f.__setattr__(attr, value)
        FONT_FACTORY[font_key] = f
    return f
    
########################################################################
def get_data():
    d = {} # this is the matrix of data
    rows = [line[:-1] for line in open ('DATA/collection_all.tsv')]  # removes newlines
    for row in rows:
        if 'month' in row: continue # filter header from SQL output
        [metric, month, code, count] = row.split('\t')
        this_key = (metric, month, code)

        d[this_key] = count
    return d
    
def get_collection_list(d):
# should grab from collections.tsv so as to have title information
    collection_list = {}
    rows = [line[:-1] for line in open ('DATA/collection_list.tsv')]
    for row in rows:
        if 'code' in row: 
            continue
        [code, title, partner_code, n_resources] = row.split('\t')
        this_title = title.decode('ascii','ignore')
        collection_list[code] = {}
        collection_list[code]['title'] = this_title
        collection_list[code]['n_resources'] = n_resources
        collection_list[code]['partner_code'] = partner_code
#    l = [c for (j1, j2, c) in d.keys()] 
#    collection_list = list(set(l))
    return collection_list

def get_month_list(d):
    l = [c for (j1, c, j2) in d.keys()]
    low = min(l).split('-')
    high = max(l).split('-')
    print "low = %s high = %s" % (low, high)
    m = []
    for this_m in range(int(low[1]),13):
        m.append("%04d-%02d" % (int(low[0]), this_m))
    for this_y in range(int(low[0])+1, int(high[0])+1): 
        for this_m in range(1, 13): 
            m.append("%04d-%02d" % (int(this_y), this_m))
    # get rid of current month if still in it!
    this_month = datetime.date.today().strftime("%Y-%m")
    while(max(m) >= this_month): m.pop()
    this_month = max(m)
    return this_month, m

def open_workbook():
    wb = pycel.Workbook()
    return wb
    
def close_workbook(wb, s):
    wb.save("EXCEL/%s.xls" % s)

def do_header(ws, sheet, this_row, months):
    h = ['Code', 'Title', '# Resources', 'Partner']
    n = 0
    for this_h in h:
        write(ws, this_row, n, this_h, fmt['text_bold'])
        n += 1
    for this_m in months:
        write(ws, this_row, n, this_m, fmt['text_bold'])
        n += 1

def do_sheet(wb, sheet, d, c, m):
    ws = wb.add_sheet('%s' % sheet)

    # Format the worksheet: set general stuff.
    ws.fit_num_pages = 1
    ws.fit_height_to_pages = 0
    ws.fit_width_to_pages = 1
    ws.paper_size_code = 1 
    ws.portrait = 0   # landscape
    
    write_merged(ws, 0, 0, 0, 60, 'Collection Metrics - %s' % sheet_metadata[sheet]['title'], fmt['text_bold'])
    
    start_row = 3
    do_fill_sheet(ws, d, c, m, sheet, start_row)
    
def do_fill_sheet(ws, d, c, m, sheet, start_row=3):
    this_row = start_row
    do_header(ws, sheet, this_row, m)

    this_row += 1
    for this_collection in c.keys():
        write(ws, this_row, 0, this_collection)
        if this_collection in c.keys():
            write(ws, this_row, 1, c[this_collection]['title'])
            write(ws, this_row, 2, int(c[this_collection]['n_resources']), fmt['int_regular'])
            write(ws, this_row, 3, c[this_collection]['partner_code'])
        this_col = 4
        for this_month in m:
            this_key = (sheet, this_month, this_collection)
            if this_key in d.keys():
                write(ws, this_row, this_col, int(d[this_key]), fmt['int_regular'])
            else:
                write(ws, this_row, this_col, 0, fmt['int_regular'])
            this_col += 1
        this_row += 1

### MAIN PROGRAM
if __name__ == "__main__":
    
    the_data = get_data()
    collection_list = get_collection_list(the_data)
    (this_month, month_list) = get_month_list(the_data)
    print "month list = %s" % month_list
    last_month = month_list[-1]
    
#    print "Last Month: %s" % last_month
    
    wb = open_workbook()
    for sheet in sheet_list:
        print "\tDoing %s" % sheet
        do_sheet(wb, sheet, the_data, collection_list, month_list)
    close_workbook(wb, "collection_%s" % last_month)
