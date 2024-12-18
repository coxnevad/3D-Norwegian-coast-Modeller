
import aiohttp
import asyncio
import json
from enum import Enum
import datetime


link = ("https://ws.geonorge.no/transformering/v1/transformer?x={E}&y={N}&fra={FromCord}&til={ToCord}")


link2 = ("https://vannstand.kartverket.no/tideapi.php?"
         "lat={lat}&lon={long}"
         "&fromtime={Date}T{time}:{min}&totime={Date}T{time2}:{min}"
         "&datatype=obs"
         "&refcode={ref}"
         "&place=test&file="
         "&lang=nn"
         "&interval=10&dst=0&tzone=1&tide_request=locationdata")

class altitudeRefSys(Enum):
    NN2000 = "nn2000"
    CHARTDATUM = "cd"
    MIDDLESEALEVEL = "msl"


class cordinateRefsys(Enum):
    EU89UTM31="25831"
    EU89UTM32="25832"
    EU89UTM33="25833"
    EU89UTM34="25834"
    LongLat="4230"





async def cord_tansform(North, East, FromC=cordinateRefsys.EU89UTM32.value, toC=cordinateRefsys.LongLat.value ):

    async with aiohttp.ClientSession() as session:
        url = link.format(E=East, N = North, FromCord = FromC, ToCord = toC)
        async with session.get(url) as r:
            content = await r.content.read()
            content = json.loads(content.decode('utf-8')).values()
            return list(content)
        
async def get_WaterLevel(lat, long, time, date,min):
    async with aiohttp.ClientSession() as session:
        print(lat)
        print(long)
        url = link2.format(lat = lat, long = long, ref = altitudeRefSys.NN2000.value, time = time,min = min, Date =date, time2 = '{0:0>2}'.format(int(time)+2))
        print(url)
        async with session.get(url) as r:
            xml = await r.content.read()
            return float(xml.decode().split("\n")[5].split('"')[1])/100
        
        
def getSeaLevel(position, date):
    
    long,lat = asyncio.run(cord_tansform(North =position[1], East=position[0]))
    dato = date.strftime('20%y-%m-%d')
    print(dato)

    return asyncio.run(get_WaterLevel(long=long, lat= lat,date=dato, time='{0:0>2}'.format(date.hour), min = '{0:0>2}'.format(date.minute)))

if __name__ == "__main__":

    maxOest =  598197.48#	569521.76
    minOest = 597810.39#569475.25
    maxNord = 6642472.99#7034758.74
    minNord = 6642154.83#7034679.45
    oceanPoint = ((maxOest+minOest)/2,(maxNord+minNord)/2)
    
    hour = 10
    min = 30
    date = "2024-11-20"
    date = datetime.datetime(year = 2024, month=11, day = 20,hour= 8, minute=30)
    print(getSeaLevel(oceanPoint,date))
