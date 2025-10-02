import pandas as pd
import os
import subprocess
import csv
import re
import textwrap
from pathlib import Path

# -------------------------
# Helpers for cross-platform paths
# -------------------------

def slugify(s: str, max_len: int = 255) -> str:
    """Make a safe string for filenames."""
    if s is None:
        return ""
    s = str(s).strip().replace(" ", "_")
    s = re.sub(r"[^A-Za-z0-9._-]", "", s)
    return s[:max_len]

def get_ips_base_dir() -> Path:
    """
    Determine writable base dir for results.
    Order:
      1. env var IPS_BASE_DIR
      2. $XDG_DATA_HOME/ips
      3. ~/.local/share/ips
    """
    env = os.getenv("IPS_BASE_DIR")
    if env:
        return Path(env).expanduser()

    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "ips"

    return Path.home() / ".local" / "share" / "ips"

def prepare_paths(country_file_path: str, entry_number_country, country_name: str, owner_name: str):
    """Return dict of safe paths for iplist, scan, and filtered results."""
    base = get_ips_base_dir()
    ip_dir = base / "iplists"
    results_dir = base / "results" / slugify(country_name)

    ip_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    list_name = f"{Path(country_file_path).stem}_{entry_number_country}"
    safe_owner = slugify(owner_name)

    filename = ip_dir / f"{list_name}_iplist.txt"
    output_filename = ip_dir / f"{list_name}_scan.txt"
    filtered_output_filename = results_dir / f"{list_name}_{safe_owner}.txt"

    return {
        "list_name": list_name,
        "filename": str(filename),
        "output_filename": str(output_filename),
        "filtered_output_filename": str(filtered_output_filename),
    }

# -------------------------
# Existing functions
# -------------------------

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_to_file(ip_list, filename):
    with open(filename, 'w') as file:
        for ip in ip_list:
            file.write(f"{ip}\n")

def ip_range(start_ip, end_ip):
    start = list(map(int, start_ip.split('.')))
    end = list(map(int, end_ip.split('.')))
    total_ips = 1
    for i in range(4):
        total_ips *= (end[i] - start[i] + 1)

    ips = []
    for _ in range(total_ips):
        ip = '.'.join(map(str, start))
        ips.append(ip)
        start[3] += 1
        for i in range(3, 0, -1):
            if start[i] > end[i]:
                start[i] = 0
                start[i - 1] += 1
    return ips

