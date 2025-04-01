#Author: NSA Cloud
import json
import os
import re
import bpy

from .gen_functions import textColors,raiseWarning
from .blender_utils import showErrorMessageBox
#from .blender_re_chain import findHeaderObj

def findHeaderObj():
	if bpy.data.collections.get("chainData",None) != None:
		objList = bpy.data.collections["chainData"].all_objects
		headerList = [obj for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		if len(headerList) >= 1:
			return headerList[0]
		else:
			return None
PRESET_VERSION = 6#To be changed when there are changes to chain object variables
skipKeys = set(["subDataList_items"])
def saveAsPreset(selection,presetName):
	if len(selection) > 0:
		# activeObj = selection[0]
		selection = bpy.context.selected_objects
		if not re.search(r'^[\w,\s-]+\.[A-Za-z]{3}$',
						 presetName) and not ".." in presetName:  # Check that the preset name contains no invalid characters for a file name
			presetDictTotal = {}
			presetDict1 = {}
			presetDict2 = {}
			presetDict3 = {}
			folderPath = "ChainPresets"
			variableList = []

			for obj in bpy.context.selected_objects:
				chainObjType = obj.get("TYPE",None)

				# presetDict["presetVersion"] = PRESET_VERSION
				# if chainObjType == "RE_CHAIN_WINDSETTINGS":
				# 	folderPath = "WindSettings"
				# 	presetDict["presetType"] = "RE_CHAIN_WINDSETTINGS"
				# 	variableList = obj.re_chain_windsettings.items()

				if chainObjType == "RE_CHAIN_CHAINSETTINGS":
					# folderPath = "ChainSettings"
					# presetDict["presetType"] = "RE_CHAIN_CHAINSETTINGS"
					variableList = obj.re_chain_chainsettings.items()
					presetDict1["subDataValues"] = []#Manual subdata support
					for item in obj.re_chain_chainsettings.subDataList_items:
						presetDict1["subDataValues"].append([v for v in item.values])

					if variableList != []:
						for key, value in variableList:
							if key not in skipKeys:
								if type(value).__name__ == "IDPropertyArray":
									presetDict1[key] = value.to_list()
								else:
									presetDict1[key] = value
					presetDictTotal["RE_CHAIN_CHAINSETTINGS"] = presetDict1


				elif chainObjType == "RE_CHAIN_CHAINGROUP":
					# folderPath = "ChainGroup"
					# presetDict["presetType"] = "RE_CHAIN_CHAINGROUP"
					variableList = obj.re_chain_chaingroup.items()

					if variableList != []:
						for key, value in variableList:
							if key not in skipKeys:
								if type(value).__name__ == "IDPropertyArray":
									presetDict2[key] = value.to_list()
								else:
									presetDict2[key] = value
					presetDictTotal["RE_CHAIN_CHAINGROUP"] = presetDict2

					if obj.children:
						obj = obj.children[0]
						if obj.get("TYPE",None)  == "RE_CHAIN_NODE":
							variableList = obj.re_chain_chainnode.items()

							if variableList != []:
								for key, value in variableList:
									if key not in skipKeys:
										if type(value).__name__ == "IDPropertyArray":
											presetDict3[key] = value.to_list()
										else:
											presetDict3[key] = value
							presetDictTotal["RE_CHAIN_NODE"] = presetDict3


				# elif chainObjType == "RE_CHAIN_NODE":
				# 	# folderPath = "ChainNode"
				# 	# presetDict["presetType"] = "RE_CHAIN_NODE"
				# 	variableList = obj.re_chain_chainnode.items()
				#
				# 	if variableList != []:
				# 		for key, value in variableList:
				# 			if key not in skipKeys:
				# 				if type(value).__name__ == "IDPropertyArray":
				# 					presetDict3[key] = value.to_list()
				# 				else:
				# 					presetDict3[key] = value
				# 	presetDictTotal["RE_CHAIN_NODE"] = presetDict3


				# else:
				# 	showErrorMessageBox("Selected object can not be made into a preset.")
			
			# if variableList != []:
			# 	for key, value in variableList:
			# 		if key not in skipKeys:
			# 			if type(value).__name__ == "IDPropertyArray":
			# 				presetDict[key] = value.to_list()
			# 			else:
			# 				presetDict[key] = value
				
				# #Find chain header in scene and get the version
				# chainHeader = findHeaderObj()
				# if chainHeader != None:
				# 	presetDict["chainVersion"] = chainHeader.re_chain_header.version
				# presetDict["presetVersion"] = PRESET_VERSION
			jsonPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets",folderPath,presetName+".json")
			#print(presetDict)#debug
			try:
				os.makedirs(os.path.split(jsonPath)[0])
			except:
				pass
			with open(jsonPath, 'w', encoding='utf-8') as f:
				json.dump(presetDictTotal, f, ensure_ascii=False, indent=4)
				print(textColors.OKGREEN+"Saved preset to " + str(jsonPath) + textColors.ENDC)
				return True
		else:
			showErrorMessageBox("Invalid preset file name. ")
	else:
		showErrorMessageBox("At least one chain object must be selected when saving a preset.")
		

def readPresetJSON(filepath,activeObj):
		try:
			with open(filepath) as jsonFile:
				jsonDict = json.load(jsonFile)
				# if jsonDict["presetVersion"] > PRESET_VERSION:
				# 	showErrorMessageBox("Preset was created in a newer version and cannot be used. Update to the latest version of the chain importer.")
				# 	return False
				
		except Exception as err:
			showErrorMessageBox("Failed to read json file. \n" + str(err))
			return False
		
		# if jsonDict["presetType"] != activeObj.get("TYPE",None):
		# 	showErrorMessageBox("Preset type does not match selected object")
		# 	return False
		propertyGroup = {}
		# if jsonDict["presetType"] == "RE_CHAIN_WINDSETTINGS":
		# 	propertyGroup = activeObj.re_chain_windsettings

		for obj in activeObj:
				
			if obj.get("TYPE", None) == "RE_CHAIN_CHAINSETTINGS":

				propertyGroup = obj.re_chain_chainsettings
				if "subDataValues" in jsonDict["RE_CHAIN_CHAINSETTINGS"]:
					obj.re_chain_chainsettings.subDataList_items.clear()
					for entry in jsonDict["RE_CHAIN_CHAINSETTINGS"]["subDataValues"]:
						item = obj.re_chain_chainsettings.subDataList_items.add()
						for index, val in enumerate(entry[:len(item.values)]):
							if isinstance(val, int):
								item.values[index] = val

				print("Applying preset to " + obj.name)

				for key in propertyGroup.keys():
					if key not in skipKeys:
						try:
							propertyGroup[key] = jsonDict["RE_CHAIN_CHAINSETTINGS"][key]
						except:
							raiseWarning(
								"Preset is missing key " + str(key) + ", cannot set value on chain settings object.")

			elif obj.get("TYPE", None) == "RE_CHAIN_CHAINGROUP":

				propertyGroup = obj.re_chain_chaingroup
				print("Applying preset to " + obj.name)

				for key in propertyGroup.keys():
					if key not in skipKeys:
						try:
							propertyGroup[key] = jsonDict["RE_CHAIN_CHAINGROUP"][key]
						except:
							raiseWarning(
								"Preset is missing key " + str(key) + ", cannot set value on chain group object.")

			elif obj.get("TYPE", None) == "RE_CHAIN_NODE":
				# currentNode = obj
				# nodeObjList = [currentNode]
				# if bpy.context.scene.re_chain_toolpanel.applyPresetToChildNodes:
				# 	while len(currentNode.children) > 1:
				# 		for child in currentNode.children:
				# 			if child.get("TYPE",None) == "RE_CHAIN_NODE":
				# 				nodeObjList.append(child)
				# 				currentNode = child

				# for nodeObj in nodeObjList:

				propertyGroup = obj.re_chain_chainnode
				print("Applying preset to " + obj.name)

				for key in propertyGroup.keys():
					if key not in skipKeys:
						try:
							propertyGroup[key] = jsonDict["RE_CHAIN_NODE"][key]
						except:
							raiseWarning(
								"Preset is missing key " + str(key) + ", cannot set value on chain nodes object.")

			# elif jsonDict["presetType"] == "RE_CHAIN_CHAINGROUP":
			# 	propertyGroup = activeObj.re_chain_chaingroup
			#
			# elif jsonDict["presetType"] == "RE_CHAIN_NODE":
			# 	propertyGroup = activeObj.re_chain_chainnode
			# 	if jsonDict["presetVersion"] < 6:
			# 		#Fix keys changed in update
			# 		if "unknChainNodeValue0" in jsonDict:
			# 			jsonDict["gravityCoef"] = jsonDict["unknChainNodeValue0"]
			else:
				# showErrorMessageBox("Preset type is not supported")
				# return False
				continue


			# for key in propertyGroup.keys():
			# 	if key not in skipKeys:
			# 		try:
			# 			propertyGroup[key] = jsonDict[key]
			# 		except:
			# 			raiseWarning("Preset is missing key " + str(key) +", cannot set value on active object.")
		return True
def reloadPresets(folderPath):
	presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")
	global presetList #支持中文预设名
	presetList = []
	relPathStart = os.path.join(presetsPath,folderPath)
	if os.path.exists(relPathStart):
		for entry in os.scandir(relPathStart):
			if entry.name.endswith(".json") and entry.is_file():
				presetList.append((os.path.relpath(os.path.join(relPathStart,entry),start = presetsPath),os.path.splitext(entry.name)[0],""))
	#print("Loading " + folderPath + " presets...")
	#print("DEBUG:" + str(presetList)+"\n")#debug
	return presetList