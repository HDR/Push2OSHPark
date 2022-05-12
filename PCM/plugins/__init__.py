import pcbnew
import sys
import os
import time
import requests
import shutil
import webbrowser

class Push2OSHParkPlugin(pcbnew.ActionPlugin):

    def __init__(self):
        super().__init__()
        self.name = "Push2OSHPark"
        self.category = "A descriptive category name"
        self.description = "Single click OSHPark Uploader"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def defaults(self):
        pass

    def Run(self):
        #Generate Gerbers
        kicad_board = pcbnew.GetBoard()
        kicad_file = kicad_board.GetFileName()
        board_name = kicad_file.split("/")[-1].replace(".kicad_pcb", "")
        
        
        plot = pcbnew.PLOT_CONTROLLER(kicad_board)
        plot_options = plot.GetPlotOptions()
        plot_options.SetOutputDirectory("Push2OSHPark")
        eLayers = kicad_board.GetEnabledLayers()
        layerid = list(eLayers.Seq())
        
        layer_names = []
        for layer_id in layerid:
            layer_names.append(kicad_board.GetLayerName(layer_id))
        maxlen = max(layer_names, key=len)
        
        
        #Plot Layers
        for i, layer_id in enumerate(layerid):
            plot.SetLayer(layer_id)
            layer_name = kicad_board.GetLayerName(layer_id).replace(".", "_")
            plot_sufix = str(layer_id).zfill(2) + "-" + layer_name
            plot.OpenPlotfile(plot_sufix, pcbnew.PLOT_FORMAT_GERBER, layer_name)
            plot.PlotLayer()
            
        #Generate Drill & Map Files
        drill = pcbnew.EXCELLON_WRITER(kicad_board)
        drill.SetMapFileFormat(pcbnew.PLOT_FORMAT_GERBER)
        drill.SetOptions(False, False, pcbnew.wxPoint(0, 0), False)
        drill.SetFormat(True, pcbnew.EXCELLON_WRITER.DECIMAL_FORMAT, 3, 3)
        drill.CreateDrillandMapFilesSet(plot.GetPlotDirName(), True, False );
        
        
        #ZIP Gerbers
        getPath = kicad_file.replace(kicad_file.split("/")[-1], "")
        shutil.make_archive(getPath + board_name, 'zip', getPath + 'Push2OSHPark/')
        zipFile = getPath + board_name + '.zip'
        
        #Send HTTP Post
        files = [('file', (zipFile, open(zipFile, 'rb'), 'application/zip'))]
        response = requests.request("POST", "https://oshpark.com/import", files=files)
        webbrowser.get().open('https://oshpark.com/uploads/' + response.text)
        response.close()



Push2OSHParkPlugin().register()