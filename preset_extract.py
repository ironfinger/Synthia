import gzip
import os
from xml.etree.ElementTree import tostring
import xml.etree.cElementTree as ET
import numpy as np
import xmltodict
import json
from xml.dom import minidom

""" 
We need to first unzip.
Then we need to try and figure out a way of looping through all the files.
Then we need to try and parse into json.
Then try send the data in an api.
"""

class PresetManager:
    def __init__(self, pr_categories, unzip_all=False) -> None:
        self.preset_path = os.path.join("Presets") # The path whre preset information is stored.
        self.analog_path = os.path.join(self.preset_path, "Analog") # Where the analog presets from ableton are stored.
        self.jsonn_path = os.path.join(self.preset_path, "JSON")
        self.categories = pr_categories # The categories from ableton analog.
        self.presets = []
        self.new_preseet_path = os.path.join("NewPresets") # The path to the new presets.



    def getPresets(self):
        preset_list = [] # Create a list for the presets.

        # Loop through the categories:
        for category in self.categories:

            # Get the presets in the category folder:
            category_presets = os.listdir(os.path.join(self.analog_path, category))

            # Get the path for the category:
            category_path = os.path.join(self.analog_path, category)

            # Loop through the presets:
            for preset in category_presets:

                # Create a new preset object:
                new_preset = Preset(
                    preset,
                    category_path,
                    category
                )

                # Append preset to presed list:
                preset_list.append(new_preset)

        # Convert this to a numpy array:
        preset_np = np.array(preset_list)

        # Add this to the object.
        self.presets = preset_np
        return preset_np # Return the numpy array.


    def get_presets_via_json(self):

        preset_list = [] # Create a list for the presets"

        for category in self.categories:
            
            # Get the path for the category:
            category_path = os.path.join(self.jsonn_path, category)

            # Get the presets in the category folder:
            category_presets = os.listdir(category_path)

            for preset in category_presets:
                # Create a new preset object:
                new_preset = Preset(
                    preset,
                    category_path,
                    category
                )

                # Append preset to the list.
                preset_list.append(new_preset)
        
        # Convert this to a numpy array:
        preset_np = np.array(preset_list)

        self.presets = preset_np
        return preset_np
            


    def get_preset_data(self):
        """
        This is to return a bunch of json to the dojo to see the different files.
        """

        presets = []

        # Get the json paths
        for category in self.categories:
            category_path = os.path.join(self.jsonn_path, category)
            category_presets = os.listdir(category_path)

            for preset in category_presets:

                values = []
                name = ""

                with open(os.path.join(category_path, preset)) as json_file:
                    data = json.load(json_file)
                    print("---------------------------------")
                    print(os.path.join(category_path, preset))
    
                    # Name
                    if len(data["Ableton"]["UltraAnalog"]["UserName"]["@Value"]) > 0:
                        name = data["Ableton"]["UltraAnalog"]["UserName"]["@Value"]
                    else:
                        name = preset[:-5]

                    """
                    Values for the parts that dont relate to the signal chain.
                    """
                    # One value
                    values.append(data["Ableton"]["UltraAnalog"]["Volume"]["Manual"]["@Value"]) # 0

                    """
                    Signal Chain 01
                    """
                    # Oscillator Toggle [1]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain1"]["OscillatorToggle"]["Manual"]["@Value"])
                    
                    # Oscillator Waveshape [2]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain1"]["OscillatorWaveShape"]["Manual"]["@Value"]) 

                    # Oscillator Oct [3]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain1"]["OscillatorOct"]["Manual"]["@Value"]) 

                    # Oscillator Semitone [4]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain1"]["OscillatorSemi"]["Manual"]["@Value"]) 

                    # Oscillator ENV Time [5]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain1"]["OscillatorEnvTime"]["Manual"]["@Value"]) 

                    """
                    Signal Chain 02
                    """
                    # Oscillator Toggle [6]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain2"]["OscillatorToggle"]["Manual"]["@Value"])
                    
                    # Oscillator Waveshape [7]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain2"]["OscillatorWaveShape"]["Manual"]["@Value"]) 

                    # Oscillator Oct [8]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain2"]["OscillatorOct"]["Manual"]["@Value"]) 

                    # Oscillator Semitone [9]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain2"]["OscillatorSemi"]["Manual"]["@Value"]) 

                    # Oscillator ENV Time [10]:
                    values.append(data["Ableton"]["UltraAnalog"]["SignalChain2"]["OscillatorEnvTime"]["Manual"]["@Value"]) 

                    new_preset = PresetV2(name, values)
                    presets.append(new_preset)
        
        return presets



    def format_preset_data_for_api(self, presets):
        preset_json_list = []
        for preset in presets:
            preset_json_list.append({ 'name': preset.name, 'volume': preset.volume})

        return preset_json_list

    def unzip(self, path, export_path):   
        export_with_category = os.path.join(export_path, "Bass")

        with gzip.open(path, 'r') as f:
            raw_xml = f.read()

            xml = ET.fromstring(raw_xml)
            tree = ET.ElementTree(xml)
            tree.write(os.path.join(export_with_category, "hello.xml"), encoding="utf-8")



    def unzip_category(self, presets, category_index):
        category_path = os.path.join(self.analog_path, self.categories[category_index])
        xml_path = os.path.join(self.preset_path, "XML")
        export_path = os.path.join(xml_path, "Bass")
        category_presets = os.listdir(category_path)

        for preset in category_presets:
            with gzip.open(os.path.join(category_path, preset), 'r') as file:
                
                preset_name = preset[:-3] + "xml"

                raw_xml = file.read()
                xml = ET.fromstring(raw_xml)
                tree = ET.ElementTree(xml)
                tree.write(os.path.join(export_path, preset_name), encoding="utf-8")

        print("Done")



    def covert_xml_category_to_json(self, category_index):
        # Create XML paths:
        xml_path = os.path.join(self.preset_path, "XML")
        xml_category_path = os.path.join(xml_path, self.categories[category_index])

        # Create JSON paths:
        json_path = os.path.join(self.preset_path, "JSON")
        json_category_path = os.path.join(json_path, self.categories[category_index])

        xml_category_presets = os.listdir(xml_category_path)

        for preset in xml_category_presets:

            xml_doc_path = os.path.join(xml_category_path, preset)
            xml_tree = ET.parse(xml_doc_path)

            root = xml_tree.getroot()

            to_string = ET.tostring(root, encoding='utf-8', method='xml')

            xml_to_dict = xmltodict.parse(to_string)

            json_name = preset[:-3] + "json"

            with open(os.path.join(json_category_path, json_name), "w") as json_file:
                json.dump(xml_to_dict, json_file, indent=2)


            
    def get_json_array(self, category_index):
        # Create JSON paths:
        json_path = os.path.join(self.preset_path, "JSON")
        json_category_path = os.path.join(json_path, self.categories[category_index])

        json_presets = os.listdir(json_category_path)

        rtn_data = []

        for preset in json_presets:
            with open(os.path.join(json_category_path, preset), "r") as json_file:
                data = json.load(json_file) 
            
            rtn_data.append(data)

        return rtn_data


    def check_for_new_presets(self): 
        """
        This functions role is to check the new presets folder,
        find the names for all the presets,
        then return a list of the preset namese to post
        """
        presets = os.listdir(self.new_preseet_path)
        new_preset_lst = [] # The list to store the new presets.

        for preset in presets:
            new_preset_lst.append({ 'name': preset[:-4], 'dynamics': 0, 'brightness': 0, 'consistency': 0, 'evolution': 0})

        return new_preset_lst

        
