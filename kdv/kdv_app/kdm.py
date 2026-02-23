import zipfile
import os
import tempfile
import msgpack
from dateutil.relativedelta import relativedelta

EQMAP = {
    0: '',

    1: 'P2000',
    2: 'Glock',
    3: 'P250',
    4: 'Deagle',
    5: 'FiveSeven',
    6: 'DualBarettas',
    7: 'Tec9',
    8: 'CZ75',
    9: 'USP',
    10: 'Revolver',

    101: 'MP7',
    102: 'MP9',
    103: 'Bizon',
    104: 'Mac10',
    105: 'UMP',
    106: 'P90',
    107: 'MP5SD',

    201: 'SawedOff',
    202: 'Nova',
    203: 'Mag7',
    204: 'XM1014',
    205: 'M249',
    206: 'Negev',

    301: 'Galil',
    302: 'Famas',
    303: 'AK47',
    304: 'M4A4',
    305: 'M4A1-S',
    306: 'SSG08',
    307: 'SG553',
    308: 'AUG',
    309: 'AWP',
    310: 'Scar20',
    311: 'G3SG1',

    401: 'Zeus',
    402: 'Kevlar',
    403: 'Helmet',
    404: 'Bomb',
    405: 'Knife',
    406: 'DefuseKit',
    407: 'World',

    501: 'Decoy',
    502: 'Molotov',
    503: 'Incendiary',
    504: 'Flash',
    505: 'Smoke',
    506: 'HE'
}

OVERLAY_SCALE_MAP = {
    "de_ancient": 5,
    "de_cache": 5.5,
    "de_dust2": 4.4,
    "de_inferno": 4.9,
    "de_mirage": 5,
    "de_nuke": 7,
    "de_overpass": 5.2,
    "de_train": 4.7,
    "de_vertigo": 4.0,
    "de_anubis": 5.22
}

IS_RAW = False

