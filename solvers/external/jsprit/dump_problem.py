import xml.etree.ElementTree as ET

from models.rich_vrp import Agent


def dump_problem():
    """
    Сохраняем xml для основной проблемы
    """
    data = ET.Element('problem')

    ...


def dump_vehicle(a: Agent, root: ET.Element):
    """
    Дампаем компонент машины
    """
    vehicle = ET.SubElement(root, 'vehicle')
    


items = ET.SubElement(data, 'items')
item1 = ET.SubElement(items, 'item')
item2 = ET.SubElement(items, 'item')
item1.set('name','item1')
item2.set('name','item2')
item1.text = 'item1abc'
item2.text = 'item2abc'

# create a new XML file with the results
mydata = ET.tostring(data)
myfile = open("items2.xml", "w")
myfile.write(mydata)
