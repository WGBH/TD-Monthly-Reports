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
    'ga': ['wfsu'],
    'ia': ['iptv'],
    'in': ['wfyi','wnin'],
    # 'il': [], # wnin?
    'ky': ['ket'], # wnin?
    'la': ['wyes'],
    'ma': ['wgbh','wgby'],
    'mn': ['tpt'],
    'mo': ['kcpt'],
    'ms': ['mpb'],
    'nc': ['unc'],
    'nd': ['prairiepublic'],
    'nh': ['nhptv'],
    'nm': ['knme'],
    'nv': ['vegas'],
    'ny': ['mlpbs','wcny','wliw','wmht','wned','wnet','wpbs','wskg','wxxi'],
    'oh': ['odc'],
    'pa': ['wpsu','witf','wqln','wlvt','wqed','wvia'],
    'sc': ['scetv'],
    'sd': ['sdpb'],
    'tn': ['wnpt'],
    'tx': ['kacv'],
    'va': ['wvpt'],
    'vt': ['vpt'],
    'wi': ['ecb'],
    'wy': ['wyoming'],
}
other_affil_seen = {}
user_type_list = ['teacher', 'student', 'other']

# Where to start the monthly reporting.
min_month_to_report = '2007-05'
min_download_month  = '2007-06'   # downloads weren't available before this month!