class KdmObj:

    def __init__(self, path):
        
        self.path = path
        self.original_filename = os.path.basename(path).split('.')[0]
        self.file_dir = os.path.dirname(path)
        self.zf = zipfile.ZipFile(path)
        self.round_traj_entries = {}
        self.round_traj_thum_entries = {}
        self.round_traj_cache = {}
        cache_key = str(abs(hash(os.path.abspath(path))))
        self.traj_cache_dir = os.path.join(tempfile.gettempdir(), "kdv_traj_cache", cache_key)
        kdm_byte = self.zf.read('kdm_header')
        self.Header = msgpack.unpackb(kdm_byte, use_list=False, raw=IS_RAW, unicode_errors='replace')
        kdm_byte = self.zf.read('kdm_matchstats')
        self.MatchStats = msgpack.unpackb(kdm_byte, use_list=False, raw=IS_RAW, unicode_errors='replace')
        self.RoundInfoList = self.MatchStats['RoundInfoList']
        self.rs = None
        
        # count the number of rounds for one-round mode
        roundfile_num = 0
        self.oneround_mode = False
        self.onefile_index = 0
        for item in self.zf.infolist():
            self._index_round_traj_entry(item.filename)
            if item.filename.startswith("kdm_round_"):
                suffix = item.filename[len("kdm_round_"):]
                if suffix.isdigit():
                    roundfile_num += 1
                    self.onefile_index = int(suffix)
        if roundfile_num == 1:
            self.oneround_mode = True

    def _index_round_traj_entry(self, filename):
        if filename.startswith("kdm_traj_round_thum_") and filename.endswith(".png"):
            index_text = filename[len("kdm_traj_round_thum_"):-4]
            if index_text.isdigit():
                self.round_traj_thum_entries[int(index_text)] = filename
            return

        prefixes = ("kdm_traj_round_", "kdm_round_trajectory_")
        for prefix in prefixes:
            if filename.startswith(prefix) and filename.endswith(".png"):
                index_text = filename[len(prefix):-4]
                if index_text.isdigit():
                    self.round_traj_entries[int(index_text)] = filename
                return

    def get_round_trajectory_path(self, index):
        return self._get_round_trajectory_path(index, prefer_thumb=True)

    def get_round_trajectory_full_path(self, index):
        return self._get_round_trajectory_path(index, prefer_thumb=False)

    def _get_round_trajectory_path(self, index, prefer_thumb=True):
        if type(index) != int or index < 0:
            return ""

        entry_name = None
        cache_key = ""
        output_name = ""

        if prefer_thumb:
            entry_name = self.round_traj_thum_entries.get(index)
            cache_key = f"thum:{index}"
            output_name = f"{self.original_filename}_traj_thum_{index}.png"

        if not entry_name:
            entry_name = self.round_traj_entries.get(index)
            cache_key = f"full:{index}"
            output_name = f"{self.original_filename}_traj_{index}.png"
        if not entry_name:
            return ""

        cached = self.round_traj_cache.get(cache_key)
        if cached and os.path.exists(cached):
            return cached

        try:
            os.makedirs(self.traj_cache_dir, exist_ok=True)
            output_path = os.path.join(self.traj_cache_dir, output_name)
            if not os.path.exists(output_path):
                with open(output_path, "wb") as out:
                    out.write(self.zf.read(entry_name))
            self.round_traj_cache[cache_key] = output_path
            return output_path
        except (KeyError, OSError, zipfile.BadZipFile):
            return ""

    def extract(self, index, filename):
        new_filename = None
        if filename == '':
            new_filename = self.original_filename + '_Round_' + str(index+1) + '.kdz'
        else:
            new_filename = filename + '.kdz'

        zout = zipfile.ZipFile(os.path.join(self.file_dir, new_filename), "w")
        for item in self.zf.infolist():
            buffer = self.zf.read(item.filename)
            if item.filename == 'kdm_header':
                zout.writestr(item, buffer)
            elif item.filename == 'kdm_matchstats':
                zout.writestr(item, buffer)
            elif item.filename[:10] == 'kdm_round_' and int(item.filename[10:]) == index:
                zout.writestr(item, buffer)
            elif item.filename[:4] == 'acm_' and int(item.filename.split('_')[1].split('-')[0]) == index:
                zout.writestr(item, buffer)
        self.zf.close()
        zout.close()
        self.zf = zipfile.ZipFile(self.path)

    def load_roundsnapshots(self, index):
        if type(index) != int:
            print("Index must be integer!")
            return
        if index < 0 or self.Header['RoundLength'] <= index:
            print("Index Range 0-" + str(self.Header['RoundLength']-1))
            return

        kdm_byte = self.zf.read('kdm_round_' + str(index))

        self.rs = msgpack.unpackb(kdm_byte, use_list=False, raw=IS_RAW, unicode_errors='replace')
        self.rs_len = len(self.rs['PlayerDrawingSnapShots'])
        self.rs_tick_list = self.rs['TickList']

        self.rs_pdss = self.rs['PlayerDrawingSnapShots']
        self.rs_bss = self.rs['BombSnapShots']
        self.rs_nss = self.rs['NadesSnapShots']
        self.rs_ness =self.rs['NadeEffectSnapShots']

        self.rs_pslot = self.rs['PlayerSlot']
        self.rs_pname = self.rs['PlayerNames']

        self.rs_ndim = self.rs['NadesDrawingInfoMap']
        self.rs_nem = self.rs['NadeEffectMap']

    def print_focused_round(self):
        out = ""

        out += "RoundNumber:{0}\n".format(self.rs['RoundNumber'])
        out += "RoundStartTick:{0}\n".format(self.rs['RoundStartTick'])


        out += "PlayerSlot:{0}\n".format(self.rs['PlayerSlot'])
        out += "PlayerNames:{0}\n".format(self.rs['PlayerNames'])

        out += "PlayerDrawingSnapShotsLength:{0}\n".format(len(self.rs['PlayerDrawingSnapShots']))
        out += "BombSnapShots:{0}\n".format(len(self.rs['BombSnapShots']))
        out += "NadesSnapShotsLength:{0}\n".format(len(self.rs['NadesSnapShots']))
        out += "NadeEffectSnapShotsLength:{0}\n".format(len(self.rs['NadeEffectSnapShots']))

        out += "NadesDrawingInfoMapKeyNumber:{0}\n".format(len(self.rs['NadesDrawingInfoMap']))
        out += "NadeEffectMapKeyNumber:{0}\n".format(len(self.rs['NadeEffectMap']))

        print(out)

    def get_mapname(self):
        return self.Header['MapName']

    def get_mapscale(self):
        return OVERLAY_SCALE_MAP[self.Header['MapName']]

    def print_ss(self, index):
        if type(index) != int:
            print("Index must be integer!")
            return
        if self.rs is None:
            print("Load RoundSnapShot first!")
            return
        if index < 0 or self.rs_len <= index:
            print("Index Range 0-" + str(self.rs_len-1))
            return  

        out = ""
        e_tick = index * self.Header['TickPerSS'] + self.rs['RoundStartTick']
        out += "Round ({0}) // SSIndex ({1}) // Estimated Tick {2} \n".format(self.rs['RoundNumber'], index , round(e_tick))
        out += "Time:" +  self.get_current_time(index) + "\n"

        # Dumping Playrs Info 
        out += "1) PlayerDrawingSnapShots\n"
        for i in range(len(self.rs_pslot)):
            out += "({})\n".format(self.rs_pname[i])
            active = self.rs_pdss[index]['PlayerDrawingInfo'][i]['ActiveEquipment']
            out += "ActiveEuipment[{0}]\n".format(EQMAP[active])
            out += "[{}]\n".format(self.rs_pdss[index]['PlayerDrawingInfo'][i])
        # Dumping C4 Info
        out += "2) BombSnapShots\n"
        out += "[{}]\n".format(self.rs_bss[index])
        # Grenade Entity Info
        out += "3) NadesSnapShots\n"
        if self.rs_nss[index] is not None:
            for i in self.rs_nss[index]:
                nade = self.rs_ndim[i]
                out += "NadeID [{0}] NadeType:{1}\n".format(i, EQMAP[nade['NadeType']])
                out += "Thrower:{0} StartTick:{1}\n".format(nade['ThrowerName'], nade['StartTick'])
                out += "ThrowPos:{0} ThrowAngX:{1} ThrowAngY:{2}\n".format(nade['ThrowPos'], nade['ThrowAngX'], nade['ThrowAngY'])
                #out += "StartSnapShotIndex:{0} DetonatedSSIndex:{1}\n".format(nade['StartSnapShotIndex'], nade['DetonatedSSIndex'])
                rindex = index-nade['StartSnapShotIndex']
                out += "PointsList:{}\n".format(nade['NadePointsList'][rindex])
        # Grenade Effects Info
        out += "4) NadeEffectSnapShots\n"
        if self.rs_ness[index] is not None:
            for i in self.rs_ness[index]:
                neffect = self.rs_nem[i]
                out += "NadeEffect:{}\n".format(neffect)
                out += "NadeType:{}\n".format(EQMAP[neffect['NadeType']])
        
        print(out)

    def get_current_time(self, index):
        if self.rs is None:
            print("Load RoundSnapShot first!")
            return "0"
        if index < 0 or self.rs_len <= index:
            print("get_current_time out of index!")
            return "0"
        if self.rs['BombPlantedSSIndex'] == 0:
            now_sec = 116 - (self.rs_tick_list[index] - self.rs['RoundStartTick'])/round(self.Header['TickRate'])
            time = relativedelta(seconds=now_sec).normalized()
            res = "{0.minutes:01}:{0.seconds:02}.{1}".format(time, str(time.microseconds)[0])  
        else:
            if index < self.rs['BombPlantedSSIndex']:
                now_sec = 116 - (self.rs_tick_list[index] - self.rs['RoundStartTick'])/round(self.Header['TickRate'])
                time = relativedelta(seconds=now_sec).normalized()
                res = "{0.minutes:01}:{0.seconds:02}.{1}".format(time, str(time.microseconds)[0])
            else:
                if self.rs['BombDetonatedSSIndex'] != 0 and self.rs['BombDetonatedSSIndex'] <= index:
                    return "Bomb Det." 
                if self.rs['BombDefusedSSIndex'] != 0 and self.rs['BombDefusedSSIndex'] <= index:
                    return "Bomb Def."

                bomb_time_until_det = 40 - (self.rs_tick_list[index] - self.rs['BombPlantedTick']) / round(self.Header['TickRate'])
                if bomb_time_until_det < 0:
                    bomb_time_until_det = 0
                time = relativedelta(seconds=bomb_time_until_det).normalized()
                res = "Bomb {0.seconds:01}.{1}".format(time, str(time.microseconds)[:1])
        return res

    def tick_to_SS(self, tick):
        if self.rs is None:
            print("Load RoundSnapShot first!")
            return
        return round((tick-self.rs['RoundStartTick'])/self.Header['TickPerSS'])


if __name__ == '__main__':
    pass
