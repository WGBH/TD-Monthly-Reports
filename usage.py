#!/usr/bin/python
import sys
import xlwt as pycel
import datetime


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


def open_workbook():
    wb = pycel.Workbook()
    return wb

def close_workbook(wb, s):
    wb.save("EXCEL/%s.xls" % s)

############################################################################
### Metrics

def get_usage_data():
    c = {} # the data
    rows = [line[:-1] for line in open('DATA/usage_all.tsv')]
    for row in rows:
        if 'month' in row: continue # header line
        (metric, country, state, month, count) = row.split('\t')
        if country != 'us': continue # for now just do US
        if metric not in c.keys(): c[metric] = {}
        if len(state) < 2: state = 'unknown'
        this_key = (state, month)
        # print "metric: %s  state: %s  month: %s  count: %d" % (metric, state, month, int(count))
        if this_key in c[metric].keys():
            c[metric][this_key] += count
        else:
            c[metric][this_key] = count
    return c

def get_visit_data():
    v = {}
    rows = [line[:-1] for line in open('DATA/access_all.tsv')]
    for row in rows:
        if 'month' in row: continue #header line
        (metric, country, state, month, count) = row.split('\t')
        if country != 'us': continue  # for now, just do US
        if metric not in v.keys(): v[metric] = {}
        if len(state) < 2: state = 'unknown'
        this_key = (state, month)
#        print "metric: %s  state: %s  month: %s  count: %d" % (metric, state, month, int(count))
        if this_key in v[metric].keys():
            v[metric][this_key] += count
        else:
            v[metric][this_key] = count
    return v

def get_state_list(d):
    l = [state for (state, month) in d['logins'].keys()]
    return list(set(l))

def get_month_list(d):
    l = [month for (state, month) in d['asset_visit'].keys()]
    s = list(set(l))
    s.sort()
    return s

#def get_top100_data():
#    t = {}
#    rows = [line[:-1] for line in open('DATA/top100_all.tsv')]
#    for row in rows:
#        if 'month' in row: continue # header line
#        (metric, country, state, month, code, count) = row.split('\t')
#        if country != 'us': continue  
#        if metric not in t.keys(): t[metric] = {}
#        if length(state) < 2: state = 'unknown'
#        this_key = (state, month)
#        t[metric][this_key] = (code, count)
#    return t
    
#def create_top_100(t, state, month, metric):
# create a list of tuples (code, n) ordered by n desc for the key [metric][(state, month)]
#    l = []
#    if length(l < 100): 
#        return l
#    else 
#        return l[0:99]




def do_access_sheet(wb, counts, months, state):
    access_metrics = {
        ('visits', 'state')     : ( 1, "%s Visits"),
        ('visits', 'us')        : ( 3, "US Visits"),
        ('logins', 'state')     : ( 2, "%s Logins"),
        ('logins', 'us')        : ( 4, "US Logins"),
    }
    metric_list = ['visits', 'logins']
    ws = wb.add_sheet('Access')
    
    row = 1
    write(ws, row, 0, 'Month', fmt['text_bold'])
    for metric in metric_list:
        for scope in ['state', 'us']:
            col = access_metrics[(metric, scope)][0]
            if scope == 'state':
                data = access_metrics[(metric, scope)][1] % state
            else:
                data = access_metrics[(metric, scope)][1]
            write(ws, row, col, data, fmt['text_bold'])
    row = 2
    for month in months:
        write(ws, row, 0, month, fmt['text'])
        for metric in metric_list:
            if metric in counts and (state, month) in counts[metric].keys():
                data = counts[metric][(state, month)]
                col = access_metrics[(metric, 'state')][0]
                write(ws, row, col, data, fmt['int_regular'])
            if metric in counts and ('all', month) in counts[metric].keys():
                data = counts[metric][('all', month)]
                col = access_metrics[(metric, 'us')][0]
                write(ws, row, col, data, fmt['int_regular'])
        row += 1
    return

def do_usage_sheet(wb, counts, months, state):
    usage_headers = {
        (1, 4) : "Asset Views",
        (6, 9) : "Resource Views",
        (11, 13) : "Downloads (login required to DL)",
        (14, 15) : "Page Views"
    }
    usage_metrics = {
        ('asset_visit', 'state')     : ( 1, "All %s Visits"),
        ('asset_login', 'state')     : ( 2, "%s Logins",),
        ('asset_visit', 'us')        : ( 3, "All US Visits"),
        ('asset_login', 'us')        : ( 4, "All US Logins"),
        ('resource_visit', 'state')  : ( 6, "All %s Visits"),
        ('resource_login', 'state')  : ( 7, "%s Logins"),
        ('resource_visit', 'us')     : ( 8, "All US Visits"),
        ('resource_login', 'us')     : ( 9, "All US Logins"),
        ('download', 'state')        : (11, "%s Logins"),
        ('download', 'us')           : (12, "US Logins"),
        ('page_hits', 'state')       : (14, "All %s Visits"),
        ('page_hits', 'us')          : (15, "All US Visits"),
    }
    metric_list = ['asset_visit', 'asset_login', 'resource_visit', 'resource_login', 'download', 'page_hits']
    
    ws = wb.add_sheet('Usage')
    for t in usage_headers.keys():
        label = usage_headers[t]
        (start_col, end_col) = t
        write_merged(ws, 0, 0, start_col, end_col, label, fmt['text_bold'])
    row = 1
    write(ws, row, 0, 'Month', fmt['text_bold'])
    for metric in metric_list:
        for scope in ['state', 'us']:
            col = usage_metrics[(metric, scope)][0]
            if scope == 'state':
                data = usage_metrics[(metric, scope)][1] % state
            else:
                data = usage_metrics[(metric, scope)][1]                        
            write(ws, row, col, data, fmt['text_bold'])
    row = 2
    for month in months:
        write(ws, row, 0, month, fmt['text'])
        for metric in metric_list:
            if metric in counts and (state, month) in counts[metric].keys():
                data = counts[metric][(state, month)]
                col = usage_metrics[(metric, 'state')][0]
                write(ws, row, col, data, fmt['int_regular'])
            if metric in counts and ('all', month) in counts[metric].keys():
                data = counts[metric][('all', month)]
                col = usage_metrics[(metric, 'us')][0]
                write(ws, row, col, data, fmt['int_regular'])
        row += 1
    return

########################################################################
### MAIN PROGRAM
if __name__ == "__main__":
    counts = get_usage_data()
    visits = get_visit_data()
    print "Data Collected" 
    month_list = get_month_list(counts)
    state_list = get_state_list(visits)
    
    this_month = max(month_list)
    print month_list
    print "This Month: %s" % this_month
    month_rev = month_list[:]
    month_rev.reverse()

    for state in state_list:
#        print "\tDoing State %s: " % state,
        if state in ['unknown', 'all']: continue
        wb = open_workbook()
        do_access_sheet(wb, visits, month_rev, state)
#        print "\tAccess",
        do_usage_sheet(wb, counts, month_rev, state)
#        print "\tUsage"
        close_workbook(wb, "usage_%s-%s" % (this_month, state))
