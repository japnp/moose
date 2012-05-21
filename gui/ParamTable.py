#!/usr/bin/python
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from GenSyntax import *

try:
  _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  _fromUtf8 = lambda s: s


class ParamTable:
  def __init__(self, main_data, action_syntax, single_item, incoming_data, main_layout, parent_class, already_has_parent_params):
    self.main_data = main_data
    self.action_syntax = action_syntax

    if main_data and 'subblocks' in main_data:
      self.subblocks = main_data['subblocks']
    else:
      self.subblocks = None
      
    self.single_item = single_item
    self.original_table_data = {}
    self.incoming_data = incoming_data
    self.main_layout = main_layout
    self.parent_class = parent_class
    self.already_has_parent_params = already_has_parent_params
    self.initUI()

  def initUI(self):
#    self.layoutV = QtGui.QVBoxLayout(self.main_layout)
    self.layoutV = QtGui.QVBoxLayout()
    
    self.init_menu(self.layoutV)
    self.table_widget = QtGui.QTableWidget()
    self.layoutV.addWidget(self.table_widget)

    self.drop_menu.setCurrentIndex(-1)
    found_index = self.drop_menu.findText('*')

    if found_index == -1:
      found_index = self.drop_menu.findText('ParentParams')
      
    self.drop_menu.setCurrentIndex(found_index)

    # print self.incoming_data
    if self.incoming_data:
      if 'type' in self.incoming_data:
        self.drop_menu.setCurrentIndex(self.drop_menu.findText(self.incoming_data['type']))
      else:
        found_index = self.drop_menu.findText(self.incoming_data['Name'])
        if found_index != -1:
          self.drop_menu.setCurrentIndex(found_index)
              
      self.table_widget.cellChanged.connect(self.cellChanged)
      self.fillTableWithData(self.incoming_data)
      self.table_widget.cellChanged.disconnect(self.cellChanged)
    self.main_layout.addLayout(self.layoutV)

    apply_button = None
        # Build the Add and Cancel buttons
    if self.incoming_data and len(self.incoming_data):
      apply_button = QtGui.QPushButton("Apply")
    else:
      apply_button = QtGui.QPushButton("Add")

    new_row_button = QtGui.QPushButton("New Parameter")
    cancel_button = QtGui.QPushButton("Cancel")
    
    QtCore.QObject.connect(apply_button, QtCore.SIGNAL("clicked()"), self.click_add)
    QtCore.QObject.connect(new_row_button, QtCore.SIGNAL("clicked()"), self.click_new_row)
    QtCore.QObject.connect(cancel_button, QtCore.SIGNAL("clicked()"), self.click_cancel)
    
    button_layout = QtGui.QHBoxLayout()

    button_layout.addWidget(apply_button)
    button_layout.addWidget(new_row_button)
    button_layout.addWidget(cancel_button)
    
    self.layoutV.addLayout(button_layout)


  ### Takes a dictionary containing name value pairs
  def fillTableWithData(self, the_data):
#     for name,value in the_data.items():
#       for i in xrange(0,self.table_widget.rowCount()):
#         row_name = str(self.table_widget.item(i,0).text())

#         if row_name == name:
#           item = self.table_widget.item(i,1)
#           item.setText(str(value))
    used_params = []
    # First, loop through and add all data that corresponds to YAML
    for i in xrange(0,self.table_widget.rowCount()):
      row_name = str(self.table_widget.item(i,0).text())

      if row_name in the_data and row_name != 'type':
        item = self.table_widget.item(i,1)
        item.setText(str(the_data[row_name]))
        used_params.append(row_name)
    # Now look to see if we have more data that wasn't in YAML and add additional rows for that
    for name,value in the_data.items():
      if name not in used_params and name != 'type':
        self.table_widget.insertRow(self.table_widget.rowCount())
        name_item = QtGui.QTableWidgetItem(name)
        value_item = QtGui.QTableWidgetItem(value)
        self.table_widget.setItem(self.table_widget.rowCount()-1,0,name_item)
        self.table_widget.setItem(self.table_widget.rowCount()-1,1,value_item)


  def tableToDict(self, only_not_in_original = False):
    the_data = {}
    for i in xrange(0,self.table_widget.rowCount()):
      param_name = str(self.table_widget.item(i,0).text())
      param_value = str(self.table_widget.item(i,1).text())
      
      if not param_name in self.original_table_data or not self.original_table_data[param_name] == param_value: #If we changed it - definitely include it
          the_data[param_name] = param_value
      else:
        if not only_not_in_original: # If we want stuff other than what we changed
          if param_name == 'parent_params' or param_name == 'type':  #Pass through type and parent_params even if we didn't change them
             the_data[param_name] = param_value
