import wx
import wx.grid as gridlib
import MySQLdb
import datetime

colNameDict={}
colNameDict["CategorieAmmortamenti"]=['Codice', 'Descrizione', 'Aliquota', 'Tipo']
#colNameDict["CategorieAmmortamenti"]=['ID', 'Codice', 'Descrizione', 'Aliquota', 'Tipo']
colNameDict["BeniAmmortizzabili"]=['ID', 'CodiceCategoria', 'Categoria', 'Descrizione', 'Tipo', 'DataDocumento', 'NumeroDocumento', 'Percentuale']

colLabDict={}
colLabDict["CategorieAmmortamenti"]=['Codice Cat', 'Descrizione Categoria', 'Aliquota Ammortamento', 'Tipo']
#colLabDict["CategorieAmmortamenti"]=['ID', 'Codice Cat', 'Descrizione Categoria', 'Aliquota Ammortamento', 'Tipo']
colLabDict["BeniAmmortizzabili"]=['ID', 'CodiceCategoria', 'Categoria', 'Descrizione', 'Tipo', 'DataDocumento', 'NumeroDocumento', 'Percentuale']
            
DTypesDict={}
DTypesDict["CategorieAmmortamenti"]=[gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT + ':3,2', gridlib.GRID_VALUE_STRING]
#DTypesDict["CategorieAmmortamenti"]=[gridlib.GRID_VALUE_LONG, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT + ':3,2', gridlib.GRID_VALUE_STRING]
DTypesDict["BeniAmmortizzabili"]=[gridlib.GRID_VALUE_LONG, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_STRING,  gridlib.GRID_VALUE_DATETIME,  gridlib.GRID_VALUE_STRING, gridlib.GRID_VALUE_FLOAT + ':3,2']

try:
    conn = MySQLdb.connect (host = "gpstrading.it", user = "Protrader", passwd = "3zyxelhub3", db = "Gestionale")
except MySQLdb.Error, e:
    print "Error in connection %d: %s" % (e.args[0], e.args[1])
            
class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self, tbName, log):
        gridlib.PyGridTableBase.__init__(self)
        self.log = log

        self.colLabels = colLabDict[tbName]
        self.dataTypes = DTypesDict[tbName]

        #try:        
        cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute ("SELECT * FROM " + tbName)
        result_set = cursor.fetchall ()
        lista=[]  
        for row in result_set:
            l=[]
            for a in colNameDict[tbName]:
                l += [row[a]]
            print l
            lista += [l]
        print "-----------------------------------"        
        print lista
            
        print "Records: " + str(cursor.rowcount)        
        self.data = lista
        cursor.close ()
            
        #except MySQLdb.Error, e:
            #print "Error in connection %d: %s" % (e.args[0], e.args[1])
            #sys.exit (1)

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data) + 1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

#---------------------------------------------------------------------------

class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        
        gridlib.Grid.__init__(self, parent, -1)

        #table = CustomDataTable(log)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        #self.SetTable(table, True)

        #self.SetRowLabelSize(0)
        #self.SetMargins(0,0)
        #self.AutoSizeColumns(False)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)


    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()


#---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):

        sampleList = ['CategorieAmmortamenti', 'BeniAmmortizzabili']        
        
        wx.Frame.__init__(self, parent, -1, "Form Ammortamenti", size=(1000,800))

        p = wx.Panel(self, -1, style=0)
        self.grid = CustTableGrid(p, log)
        
        b = wx.Button(p, -1, "Carica Tabella",(-1, -1),(100,22))
        b.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)
        b.Bind(wx.EVT_SET_FOCUS, self.OnButtonFocus)

        lbl = wx.StaticText(p, -1, "Seleziona una tabella:", (15, 50), (120, -1))
        self.ch = wx.Choice(p, -1, (100, 50), choices = sampleList)
        self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.ch)

        bshg = wx.BoxSizer(wx.HORIZONTAL)
        bsv = wx.BoxSizer(wx.VERTICAL)
        bsh = wx.BoxSizer(wx.HORIZONTAL)
        
        bshg.Add((10,720), 0)
        bshg.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        #bshg.Add(self.grid, 1, wx.EXPAND, 5)
        #bshg.Add((20,700), 1)        
        
        bsh.Add((20,20), 1)
        bsh.Add(b, 0, 0, 5)
        bsh.Add((5,20), 1)
        bsh.Add(lbl, 0, 0, 5)
        bsh.Add(self.ch, 0, 0, 5)
        bsv.Add(bshg, 0, 0, 5)
        bsv.Add((15,15), 1)
        bsv.Add(bsh, 0, 0, 5)
        bsv.Add((15,15), 0)
        
        p.SetSizer(bsv)
        p.Refresh
        
        
        
    def EvtChoice(self, event):
        print('EvtChoice: %s\n' % event.GetString())
        #self.ch.Append("A new item")
        
        #if event.GetString() == 'one':
            #self.log.WriteText('Well done!\n')


    def OnButton(self, evt):
        print "button selected"
        t0 = datetime.datetime.now()
        table = CustomDataTable("CategorieAmmortamenti",sys.stdout)
        t1 = datetime.datetime.now()
        self.grid.SetTable(table, True)
        self.grid.SetRowLabelSize(0)
        self.grid.SetMargins(0,0)
        self.grid.AutoSizeColumns(False)
        t2 = datetime.datetime.now()
        print "Tempo x lettura table " + str(t1-t0)
        print "Tempo x creazione grid " + str(t2-t1)
        #self.p.Refresh
        self.Refresh
    def OnButtonFocus(self, evt):
        print "button focus"
        
#---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()
