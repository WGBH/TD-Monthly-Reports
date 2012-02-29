#!/usr/bin/python
import sys
import xlwt as pycel
import datetime


STYLE_FACTORY = {}
FONT_FACTORY = {}

# List of states/etc.
state_names = {
    'us': 'United States',
#    'aa': 'Amer. Armed Forces - Americas', 'ae': 'Amer. Armed Forces - Europe', 'ap': 'Amer. Armed Forces - Pacific',
#    'as': 'American Samoa', 'fm':'Fed. States of Micronesia','mp':'MP?','pw':'Palau',
    'ak': 'Alaska', 'al':'Alabama','ar':'Arkansas','az':'Arizona','ca':'California','co':'Colorado','ct':'Connecticut',
    'dc': 'District of Columbia', 'de':'Delaware','fl':'Florida','ga':'Georgia','hi':'Hawaii','ia':'Iowa','id':'Idaho',
    'il': 'Illinois', 'in':'Indiana', 'ks':'Kansas', 'ky':'Kentucky','la':'Louisiana','ma':'Massachusetts','md':'Maryland',
    'me': 'Maine','mi':'Michigan','mn':'Minnesota','mo':'Missouri','ms':'Mississippi','mt':'Montana','nc':'North Carolina',
    'nd': 'North Dakota','ne':'Nebraska','nh':'New Hampshire','nj':'New Jersey','nm':'New Mexico','nv':'Nevada','ny':'New York',
    'oh': 'Ohio', 'or':'Oregon','ok':'Oklahoma','pa':'Pennsylvania','pr':'Puerto Rico','ri':'Rhode Island','sc':'South Carolina',
    'sd': 'South Dakota','tn':'Tennessee','tx':'Texas','ut':'Utah','va':'Virginia','vi':'Virgin Islands','vt':'Vermont',
    'wa': 'Washington', 'wi': 'Wisconsin', 'wv': 'West Virginia', 'wy':'Wyoming',
    'gu':'Guam',
}

# List of affiliates by state
state_affil_list = {
    'az': ['kaet'],
    'ca': ['kqed'],
    'co': ['rmpbs'],
    'fl': ['wsre'],
    'ia': ['iptv'],
    'in': ['wfyi'],
    'ky': ['ket'],
    'ma': ['wgbh','wgby'],
    'mn': ['tpt'],
    'ms': ['mpb'],
    'nc': ['unc'],
    'nd': ['prairiepublic'],
    'nh': ['nhptv'],
    'nm': ['knme'],
    'nv': ['vegas'],
    'ny': ['mlpbs','wcny','wliw','wmht','wned','wnet','wpbs','wskg','wxxi'],
    'oh': ['odc'],
    'pa': ['wpsu','witf','wqln','wlvt','wvia'],
    'sd': ['sdpb'],
    'tn': ['wnpt'],
    'wi': ['ecb'],
    'wy': ['wyoming'],
}
other_affil_seen = {}
user_type_list = ['teacher', 'student', 'other']

# Where to start the monthly reporting.
min_month_to_report = '2007-05'
min_download_month  = '2007-06'   # downloads weren't available before this month!

c = {
    ('reg', 'total', 'month'):    (1, 'Monthly Total'), 
    ('reg','total','cum'):    (2, 'Cum. Total'),
    ('reg', 'teacher', 'month'):  (3, 'Monthly Teachers'),
    ('reg','teacher','cum'):  (4, 'Cum. Teachers'),
    ('reg', 'student', 'month'):  (5, 'Monthly Students'),
    ('reg','student','cum'):  (6, 'Cum. Students'),       
    ('reg', 'other', 'month'):    (7, 'Monthly All Others'), 
    ('reg','other','cum'):    (8, 'Cum. All Others'),
}

line1 = {
    'reg': (1, 8, "REGISTRATION"),
}
# this handles the second line header in the internal reports.
# Again, the keys here are completely arbitrary.
line2 = {
    'reg1': (1, 2, "(all users)"),
    'reg2': (3, 6, "(users by type)"),
}

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