#          else:
#            if param_name in self.param_is_required and self.param_is_required[param_name]: #Pass through any 'required' parameters
#              the_data[param_name] = param_value
    return the_data
    

  def init_menu(self, layout):
    self.drop_menu = QtGui.QComboBox()
    self.has_type = False
    if self.subblocks:
      for item in self.subblocks:
        name = item['name'].split('/').pop()
        if name == '<type>':  #If this is the "type" node then put all of it's subblocks into the menu
          if self.already_has_parent_params:
            continue
          self.has_type = True
          if item['subblocks'] and len(item['subblocks']):
            for sb in item['subblocks']:
              sb_name = sb['name'].split('/').pop()
              self.drop_menu.addItem(sb_name)
        else:
          if not self.action_syntax.isPath(item['name']):
            self.drop_menu.addItem(name)
    

    if not self.already_has_parent_params and self.main_data and self.main_data['parameters'] and len(self.main_data['parameters']) and ('subblocks' not in self.main_data or not self.main_data['subblocks'] or not self.has_type):
      self.drop_menu.addItem('ParentParams')
#    self.drop_menu.activated[str].connect(self.item_clicked)
    self.drop_menu.currentIndexChanged[str].connect(self.item_clicked)
    layout.addWidget(self.drop_menu)

  def click_add(self):
    self.table_data = self.tableToDict()
    self.parent_class.accept_params()
    return

  def click_new_row(self):
    self.table_widget.insertRow(self.table_widget.rowCount())

  def result(self):
    return self.table_data

  def click_cancel(self):
    self.parent_class.reject_params()

  def item_clicked(self, item):
    saved_data = {}
    # Save off the current contents to try to restore it after swapping out the params
    if self.original_table_data: #This will only have some length after the first time through
      saved_data = self.tableToDict(True) # Pass true so we only save off stuff the user has entered

    # Build the Table
    the_table_data = []

    # Save off thie original data from the dump so we can compare later
    self.original_table_data = {}
    self.param_is_required = {}

    the_table_data.append({'name':'Name','default':'','description':'Name you want to give to this object','required':True})

    # Whether or not we've found the right data for this item
    found_it = False
    
    has_parent_params_set = False

    if self.subblocks:
      for new_text in self.subblocks:
        if new_text['name'].split('/').pop() == item:
          found_it = True
          #the_table_data.append({'name':'type','default':new_text['name'].split('/').pop(),'description':'The object type','required':True})
          for param in new_text['parameters']:
            self.original_table_data[param['name']] = param['default']
            if param['name'] == 'type':
              param['default'] = new_text['name'].split('/').pop()
            the_table_data.append(param)
            self.param_is_required[param['name']] = param['required']
          break #- can't break here because there might be more


      if not found_it and not self.already_has_parent_params: # If we still haven't found it... look under "item"
        for data in self.subblocks:
          name = data['name'].split('/').pop()
          if name == '<type>':
            if data['subblocks'] and len(data['subblocks']):
              for sb in data['subblocks']:
                sb_name = sb['name'].split('/').pop()
                if sb_name == item:
                  found_it = True
                  has_parent_params_set = True
                  for param in sb['parameters']:
                    self.original_table_data[param['name']] = param['default']
                    the_table_data.append(param)
                    self.param_is_required[param['name']] = param['required']
          if found_it:
            break
    else:
      has_parent_params_set = True  #If there are no subblocks then these options are definitely going into the parent

    if item == 'ParentParams': # If they explicitly selected ParentParams then let's put them there
      has_parent_params_set = True

    if has_parent_params_set: # Need to add in the parent's params
      the_table_data.append({'name':'parent_params','default':'true','description':'These options will go into the parent','required':False})
      for param in self.main_data['parameters']:
        if param['name'] == 'type':
          continue
        self.original_table_data[param['name']] = param['default']
        the_table_data.append(param)
        self.param_is_required[param['name']] = param['required']

    total_rows = len(the_table_data)
    self.table_widget.setRowCount(total_rows)
    self.table_widget.setColumnCount(3)
    self.table_widget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem('Name'))
    self.table_widget.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem('Value'))
    self.table_widget.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem('Description'))
    self.table_widget.verticalHeader().setVisible(False)

    row = 0
    for param in the_table_data:
      # Populate table with data:
      name_item = QtGui.QTableWidgetItem(param['name'])

      value = ''
      
      if not param['required'] or param['name'] == 'type':
        value = param['default']

      if param['required']:
        color = QtGui.QColor()
#        color.setNamedColor("red")
        color.setRgb(255,204,153)
        name_item.setBackgroundColor(color)

      if has_parent_params_set and param['name'] == 'Name':
        value = 'ParentParams'
        
      value_item = QtGui.QTableWidgetItem(value)

      doc_item = QtGui.QTableWidgetItem(param['description'])
      
      name_item.setFlags(QtCore.Qt.ItemIsEnabled)
      doc_item.setFlags(QtCore.Qt.ItemIsEnabled)

      if param['name'] == 'type' or param['name'] == 'parent_params' or (has_parent_params_set and param['name'] == 'Name'):
        value_item.setFlags(QtCore.Qt.NoItemFlags)

      self.table_widget.setItem(row, 0, name_item)
      self.table_widget.setItem(row, 1, value_item)
      self.table_widget.setItem(row, 2, doc_item)
      row += 1

    self.table_widget.resizeColumnsToContents()

    # Try to restore saved data
    if len(saved_data):
      self.fillTableWithData(saved_data)
    
    self.table_widget.cellChanged.connect(self.cellChanged)
    
  def cellChanged(self, row, col):
    pass