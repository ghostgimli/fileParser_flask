# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import flask
from XMLdoc import XMLdoc

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        xml = XMLdoc('example.xml')
        xml.backup_file(xml.Xml_file,'backup.xml')
        #xml.convert_encoding(old_encoding="iso-8859-5",new_encoding="utf-8")
        if xml.check_encoding()['encoding'] != 'utf-8':
            xml.convert_encoding(old_encoding="iso-8859-5", new_encoding="utf-8")
        xml.remove_header()
        xml.edit_xml()
        xml.set_header("template.xml","utf-8")
        xml.backup_file('backup.xml', xml.Xml_file)
    except:
        xml.backup_file('backup.xml', xml.Xml_file)
        raise


    #    editXML('example.xml', "iso-8859-5")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