########################################################################
### METRICS
def get_registration_data():
    c = {} # The data
    rows = [line[:-1] for line in open('DATA/reg_all.tsv')]  # removes newlines
    for row in rows:
        if 'user_type' in row: continue  # ignore header lines
        [metric, scope, month, affiliate, users, n]  = row.split('\t')
        this_aff = affiliate.lower()
        this_scope = scope.lower()
        if this_scope in ('us', 'world'):
            pass
        elif this_aff[0:4] == 'all_':
            pass
        elif this_scope in state_affil_list.keys():
            if this_aff not in state_affil_list[this_scope]:
                if this_scope not in other_affil_seen.keys(): other_affil_seen[this_scope] = []
                if this_aff not in other_affil_seen[this_scope]:
                    other_affil_seen[this_scope].append(this_aff)
                this_aff = 'other'
        else:
            continue
        
        this_key = (this_scope, this_aff, month, users.lower())
        c[this_key] = int(n)
    return c
    
def get_month_list(k):
    """
        JUST IN CASE there are gaps, handle them!
    """
    # the j1, j2, vars are just "junk" to scoop out the appropriate axis in the key list
    l = [m for (j1, j2, m, j4) in k]
    low = min(l).split('-')   # two element list of year, month
    high = max(l).split('-')  # ditto
    m = []
    # loop from lowest month YYYY-MM to highest and build a COMPLETE list.
    for this_m in range(int(low[1]), 13):
        m.append("%04d-%02d" % (int(low[0]), this_m))
    for this_y in range(int(low[0])+1, int(high[0])):
        for this_m in range(1, 13):
            m.append("%04d-%02d" % (this_y, this_m))
    for this_m in range(1, int(high[1])+1):
        m.append("%04d-%02d" % (int(high[0]), this_m))
    # remove last month if still in it!
    # the queries aren't smart enough to remove partial months.
    # so, by truncating the month list if we're still "in" the month, 
    # the workbook won't have partial months.
    this_month = datetime.date.today().strftime("%Y-%m")
    while(max(m) >= this_month):
        m.pop()
    return m
    
def convert_month_to_text(month):
    names = ['','January','February','March','April','May','June','July','August','September','October','November','December']
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    (yyyy, mm) = month.split('-')
    y = int(yyyy)
    m = int(mm)+0
    leap = 0
    if(m == 2):
        if(y % 4 == 0):
            if(y % 100 != 0):
                leap = 1
            elif(y % 400 == 0):
                leap = 1
    return "%s %d, %d" % (names[m], days[m]+leap, y)

def get_state_list(k):
    # Instead of worrying which states get reports, just assume that everything that
    # comes in defines that list.
    # j1, j2, etc. are junk - filtering on the key tuple for state
    if len(sys.argv) > 1:    # command line argument is list of state abbreviations, comma-separated
        s = sys.argv[1].split(',')
    else:
        l = [s for (s, j2, j3, j4) in k]
        s = list(set(l))
    return s
    
def get_cumulate_data(counts, states, months):
    scope_list = states[:]
    scope_list.extend(['us','world'])

    cum = {}
    l = [(scope, aff, users) for (scope, aff, m, users) in counts.keys() if scope in scope_list]
    s = set(l) # make unique
    for z in s: 
        total = 0
        for m in months:
            this_key = (z[0], z[1], m, z[2])
            if this_key not in counts.keys():
                c = 0
            else:
                c = counts[this_key]
            total += c
            cum[this_key] = total
    return cum

def tabulate(ws, counts, report, affil, m, row, this_fmt):
    t_month = t_users = t_assets = 0

### Phase 1: put in monthly value for each user type    
    for u in user_type_list:
        this_key = (report, affil, m, u)
        this_number = this_users = this_assets = 0
        if this_key in counts.keys():
            this_number = counts[this_key]
            this_users = 0 # counts[this_key][1]

        attempt_cell_fill(ws, row, (u, 'month'), this_number, this_fmt)
        t_month += this_number
        t_users += this_users       
    # monthly totals
    attempt_cell_fill(ws, row, ('total', 'month'), t_month, this_fmt)

### Phase 2: cumulative totals
    all_cum = 0
    for u in user_type_list:
        this_key = (report, affil, m, u)
        if this_key not in cumulate.keys():  # no data
#           print "ERROR!  Can't find cumulate data for ", this_key
            this_value = 0
        else:
            this_value = cumulate[this_key]
        all_cum += this_value
        attempt_cell_fill(ws, row, (u, 'cum'), this_value, this_fmt)
    # cumulative totals
    if all_cum > 0: attempt_cell_fill(ws, row, ('total', 'cum'), all_cum, this_fmt)
    
def attempt_cell_fill(ws, row, col_key, this_number, this_fmt):
    if col_key not in c.keys(): return
    write(ws, row, c[col_key], this_number, this_fmt)
    
