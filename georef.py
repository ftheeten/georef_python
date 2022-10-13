from tkinter import filedialog
import pandas as pd
import chardet
import sys, getopt
import requests

url_nominatim="https://nominatim.openstreetmap.org/reverse?format=json"

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def fill_df(df, osm_json, col_name, idx):
    if col_name in osm_json:
        df.at[idx, col_name]=osm_json[col_name]
        
def launch(argv):
    file_path_string = filedialog.askopenfilename()
    rawdata = open(file_path_string, 'rb').read()
    t_encoding=chardet.detect(rawdata )
    print(t_encoding)
    opts, args = getopt.getopt(argv,None,["lat=","long="])
    latcol=None
    longcol=None
    for opt, arg in opts:
        if opt == '--lat':
            latcol=arg
        elif opt == '--long':
            longcol=arg
    if latcol is not None and longcol is not None:
        print(latcol)
        print(longcol)
        df=pd.read_csv(file_path_string, sep='\t', lineterminator='\r', encoding=t_encoding['encoding'])
        df["country_code"]=""
        df["country"]=""
        df["state"]=""
        df["state_district"]=""
        df["state"]=""
        df["city"]=""
        df["town"]=""
        df["display_name"]=""
        df["osm_id"]=""
        df["place_id"]=""
        df["osm_type"]=""
        df["osm_url"]=""
        df[longcol]=df[longcol].astype(str)
        df[latcol]=df[latcol].astype(str)
        for i, row in df.iterrows():
            print(i)
            long=row[longcol]
            lat=row[latcol]
            print(long)
            print(lat)
            if(is_number(lat) and is_number(long) and lat !="nan" and long !="nan"):
                row_url=url_nominatim+"&lat="+lat.strip()+"&lon="+long.strip()
                print(row_url)
                response = requests.get(row_url.strip(), headers={"Accept-Language": "en-US,en;q=0.5"})
                print(response.json())
                osm_json=response.json()
                fill_df(df, osm_json, "osm_id", i)
                fill_df(df, osm_json, "place_id", i)
                fill_df(df, osm_json, "osm_type", i)
                if "address" in osm_json:
                    fill_df(df, osm_json["address"], "country_code",i)
                    fill_df(df, osm_json["address"], "country", i)
                    fill_df(df, osm_json["address"], "state", i)
                    fill_df(df, osm_json["address"], "state_district", i)
                    fill_df(df, osm_json["address"], "city", i)
                    fill_df(df, osm_json["address"], "town", i)
                fill_df(df, osm_json, "display_name", i)
                df.at[i, "osm_url"]= row_url.strip()
                print("done")
                
            else:
               print("no coord")
        filename_array=file_path_string.split(".")
        filename_array[len(filename_array)-2]=filename_array[len(filename_array)-2]+"_osm_check"
        df.to_csv( ".".join(filename_array),sep="\t")
               
    else:
        print("provide --lat and --long col")

if __name__ == "__main__":
    launch(sys.argv[1:])


