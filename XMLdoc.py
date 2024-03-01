import datetime
import xml.dom.minidom
from xml.dom import minidom
from chardet.universaldetector import UniversalDetector
import xml.etree.ElementTree as ET
import io
import os
class XMLdoc:
    def __init__(self,  Xml_file, new_file, OrgStatus, EgrulIsNotIncluded):
        # self.Xml_doc=_Xml_doc
        self.Xml_file=Xml_file
        self.new_file = new_file
        self.OrgStatus = OrgStatus
        self.EgrulIsNotIncluded = EgrulIsNotIncluded

    @staticmethod
    def open_file(file, encoding ="utf-8"):
        array = []
        with io.open(file,"r",encoding=encoding) as fr:
            array = fr.readlines()
            fr.close()
        return array

    @staticmethod
    def write_file(array,file,encoding="utf-8"):
        with io.open(file, "w", encoding=encoding) as fw:
            fw.writelines(array)
            fw.close()

    def backup_file(self,old,new,encoding="utf-8"):
        arr = self.open_file(old, encoding)
        self.write_file(arr,new,encoding)

    def convert_encoding(self,old_encoding, new_encoding):
        arr = self.open_file(self.Xml_file, old_encoding)
        self.write_file(arr,self.Xml_file,new_encoding)

    def check_encoding(self):
        detector = UniversalDetector()
        with open(self.Xml_file, 'rb') as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
        return detector.result

    def set_Xml_file(self, Xml_file):
        self.Xml_file=Xml_file

    def restore_subs(self,arr,main_arr):
        for elem in main_arr[i]:
            if len(elem):
                ET.SubElement()

    def rec_remove(self,element,parent):
        if parent.find(element.tag) == None:
            for i in range(len(parent)):
                if len(parent[i]): # если что-то вложено ещё
                    a=parent[i]
                    self.rec_remove(element,parent[i])
        else:
            #
            #try:
            elem=parent.find(element.tag)
            l = list(parent)
            parent.remove(elem)
            #except (ValueError):
            #    pass
        # result=[]
        # src_arr = arr
        # for i in range(len(arr)):
        #     if len(arr[i]):
        #         #d = list(arr[i].iter())
        #         for sub in arr[i]:
        #             arr[i].remove(sub)
        # full = self.restore_subs(arr[i],arr)
        # self.restore_subs(arr[i], arr)
        # b = arr[i]
        # a = ET.tostring(arr[i], encoding='utf-8').decode("utf-8")
        # result.append(a)

        #return ''.join(result)

    #преобразуем xml в ET и назначим рабочее пространство в row
    @staticmethod
    def parse_xml(file,encoding="utf-8"):
        parser = ET.XMLParser(encoding=encoding)
        doc = ET.parse(file, parser)
        return doc

    def del_elem(self,elem, parent):
        element= parent.iter(elem)
        if parent.find(elem.tag) != None:
            parent.remove(elem)
        else:
            for child in parent:
                res = list(child.iterfind(elem.tag))
                if res != []:
                    self.del_elem(elem,child)

    def status_change(self,element, status):
        if element.tag == "RecordNum":
            element.text = element.text[:-1] + status
        elif element.tag == "OrgStatus":
            element.text = status
    def Egrul_status_change(self, element, bools):
        if element.tag == "EgrulIsNotIncluded":
            element.text = bools
    # Status изменим


    def remove_header(self,encoding="utf-8"):
        doc = self.parse_xml(self.Xml_file)
        root = doc.getroot()
        for child in root.iter():
            row = child.find('row')
            if row != None:
                break;
        #rows = root.iterfind('row')
        print(row.attrib)
        newdoc = ET.ElementTree(row)
        root =newdoc.getroot()
        newdoc.write(self.Xml_file,encoding=encoding)

    #Другие названния нужны для отладки. Похже сменю на основные
    def edit_xml(self,encoding="utf-8"):
        doc = self.parse_xml(self.Xml_file)
        root = doc.getroot()
        root.set("xmlns","")
        for child in enumerate(root.iter()):
            # Обязательная настройка
            if child[1].tag == "StartDateActive" and root.find("NoInternet")==None:
                new=ET.Element("NoInternet", {})
                new.text="false"
                root.insert(child[0], new )
            elif child[1].tag == "IsObosob" and child[1].text == "1":
                print("проверьте, что правильный статус указан у головной организации")
            # elif 'OgrDos' in child[1].tag:
            #     self.rec_remove(child[1], root)
            self.Egrul_status_change(child[1], self.EgrulIsNotIncluded)
            self.status_change(child[1], self.OrgStatus)
        doc.write(self.Xml_file, encoding=encoding)

    #Разбивка идёт по закрывающему тэгу
    def set_header(self,template, encoding="utf-8", INC="", environment="PROD", splitter = "</REF_UBPandNUBP>"):
        arr_src = self.open_file(file=self.Xml_file)
        arr_template = self.open_file(file=template)
        for item in enumerate(arr_template):
            if splitter in item[1]:
                result=arr_template[:item[0]]+arr_src+arr_template[item[0]:]
                try:
                    os.mkdir(self.new_file)
                except (FileExistsError):
                    print('Folder already exists, skipping')
                file_path=self.new_file + '\\' + self.new_file + '.xml'
                self.write_file(result, file_path)
                return file_path
                #header=arr_template[item[0]:]
                #close_header=arr[:item[0]]
        return "Неправильно задана разбивка, обратитесь к автору этой какахи"