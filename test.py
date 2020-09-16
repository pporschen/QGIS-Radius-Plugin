# -*- coding: utf-8 -*-
"""
/***************************************************************************
 test
                                 A QGIS plugin
 test
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-09-13
        git sha              : $Format:%H$
        copyright            : (C) 2019 by test
        email                : test@test.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QFont, QColor
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt import QtGui
from qgis.core import *
import qgis.utils, sys, os, json, requests, math, shapely, sqlite3, csv, os.path

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .test_dialog import testDialog
from shapely.geometry import Polygon
from shapely.wkt import dumps, loads


class hallo:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'test_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&test')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('test', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/test/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'test'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&test'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = testDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        address = self.dlg.lineEdit.text()
        radius = self.dlg.lineEdit_2.text() #Radius anpassen

        if result and address and radius:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            radius = float(self.dlg.lineEdit_2.text())
            dbpath = os.path.join(os.path.dirname(__file__),"PLZ1.db")#Speicherort der Datenbank Datei
            csvpath = open(os.path.join(os.path.dirname(__file__),"search_results.csv"),"w")#Speicherort und Namen des Outputs angeben
            qgis_csv = "file:///"+os.path.join(os.path.dirname(__file__),"search_results.csv")+"?type=csv&detectTypes=yes&wktField=wkt&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no"
           
            def geocode(address):
            
                url = 'https://nominatim.openstreetmap.org/search?format=json&q=%s' % (address)
                results = json.loads(requests.get(url).text)
                lat, lon = results[0]["lat"], results[0]["lon"]

                return float(lat), float(lon)
                
            def boundaries_lookup(lat,lon,radius):

                searchfactor = 5

                lat1 = lat + 0.008983204953 * radius * searchfactor
                lat2 = lat - 0.008983204953 * radius * searchfactor
                lon1 = lon + 0.008983204953 * radius * 1/math.cos(lat * math.pi / 180) * searchfactor
                lon2 = lon - 0.008983204953 * radius * 1/math.cos(lat * math.pi / 180) * searchfactor
                
                return lat1,lat2,lon1,lon2

            def radius_wkt(lat,lon,radius):
                
                normal_polygon = [[0,0.008983204953],[0.0006266367004,0.008961322318],[0.00125022049,0.00889578102],[0.001867713331,0.008786900372],[0.00247610686,0.008635210828],[0.003072437046,0.008441451406],[0.003653798627,0.00820656608],[0.004217359268,0.00793169919],[0.004760373359,0.007618189858],[0.00528019539,0.007267565471],[0.005774292839,0.006881534236],[0.006240258514,0.006461976858],[0.006675822277,0.006010937378],[0.007078862105,0.005530613215],[0.007447414428,0.00502334446],[0.007779683697,0.004491602477],[0.008074051129,0.003937977857],[0.008329082595,0.003365167806],[0.008543535608,0.002775962995],[0.008716365375,0.002173233971],[0.008846729885,0.00155991717],[0.008933994017,0.000939000609],[0.008977732628,0.0003135093317],[0.008977732628,-0.0003135093317],[0.008933994017,-0.000939000609],[0.008846729885,-0.00155991717],[0.008716365375,-0.002173233971],[0.008543535608,-0.002775962995],[0.008329082595,-0.003365167806],[0.008074051129,-0.003937977857],[0.007779683697,-0.004491602477],[0.007447414428,-0.00502334446],[0.007078862105,-0.005530613215],[0.006675822277,-0.006010937377],[0.006240258514,-0.006461976858],[0.005774292839,-0.006881534236],[0.00528019539,-0.007267565471],[0.004760373359,-0.007618189858],[0.004217359268,-0.00793169919],[0.003653798627,-0.00820656608],[0.003072437046,-0.008441451406],[0.00247610686,-0.008635210828],[0.001867713331,-0.008786900372],[0.00125022049,-0.00889578102],[0.0006266367004,-0.008961322318],[0.00E+00,-0.008983204953],[-0.0006266367004,-0.008961322318],[-0.00125022049,-0.00889578102],[-0.001867713331,-0.008786900372],[-0.00247610686,-0.008635210828],[-0.003072437046,-0.008441451406],[-0.003653798627,-0.00820656608],[-0.004217359268,-0.00793169919],[-0.004760373359,-0.007618189858],[-0.00528019539,-0.007267565471],[-0.005774292839,-0.006881534236],[-0.006240258514,-0.006461976858],[-0.006675822277,-0.006010937377],[-0.007078862105,-0.005530613215],[-0.007447414428,-0.00502334446],[-0.007779683697,-0.004491602477],[-0.008074051129,-0.003937977857],[-0.008329082595,-0.003365167806],[-0.008543535608,-0.002775962995],[-0.008716365375,-0.002173233971],[-0.008846729885,-0.00155991717],[-0.008933994017,-0.000939000609],[-0.008977732628,-0.0003135093317],[-0.008977732628,0.0003135093317],[-0.008933994017,0.000939000609],[-0.008846729885,0.00155991717],[-0.008716365375,0.002173233971],[-0.008543535608,0.002775962995],[-0.008329082595,0.003365167806],[-0.008074051129,0.003937977857],[-0.007779683697,0.004491602477],[-0.007447414428,0.00502334446],[-0.007078862105,0.005530613215],[-0.006675822277,0.006010937378],[-0.006240258514,0.006461976858],[-0.005774292839,0.006881534236],[-0.00528019539,0.007267565471],[-0.004760373359,0.007618189858],[-0.004217359268,0.00793169919],[-0.003653798627,0.00820656608],[-0.003072437046,0.008441451406],[-0.00247610686,0.008635210828],[-0.001867713331,0.008786900372],[-0.00125022049,0.00889578102],[-0.0006266367004,0.008961322318],[0,0.008983204953]]
                new_polygon = [(lon + x[1] * radius * 1/math.cos(lat * math.pi / 180), lat + x[0] * radius) for x in normal_polygon]
                wkt = Polygon(new_polygon).wkt
                
                return loads(wkt)

            def db_lookup(lat1,lat2,lon1,lon2):
                
                con = sqlite3.connect(dbpath)
                cur = con.cursor()
                sql = "SELECT * FROM PLZDE WHERE ? > lat_centroid AND lat_centroid > ? AND ? > lon_centroid AND lon_centroid > ?"
                cur.execute(sql, (lat1,lat2,lon1,lon2))
                
                return cur.fetchall()
                
                con.commit()
                con.close()
                           
            coordinates = geocode(address)
            boundaries = boundaries_lookup(*coordinates,radius)

            radius_polygon = radius_wkt(*coordinates,radius)
            plz = db_lookup(*boundaries)
            x1,x2,y1,y2 = boundaries
           
            csv_list = [["type","postcode","name","overlap","wkt"],["radius","","radius","100.0",radius_polygon]]

            for i in plz:  
                postcode = i[0]
                postcode_name = i[1] 
                postcode_polygon = loads(i[2])
                if postcode_polygon.intersects(radius_polygon):
                    overlap = postcode_polygon.intersection(radius_polygon).area/postcode_polygon.area 
                    #print(f"{overlap:<10.1%}{postcode:10}{postcode_name:<15}")
                    csv_list.append(["area",postcode,postcode_name,round(overlap*100,1),i[2]])

            with csvpath:
                writer=csv.writer(csvpath)
                writer.writerows(csv_list)


            layer = QgsVectorLayer(qgis_csv, address+", Radius: "+ str(radius), "delimitedtext")
            renderer = layer.renderer()

            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(QtGui.QColor('#57ad6b'))
            symbol.setOpacity(0.45)
            symbol.symbolLayer(0).setStrokeColor(QtGui.QColor('#888'))
            renderer.setSymbol(symbol)
            
            layer_settings  = QgsPalLayerSettings()

            text_format = QgsTextFormat()
            text_format.setFont(QFont("Arial", 4))
            text_format.setSize(6)

            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)
            buffer_settings.setSize(0.3)
            buffer_settings.setColor(QColor("white"))

            text_format.setBuffer(buffer_settings)
            layer_settings.setFormat(text_format)

            layer_settings.fieldName = "postcode"
            layer_settings.placement = 1
            layer_settings.enabled = True
            layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)

            layer.setLabelsEnabled(True)
            layer.setLabeling(layer_settings)


            QgsProject.instance().addMapLayer(layer)
            qgis.utils.iface.mapCanvas().setExtent(QgsRectangle(y2, x2, y1, x1))
            self.dlg.lineEdit.clear()
            self.dlg.lineEdit_2.clear()
           