c = {
    ('total', 'month'):    (1, 'Monthly Total'), 
    ('total','cum'):    (2, 'Cum. Total'),
    ('teacher', 'month'):  (3, 'Monthly Teachers'),
    ('teacher','cum'):  (4, 'Cum. Teachers'),
    ('student', 'month'):  (5, 'Monthly Students'),
    ('student','cum'):  (6, 'Cum. Students'),       
    ('other', 'month'):    (7, 'Monthly All Others'), 
    ('other','cum'):    (8, 'Cum. All Others'),
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
    print "Saving %s" % s
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
### Phase 1: monthly totals
    t_month = 0  
    for u in user_type_list:
        this_key = (report, affil, m, u)
        this_number = 0
        if this_key in counts.keys():
            this_number = counts[this_key]
            t_month += this_number
        attempt_cell_fill(ws, row, (u, 'month'), this_number, this_fmt)
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
    if col_key not in c.keys(): 
        print "cannot find %s " % str(col_key)
        return
    write(ws, row, c[col_key][0], this_number, this_fmt)
    
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

    this_date_fmt = fmt['text_bold'] # make first row bold
    this_n_fmt = fmt['int_bold']     # 
    for m in month_rev:
        if m < min_month_to_report: continue
        write(ws, row, 0, m, this_date_fmt) # Month column
        tabulate(ws, counts, report, affil, m, row, this_n_fmt)
        row += 1
        this_date_fmt = fmt['text']     # change to unbolded after first row
        this_n_fmt = fmt['int_regular'] # ditto
    return
    
def do_summary(wb, counts, state, affiliate_list, this_month):
    # This creates the summary sheet.
    # Unfortunately, xlwt doesn't allow you to order the worksheets you create:
    #   they appear in the workbook in the order created.
    # Since we want the Summary page FIRST, we need to know things BEFORE
    # we do the affiliate sheets.   Therefore, there's a bit of reduplication
    # in this method (because I wrote it last).
    #
    # Ideally, all the calculations should be done AHEAD of calling this, and this
    # (and the other reporter functions) should refer to the output of the (unwritten)
    # calculation method.
    ws = wb.add_sheet('Summary')

    # Format the worksheet: set general stuff.
    ws.fit_num_pages = 1
    ws.fit_height_to_pages = 0
    ws.fit_width_to_pages = 1
    ws.paper_size_code = 1 
    ws.portrait = 0   # landscape

    # Put up some banners.
    # There's a mix between the local write() and the worksheet method 
    # because the former doesn't handle merged cells.  However, the LATTER
    # doesn't handle the style dictionary that's created in this program.
    write_merged(ws, 0, 0, 0, 60, '%s TD Metrics: %s' % (state_names[state.lower()], convert_month_to_text(this_month)), fmt['big_bold'])


### AFFILIATE SECTION
    # where to start the summary BY AFFILILATE table
    start_row = 5
    # format for this call is  (top_row, bottom_row, left_column, right_column, text, [style])
    # columns are zero-offset (i.e., A=0, B=1, ... Z=25, AA=26, AB=27,...)
    write_merged(ws, start_row,  start_row, 0, 50, 'Summary for Latest Month:', fmt['text_bold'])
    write_merged(ws, start_row+1, start_row+1, 1, 3, 'Registration', fmt['text_bold'])

    c = 1
    write(ws, start_row+2, c,'This Month', fmt['text_bold'])
    write(ws, start_row+2, c+2, 'Total to Date', fmt['text_bold'])

    row = start_row + 3 # where to start the table - row is the location of the current row   
    aff_total = 0  # create totals for affiliates so as to make the percentage columns
    aff = {}
#    for r in metric_list: aff_total[r] = 0

    #TABLE:
    # Make a list of teacher/student totals for each metric by DEFINED affiliate  (i.e., no 'other')
    for a in affiliate_list:
        if a == 'other': continue  # ignore/skip 'other'
        write(ws, row, 0, a.upper(), fmt['text_bold'])

        t = 0
        for u in user_type_list: # include everyone
            this_key = (state, a, this_month, u)
            if this_key not in counts.keys(): continue # can skip gaps
            this_value = int(counts[this_key])
            t += this_value
        this_key = a
        aff[this_key] = t
        write(ws, row, 1, t, fmt['int_regular'])
        aff_total += t

        row += 1
        
    if len(affiliate_list) > 0: 
        write(ws, row, 0, 'TOTAL', fmt['text_bold'])
        # put in the totals for each metric 
        offset = 1 # column of first metric total
        write(ws, row, offset, aff_total, fmt['int_bold'])

    # OK - do it AGAIN to put in the percentages that were calculated in the previous block:
    row = start_row + 3
    for a in affiliate_list:
        if a == 'other': continue
        offset = 2 # column of first metric percentage

        p = 0.
        if aff_total != 0:
            p = aff[a]/(aff_total + 0.0)
        write(ws, row, offset, p, fmt['percent'])

        row += 1

    # cumulative data --- this is a repeat of the code above
    # (I know, sorry, with the dict changes from counts to cumulate)

    aff = {}
    row = start_row + 3
    aff_total = 0
    for a in affiliate_list:
        if a == 'other': continue  # ignore/skip 'other'
        offset = 3

        t = 0
        for u in user_type_list:
            this_key = (state, a, this_month, u)
            if this_key not in cumulate.keys(): continue # can skip gaps
            this_value = int(cumulate[this_key])
            t += this_value
        this_key = a
        aff[this_key] = t
        write(ws, row, offset, t, fmt['int_regular'])
        aff_total += t
        offset += 4
        row += 1

    # put in the totals for each metric 
    if len(affiliate_list) > 0:
        offset = 3 # column of first metric total
        write(ws, row, offset, aff_total, fmt['int_bold'])
        write(ws, row, offset-1, 1.0, fmt['percent_bold'])
        offset += 4 # skip a column to leave space for the corresponding percentage
        row += 2

### US
    write(ws, row, 0, 'All State', fmt['text_bold'])
    do_summary_line (ws, counts, state, row)
    write(ws, row+1, 0, 'All U.S.', fmt['text_bold'])
    do_summary_line (ws, counts, 'us', row+1)
    write(ws, row+2, 0, 'Worldwide', fmt['text_bold'])
    do_summary_line (ws, counts, 'world', row+2)
    
def do_summary_line(wb, counts, scope, row):
    this_month = max(month_list)
    cols = [1,5,9,13]
    if(scope == 'us'): 
        this_aff = 'us_td'
    elif(scope == 'world'): 
        this_aff = 'world_td'
    else: 
        this_aff = 'all_%s' % scope

    this_col_ref = 0

    month_total = cum_total = 0
    for this_user in user_type_list:
        this_key = (scope, this_aff, this_month, this_user)
        if this_key in counts.keys(): 
            month_total += counts[this_key]
        if this_key in cumulate.keys(): cum_total += cumulate[this_key]
    write(wb, row, cols[this_col_ref], month_total, fmt['int_regular'])
    write(wb, row, cols[this_col_ref]+2, cum_total, fmt['int_regular'])
    this_col_ref += 1

def get_org_data(state):
    rows = [line[:-1] for line in open('DATA/org_all.tsv')]
    orgs = []
    for row in rows:
        fields = row.split('\t')
        if fields[5].lower() != state: continue
        grades = fields[12].split(',')
        grade_text = "%s-%s" % (grades[0], grades[-1])
        fields[12] = grade_text
        orgs.append(tuple(fields))
    return orgs

def do_org_sheet(wb, s):
    orgs = get_org_data(s)
    if len(orgs) < 1:
        print "Did not find orgs - skipping"
        print "# Orgs: %d" % len(orgs)
        return
    ws = wb.add_sheet('Orgs')
    
    write_merged(ws, 0, 0, 0, 20, 'NCES School Metadata for %s' % s.upper(), fmt['text_bold'])
    org_headers = [
        'TD Org ID', 'NCES ID', 'Name', 'Address', 'City', 'State', 'Zip', 'District Code', 'District Name',
        '# Users', 'County', 'Locale', 'Grades', 'Type', 'Enrollment', 'FTE', 'Title 1?', '% Red. Lunch'
    ]
    c = 0
    for head in org_headers: 
        write(ws, 2, c, head, fmt['text_bold'])
        c += 1
    row = 3
    for org in orgs:
        c = 0
        for field in org:
            write(ws, row, c, field, fmt['text'])
            c += 1
        row += 1
    return


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
        if s in ('us', 'world', 'pr','vi','gu'): continue
        print "Starting state %s:" % s
        if s in state_affil_list.keys():
            this_affil_list = state_affil_list[s]
            this_affil_list.append('other')
        else: this_affil_list = []
        
        wb = open_workbook()
        print "\tSummary sheet"
        do_summary(wb, registrations, s, this_affil_list, this_month)
        print "\tOrg Sheet"
        do_org_sheet(wb, s)
        # put in world sheet
        print "\tUS Sheet"
        do_worksheet(wb, registrations, 'us')
        print "\t state %s sheet" % s
        do_worksheet(wb, registrations, 'state', state=s)
        for w in this_affil_list:
            print "\t\tSheet for %s" % w
            do_worksheet(wb, registrations, 'affil', state=s, affil=w)
    
        close_workbook(wb, "reg_%s-%s" % (this_month, s))