def do_format_worksheet(ws, row, ws_type, ws_title, state):
    ws.fit_num_pages = 1
    ws.fit_height_to_pages = 0
    ws.fit_width_to_pages = 1
    ws.paper_size_code = 1
    ws.portrait = 0    # Set to landscape

    if(ws_type == 'us'):
        title = ws_title
    elif(ws_type == 'state'):
        title = 'ALL %s' %  ws_title
    elif(ws_type == 'affil'):
        title = '%s' % ws_title

# Sheet Headers
    write_merged(ws, 0, 0, 0, 60, "Stats for %s" % title, fmt['big_bold'])
#    write_merged(ws, 1, 1, 0, 60, "(See the Details worksheet for definitions, etc.)", fmt['little_italic'])
    if ws_title.upper() == 'OTHER': write_merged(ws, 2, 2, 0, 60, "Included: %s" % ', '.join(other_affil_seen[state]), fmt['little_italic'])

# Line 1 headers --- NEED TO REFACTOR!
    for h in line1.keys():
        col_start = line1[h][0]
        col_end = col_start + line1[h][1] - 1
        write_merged(ws, row, row, col_start, col_end, line1[h][2], fmt['text_bold'])

# Line 2 headers ---
    for h in line2.keys():
        col_start = line2[h][0]
        col_end = col_start + line2[h][1] - 1
        write_merged(ws, row+1, row+1, col_start, col_end, line2[h][2], fmt['little_italic'])

# Line 3 headers
    write(ws, row+2, 0, "Month", fmt['header'])
    for h in c.keys():
        write(ws, row+2, c[h][0], c[h][1], fmt['header'])

def do_worksheet(wb, counts, ws_type, state=None, affil=None):
    if(ws_type == 'us'): 
        title = 'US TD'
        report = 'us'
        affil = 'us_td'
    elif(ws_type == 'state'): 
        title = state_names[state.lower()]
        report = state
        affil = 'all_%s' % state
    elif(ws_type == 'affil'): 
        title = affil.upper()
        if title == 'WYOMING': 
            title = 'WYOMING PBS'  ### THIS IS A HUGE HACK.  Sorry!  RAD 20100601
        report = state
    else:
        return
    ws = wb.add_sheet(title)
    header_row = 4
    do_format_worksheet(ws, header_row, ws_type, title, state)
    row = header_row + 3

    this_date_fmt = fmt['text_bold']
    this_n_fmt = fmt['int_bold']
    for m in month_rev:
        if m < min_month_to_report: continue
        write(ws, row, 0, m, this_date_fmt) # Month number
        tabulate(ws, counts, report, affil, m, row, this_n_fmt)
        row += 1
        this_date_fmt = fmt['text']
        this_n_fmt = fmt['int_regular']
    return
    
def do_summary(wb, d, state, affil_list, this_month):
    ws = wb.add_sheet('Summary')
    # Format the worksheet: set general stuff.
    ws.fit_num_pages = 1
    ws.fit_height_to_pages = 0
    ws.fit_width_to_pages = 1
    ws.paper_size_code = 1 
    ws.portrait = 0   # landscape

    write_merged(ws, 0, 0, 0, 60, '%s TD Metrics: %s' % (state_names[state.lower()], convert_month_to_text(this_month)), fmt['big_bold'])


########################################################################
### MAIN PROGRAM
if __name__ == "__main__":
    registrations = get_registration_data()
    print "Data collected."
    month_list = get_month_list(registrations.keys())
    this_month = max(month_list)
    state_list = get_state_list(registrations.keys())
    cumulate = get_cumulate_data(registrations, state_list, month_list)
    print "Cumulation complete."
    month_rev = month_list[:]
    month_rev.reverse()

    for s in state_list:
        if s not in state_names.keys(): continue
        if s in ('us', 'world'): continue
        print "Starting state %s:" % s
        if s in state_affil_list.keys():
            this_affil_list = state_affil_list[s]
            this_affil_list.append('other')
        else: this_affil_list = []
        
        wb = open_workbook()
        print "\tSummary sheet"
        do_summary(wb, registrations, s, this_affil_list, this_month)
        # put in world sheet
        print "\tUS Sheet"
        do_worksheet(wb, registrations, 'us')
        print "\t state %s sheet" % s
        do_worksheet(wb, registrations, 'state', state=s)
        for w in this_affil_list:
            print "\t\tSheet for %s" % w
            do_worksheet(wb, registrations, 'affil', state=s, affil=w)
    
        close_workbook(wb, "reg_%s-%s" % (this_month, s))