def filter_open_ports(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            host_match = re.match(r'Host: ([\d\.]+) \((.*?)\)\s+Ports: (.*)', line)
            if host_match:
                ip = host_match.group(1)
                host_name = host_match.group(2)
                ports_info = host_match.group(3)
                open_ports = []
                ports = ports_info.split(', ')
                for port in ports:
                    port_info = port.split('/')
                    if port_info[1] == 'open':
                        open_ports.append(f"{port_info[0]}/open")
                if open_ports:
                    open_ports_str = ', '.join(open_ports)
                    outfile.write(f"{ip} ({host_name}) {open_ports_str}\n")

def display_all_countries():
    countries_file = 'countries.csv'
    df = pd.read_csv(countries_file, header=None)
    df.insert(0, 'Entry Number', df.index)
    column_width = 30
    num_columns = 5
    num_rows = -(-len(df) // num_columns)

    lines = []
    for row in range(num_rows):
        line_parts = []
        for col in range(num_columns):
            index = row + col * num_rows
            if index < len(df):
                entry_number = df.iloc[index, 0]
                country_name = df.iloc[index, 1]
                line_parts.append(f"{entry_number:3d}: {country_name.ljust(column_width)}")
            else:
                line_parts.append(" " * column_width)
        lines.append("".join(line_parts))

    print("\nCountries:")
    for line in lines:
        print(line)

# -------------------------
# Country mapping
# -------------------------
country_names = {
    # Add all mappings here
    0: 'countries/af.csv',  # Afghanistan
    1: 'countries/ax.csv',  # Aland Islands
    2: 'countries/al.csv',  # Albania
    3: 'countries/dz.csv',  # Algeria
    4: 'countries/as.csv',  # American Samoa
    5: 'countries/ad.csv',  # Andorra
    6: 'countries/ao.csv',  # Angola
    7: 'countries/ag.csv',  # Antigua and Barbuda
    8: 'countries/ar.csv',  # Argentina
    9: 'countries/am.csv',  # Armenia
    10: 'countries/aw.csv',  # Aruba
    11: 'countries/au.csv',  # Australia
    12: 'countries/at.csv',  # Austria
    13: 'countries/az.csv',  # Azerbaijan
    14: 'countries/bs.csv',  # Bahamas
    15: 'countries/bh.csv',  # Bahrain
    16: 'countries/bd.csv',  # Bangladesh
    17: 'countries/bb.csv',  # Barbados
    18: 'countries/by.csv',  # Belarus
    19: 'countries/be.csv',  # Belgium
    20: 'countries/bz.csv',  # Belize
    21: 'countries/bj.csv',  # Benin
    22: 'countries/bm.csv',  # Bermuda
    23: 'countries/bt.csv',  # Bhutan
    24: 'countries/bo.csv',  # Bolivia
    25: 'countries/ba.csv',  # Bosnia and Herzegovina
    26: 'countries/bw.csv',  # Botswana
    27: 'countries/br.csv',  # Brazil
    28: 'countries/bn.csv',  # Brunei Darussalam
    29: 'countries/bg.csv',  # Bulgaria
    30: 'countries/bf.csv',  # Burkina Faso
    31: 'countries/bu.csv',  # Burundi
    32: 'countries/kh.csv',  # Cambodia
    33: 'countries/cm.csv',  # Cameroon
    34: 'countries/ca.csv',  # Canada
    35: 'countries/cv.csv',  # Cape Verde
    36: 'countries/ky.csv',  # Cayman Islands
    37: 'countries/ch.csv',  # Chad
    38: 'countries/cl.csv',  # Chile
    39: 'countries/cn.csv',  # China
    40: 'countries/co.csv',  # Colombia
    41: 'countries/km.csv',  # Comoros
    42: 'countries/cg.csv',  # Congo
    43: 'countries/cd.csv',  # Congo, The Democratic Republic Of The
    44: 'countries/ck.csv',  # Cook Islands
    45: 'countries/cr.csv',  # Costa Rica
    46: 'countries/hr.csv',  # Croatia
    47: 'countries/cu.csv',  # Cuba
    48: 'countries/cy.csv',  # Cyprus
    49: 'countries/cz.csv',  # Czech Republic
    50: 'countries/ci.csv',  # Côte D'ivoire
    51: 'countries/dk.csv',  # Denmark
    52: 'countries/dj.csv',  # Djibouti
    53: 'countries/dm.csv',  # Dominica
    54: 'countries/do.csv',  # Dominican Republic
    55: 'countries/ec.csv',  # Ecuador
    56: 'countries/eg.csv',  # Egypt
    57: 'countries/sv.csv',  # El Salvador
    58: 'countries/gq.csv',  # Equatorial Guinea
    59: 'countries/er.csv',  # Eritrea
    60: 'countries/ee.csv',  # Estonia
    61: 'countries/et.csv',  # Ethiopia
    62: 'countries/fo.csv',  # Faroe Islands
    63: 'countries/fj.csv',  # Fiji
    64: 'countries/fi.csv',  # Finland
    65: 'countries/fr.csv',  # France
    66: 'countries/gf.csv',  # French Guiana
    67: 'countries/pf.csv',  # French Polynesia
    68: 'countries/gp.csv',  # Gabon
    69: 'countries/gm.csv',  # Gambia
    70: 'countries/ge.csv',  # Georgia
    71: 'countries/de.csv',  # Germany
    72: 'countries/gh.csv',  # Ghana
    73: 'countries/gi.csv',  # Gibraltar
    74: 'countries/gr.csv',  # Greece
    75: 'countries/gl.csv',  # Greenland
    76: 'countries/gp.csv',  # Guadeloupe
    77: 'countries/gu.csv',  # Guam
    78: 'countries/gt.csv',  # Guatemala
    79: 'countries/gg.csv',  # Guernsey
    80: 'countries/gn.csv',  # Guinea
    81: 'countries/gw.csv',  # Guinea-Bissau
    82: 'countries/gy.csv',  # Guyana
    83: 'countries/ht.csv',  # Haiti
    84: 'countries/va.csv',  # Holy See (Vatican City)
    85: 'countries/hn.csv',  # Honduras
    86: 'countries/hk.csv',  # Hong Kong
    87: 'countries/hu.csv',  # Hungary
    88: 'countries/is.csv',  # Iceland
    89: 'countries/in.csv',  # India
    90: 'countries/id.csv',  # Indonesia
    91: 'countries/ir.csv',  # Iran
    92: 'countries/iq.csv',  # Iraq
    93: 'countries/ie.csv',  # Ireland
    94: 'countries/im.csv',  # Isle of Man
    95: 'countries/il.csv',  # Israel
    96: 'countries/it.csv',  # Italy
    97: 'countries/jm.csv',  # Jamaica
    98: 'countries/jp.csv',  # Japan
    99: 'countries/je.csv',  # Jersey
    100: 'countries/jo.csv',  # Jordan
    101: 'countries/kz.csv',  # Kazakhstan
    102: 'countries/ke.csv',  # Kenya
    103: 'countries/kw.csv',  # Kuwait
    104: 'countries/kg.csv',  # Kyrgyzstan
    105: 'countries/la.csv',  # Lao People's Democratic Republic
    106: 'countries/lv.csv',  # Latvia
    107: 'countries/lb.csv',  # Lebanon
    108: 'countries/ls.csv',  # Lesotho
    109: 'countries/lr.csv',  # Liberia
    110: 'countries/ly.csv',  # Libyan Arab Jamahiriya
    111: 'countries/li.csv',  # Liechtenstein
    112: 'countries/lt.csv',  # Lithuania
    113: 'countries/lu.csv',  # Luxembourg
    114: 'countries/mo.csv',  # Macao
    115: 'countries/mk.csv',  # Macedonia
    116: 'countries/mg.csv',  # Madagascar
    117: 'countries/mw.csv',  # Malawi
    118: 'countries/my.csv',  # Malaysia
    119: 'countries/mv.csv',  # Maldives
    120: 'countries/ml.csv',  # Mali
    121: 'countries/mt.csv',  # Malta
    122: 'countries/mq.csv',  # Martinique
    123: 'countries/mr.csv',  # Mauritania
    124: 'countries/mu.csv',  # Mauritius
    125: 'countries/mx.csv',  # Mexico
    126: 'countries/fm.csv',  # Micronesia, Federated States Of
    127: 'countries/md.csv',  # Moldova
    128: 'countries/mc.csv',  # Monaco
    129: 'countries/mn.csv',  # Mongolia
    130: 'countries/me.csv',  # Montenegro
    131: 'countries/ma.csv',  # Morocco
    132: 'countries/mz.csv',  # Mozambique
    133: 'countries/mm.csv',  # Myanmar
    134: 'countries/na.csv',  # Namibia
    135: 'countries/nr.csv',  # Nauru
    136: 'countries/np.csv',  # Nepal
    137: 'countries/nl.csv',  # Netherlands
    138: 'countries/nc.csv',  # New Caledonia
    139: 'countries/nz.csv',  # New Zealand
    140: 'countries/ni.csv',  # Nicaragua
    141: 'countries/ne.csv',  # Niger
    142: 'countries/ng.csv',  # Nigeria
    143: 'countries/mp.csv',  # Northern Mariana Islands
    144: 'countries/no.csv',  # Norway
    145: 'countries/om.csv',  # Oman
    146: 'countries/pk.csv',  # Pakistan
    147: 'countries/pw.csv',  # Palau
    148: 'countries/ps.csv',  # Palestinian Territory
    149: 'countries/pa.csv',  # Panama
    150: 'countries/pg.csv',  # Papua New Guinea
    151: 'countries/py.csv',  # Paraguay
    152: 'countries/pe.csv',  # Peru
    153: 'countries/ph.csv',  # Philippines
    154: 'countries/pl.csv',  # Poland
    155: 'countries/pt.csv',  # Portugal
    156: 'countries/pr.csv',  # Puerto Rico
    157: 'countries/qa.csv',  # Qatar
    158: 'countries/re.csv',  # Reunion
    159: 'countries/ro.csv',  # Romania
    160: 'countries/ru.csv',  # Russian Federation
    161: 'countries/rw.csv',  # Rwanda
    162: 'countries/kn.csv',  # Saint Kitts and Nevis
    163: 'countries/lc.csv',  # Saint Lucia
    164: 'countries/bl.csv',  # Saint Pierre and Miquelon
    165: 'countries/ws.csv',  # Samoa
    166: 'countries/sm.csv',  # San Marino
    167: 'countries/st.csv',  # Sao Tome and Principe
    168: 'countries/sa.csv',  # Saudi Arabia
    169: 'countries/sn.csv',  # Senegal
    170: 'countries/rs.csv',  # Serbia
    171: 'countries/sc.csv',  # Seychelles
    172: 'countries/sl.csv',  # Sierra Leone
    173: 'countries/sg.csv',  # Singapore
    174: 'countries/sk.csv',  # Slovakia
    175: 'countries/si.csv',  # Slovenia
    176: 'countries/sb.csv',  # Solomon Islands
    177: 'countries/so.csv',  # Somalia
    178: 'countries/za.csv',  # South Africa
    179: 'countries/kr.csv',  # South Korea
    180: 'countries/es.csv',  # Spain
    181: 'countries/lk.csv',  # Sri Lanka
    182: 'countries/sd.csv',  # Sudan
    183: 'countries/sr.csv',  # Suriname
    184: 'countries/sz.csv',  # Swaziland
    185: 'countries/se.csv',  # Sweden
    186: 'countries/ch.csv',  # Switzerland
    187: 'countries/sy.csv',  # Syrian Arab Republic
    188: 'countries/tw.csv',  # Taiwan
    189: 'countries/tj.csv',  # Tajikistan
    190: 'countries/tz.csv',  # Tanzania
    191: 'countries/th.csv',  # Thailand
    192: 'countries/tl.csv',  # Timor-Leste
    193: 'countries/tg.csv',  # Togo
    194: 'countries/tt.csv',  # Trinidad and Tobago
    195: 'countries/tn.csv',  # Tunisia
    196: 'countries/tr.csv',  # Turkey
    197: 'countries/tm.csv',  # Turkmenistan
    198: 'countries/tc.csv',  # Turks and Caicos Islands
    199: 'countries/tv.csv',  # Tuvalu
    200: 'countries/ug.csv',  # Uganda
    201: 'countries/ua.csv',  # Ukraine
    202: 'countries/ae.csv',  # United Arab Emirates
    203: 'countries/gb.csv',  # United Kingdom
    204: 'countries/us.csv',  # United States
    205: 'countries/uy.csv',  # Uruguay
    206: 'countries/uz.csv',  # Uzbekistan
    207: 'countries/vu.csv',  # Vanuatu
    208: 'countries/ve.csv',  # Venezuela
    209: 'countries/vn.csv',  # Viet Nam
    210: 'countries/vg.csv',  # Virgin Islands, British
    211: 'countries/vi.csv',  # Virgin Islands, U.S.
    212: 'countries/ye.csv',  # Yemen
    213: 'countries/zm.csv'  # Zambia
}


# -------------------------
# Main logic
# -------------------------
clear_screen()
csv_file_path = 'countries.csv'
df = pd.read_csv(csv_file_path, header=None)
df.insert(0, 'Entry Number', df.index)

display_all_countries()
print("\n")

while True:
    try:
        entry_number = int(input("Type an entry number: "))
        if 0 <= entry_number < len(df):
            clear_screen()
            selected_entry = df[df['Entry Number'] == entry_number]
            print("Selected Entry:")
            print(selected_entry.to_string(index=False))

            country_file_path = country_names.get(entry_number)
            if country_file_path:
                country_name = os.path.basename(country_file_path).split('.')[0]
                country_df = pd.read_csv(country_file_path)
                country_df.columns = ["From IP", "To IP", "Total IP's", "Assign Date", "Owner"]
                country_df.insert(0, 'Entry Number', country_df.index)
                pd.set_option('display.max_rows', None)

                print("\nCountry Data:")
                print(country_df.to_string(index=False))
                print()

                while True:
                    try:
                        entry_number_country = int(input("Type an entry number to start the scan: "))
                        if 0 <= entry_number_country < len(country_df):
                            selected_country_entry = country_df[country_df['Entry Number'] == entry_number_country]
                            if not selected_country_entry.empty:
                                start_ip = selected_country_entry['From IP'].values[0]
                                end_ip = selected_country_entry['To IP'].values[0]
                                owner_name = selected_country_entry['Owner'].values[0]

                                ip_list = ip_range(start_ip, end_ip)

                                paths = prepare_paths(country_file_path, entry_number_country, country_name, owner_name)
                                filename = paths["filename"]
                                output_filename = paths["output_filename"]
                                filtered_output_filename = paths["filtered_output_filename"]

                                save_to_file(ip_list, filename)

                                clear_screen()
                                ports = input("Enter the ports to scan (comma-separated ex: 80,443,21...): ")
                                clear_screen()
                                command = f"nmap -sS -p {ports} -iL {filename} -oG {output_filename} -v"
                                print(selected_country_entry)
                                print("Command: ", command)
                                print()
                                subprocess.run(command, shell=True, check=True)

                                filter_open_ports(output_filename, filtered_output_filename)

                                os.remove(filename)
                                os.remove(output_filename)

                                clear_screen()
                                print()
                                print(f"Scan successful. Results saved to '{filtered_output_filename}'")
                                print()
                                display_all_countries()
                                subprocess.run(["xdg-open", filtered_output_filename])

                            break
                        else:
                            print(f"Please enter a number between 0 and {len(country_df) - 1}.")
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                print("No country file found for this entry.")
        else:
            print(f"Please enter a number between 0 and {len(df) - 1}.")
    except ValueError:
        print("Please enter a valid number.")