class Preset:
    def __init__ (self, name, adv_path, category):
        self.name = name
        self.adv_path = adv_path
        self.category = category



    def get_name(self):
        return self.name



    def get_adv_path(self):
        return self.adv_path



    def get_category(self):
        return self.category

class PresetV2:
    def __init__ (self, name, values):
        self.name = name
        self.volume = values[0]

        """
        Signal Chain 01
        """
        self.OscToggle01 = values[1]
        self.OscWaveshape01 = values[2]
        self.OscOsctave01 = values[3]
        self.OscSemi01 = values[4]
        self.OscEnvT01 = values[5]

        """
        Signal Chain 02
        """
        self.OscToggle02 = values[6]
        self.OscWaveshape02 = values[7]
        self.OscOsctave02 = values[8]
        self.OscSemi02 = values[9]
        self.OscEnvT02 = values[10]

    def format_to_json(self):
        return {
            'name': self.name,
            'volume': self.volume,
            'OscToggle01': self.OscToggle01,
            'OscWaveshape01': self.OscWaveshape01,
            'OscOctave01': self.OscOsctave01,
            'OscSemi01': self.OscSemi01,
            'OsvEnvT01': self.OscEnvT01,
            'OscToggle02': self.OscToggle02,
            'OscWaveshape02': self.OscWaveshape02,
            'OscOctave02': self.OscOsctave02,
            'OscSemi02': self.OscSemi02,
            'OscEnvT02': self.OscEnvT02
        }